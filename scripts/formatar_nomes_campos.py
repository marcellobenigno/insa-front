# -*- coding: utf-8 -*-
"""
normalizar_colunas_gpkg.py

Uniformiza os nomes das colunas (campos) de todas as camadas de um
GeoPackage, seguindo o mesmo padrão já aplicado aos nomes das camadas:
    - remove acentuação da língua portuguesa
    - converte para minúsculas
    - substitui espaços e caracteres especiais por underscore
    - remove underscores duplicados/nas bordas
    - prefixa com "col_" caso o resultado comece com dígito (identificador
      SQL não pode iniciar com número)

Cuidados especiais:
    - NÃO renomeia a coluna de geometria nem a coluna de FID (chave
      primária interna do GeoPackage) — alterar qualquer uma delas
      corrompe a estrutura do arquivo.
    - NÃO processa a própria tabela 'layer_styles' (tabela de controle
      do QGIS, cujas colunas são fixas pelo padrão do QGIS).
    - Trata o caso especial de rename "só-muda-a-caixa" (ex: 'IQM' ->
      'iqm'), usando um nome de coluna temporário intermediário, pois
      o SQLite/GDAL pode rejeitar (ou falhar silenciosamente) um rename
      direto quando origem e destino só diferem em maiúsculas/minúsculas.
    - Após renomear os campos de uma camada, atualiza automaticamente
      as referências a esses campos dentro do estilo salvo no próprio
      GeoPackage (tabela 'layer_styles', colunas styleQML/styleSLD),
      para que o renderer, rótulos, aliases, formulários e valores
      padrão continuem funcionando.

Uso:
    1. Abra o Console Python do QGIS (Plugins > Console Python).
    2. Ajuste a variável GPKG_PATH abaixo.
    3. Execute o script.

Requisitos:
    - QGIS 3.x (testado em 3.44.8-Solothurn).
"""

import re
import unicodedata
import uuid

from osgeo import ogr

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------

GPKG_PATH = "/Users/marcellodebarrosfilho/code/insa-front/data/insa3.gpkg"  # <-- ajuste aqui
DRY_RUN = False  # True = apenas mostra o que seria feito, sem alterar o arquivo

NOME_TABELA_ESTILOS = "layer_styles"  # tabela de controle de estilos do QGIS


# ---------------------------------------------------------------------------
# Funções de normalização de nomes
# ---------------------------------------------------------------------------

def remover_acentos(texto: str) -> str:
    """Remove acentos e diacríticos de uma string (ex: 'ç' -> 'c', 'ã' -> 'a')."""
    forma_normalizada = unicodedata.normalize("NFKD", texto)
    return "".join(
        caractere for caractere in forma_normalizada
        if not unicodedata.combining(caractere)
    )


def normalizar_nome_coluna(nome: str) -> str:
    """
    Converte o nome de uma coluna para um formato padronizado:
    minúsculo, sem acentos, sem espaços, apenas [a-z0-9_].
    Prefixa com 'col_' se o resultado começar com dígito, pois
    identificadores SQL não podem iniciar com número.
    """
    nome = remover_acentos(nome)
    nome = nome.lower()
    nome = re.sub(r"[^a-z0-9]+", "_", nome)
    nome = re.sub(r"_+", "_", nome).strip("_")

    if nome and nome[0].isdigit():
        nome = f"col_{nome}"

    return nome


def gerar_nome_unico(nome_base: str, nomes_em_uso_lower: set) -> str:
    """
    Garante que o nome gerado não colida com outra coluna já existente
    (ou já renomeada) na mesma tabela, de forma case-insensitive —
    regra do SQLite, que é a base do GeoPackage.
    """
    if nome_base.lower() not in nomes_em_uso_lower:
        return nome_base

    contador = 2
    novo_nome = f"{nome_base}_{contador}"
    while novo_nome.lower() in nomes_em_uso_lower:
        contador += 1
        novo_nome = f"{nome_base}_{contador}"
    return novo_nome


def eh_apenas_mudanca_de_caixa(nome_origem: str, nome_destino: str) -> bool:
    """
    Detecta o caso especial em que origem e destino são o mesmo nome de
    coluna do ponto de vista do SQLite (case-insensitive), mas diferem
    na grafia (maiúsculas/minúsculas). Esse caso exige um rename em dois
    passos, via nome temporário, para evitar rejeição/comportamento
    inconsistente do driver.
    """
    return (
        nome_origem != nome_destino
        and nome_origem.lower() == nome_destino.lower()
    )


# ---------------------------------------------------------------------------
# Renomeação de campos (colunas) de uma camada
# ---------------------------------------------------------------------------

def calcular_mapeamento_colunas(layer) -> dict:
    """
    Calcula o mapeamento {nome_antigo: nome_novo} para os campos
    "comuns" de uma camada (exclui geometria e FID), ignorando campos
    já normalizados e resolvendo colisões de nome.
    """
    layer_defn = layer.GetLayerDefn()
    coluna_fid = (layer.GetFIDColumn() or "fid").lower()

    nomes_em_uso_lower = {
        layer_defn.GetFieldDefn(i).GetName().lower()
        for i in range(layer_defn.GetFieldCount())
    }
    nomes_em_uso_lower.add(coluna_fid)

    mapeamento = {}
    for indice in range(layer_defn.GetFieldCount()):
        campo_defn = layer_defn.GetFieldDefn(indice)
        nome_original = campo_defn.GetName()

        if nome_original.lower() == coluna_fid:
            continue  # nunca renomeia a chave primária do GeoPackage

        nome_normalizado = normalizar_nome_coluna(nome_original)
        if nome_normalizado == nome_original:
            continue  # já está padronizado

        nomes_em_uso_lower.discard(nome_original.lower())
        nome_final = gerar_nome_unico(nome_normalizado, nomes_em_uso_lower)
        nomes_em_uso_lower.add(nome_final.lower())

        mapeamento[nome_original] = nome_final

    return mapeamento


def renomear_campo(layer, nome_origem: str, nome_final: str) -> None:
    """
    Executa o rename de um único campo via AlterFieldDefn, tratando
    automaticamente o caso especial de mudança apenas de caixa
    (ex: 'IQM' -> 'iqm') através de um nome temporário intermediário.
    """
    layer_defn = layer.GetLayerDefn()

    def _alterar_nome(nome_atual: str, novo_nome: str) -> None:
        indice = layer_defn.GetFieldIndex(nome_atual)
        if indice < 0:
            raise RuntimeError(
                f"Campo '{nome_atual}' não encontrado ao tentar renomear "
                f"para '{novo_nome}'."
            )
        campo_atual = layer_defn.GetFieldDefn(indice)

        novo_campo_defn = ogr.FieldDefn(novo_nome, campo_atual.GetType())
        novo_campo_defn.SetWidth(campo_atual.GetWidth())
        novo_campo_defn.SetPrecision(campo_atual.GetPrecision())

        resultado = layer.AlterFieldDefn(indice, novo_campo_defn, ogr.ALTER_NAME_FLAG)
        if resultado != ogr.OGRERR_NONE:
            raise RuntimeError(
                f"Falha ao renomear '{nome_atual}' para '{novo_nome}' "
                f"(código OGR: {resultado})"
            )

    if eh_apenas_mudanca_de_caixa(nome_origem, nome_final):
        nome_temporario = f"tmp_{uuid.uuid4().hex[:8]}"
        _alterar_nome(nome_origem, nome_temporario)
        _alterar_nome(nome_temporario, nome_final)
    else:
        _alterar_nome(nome_origem, nome_final)


def aplicar_renomeacao_colunas(layer, mapeamento: dict) -> None:
    """Aplica o rename de todos os campos mapeados para uma camada."""
    for nome_original, nome_final in mapeamento.items():
        try:
            renomear_campo(layer, nome_original, nome_final)
            observacao = (
                " (via nome temporário, mudança apenas de caixa)"
                if eh_apenas_mudanca_de_caixa(nome_original, nome_final)
                else ""
            )
            print(f"    [RENOMEADO] '{nome_original}' -> '{nome_final}'{observacao}")
        except RuntimeError as erro:
            print(f"    [ERRO]      {erro}")


# ---------------------------------------------------------------------------
# Atualização de estilos (layer_styles) para manter a renderização
# ---------------------------------------------------------------------------

def substituir_referencias_de_campo(texto_estilo: str, mapeamento: dict) -> str:
    """
    Substitui, dentro do XML de estilo (QML/SLD), as referências aos
    nomes antigos de campo pelos novos nomes.

    A substituição é restrita a ocorrências "delimitadas por aspas"
    (literais ' e " ou suas entidades XML &quot;/&apos;), que é como
    o QGIS sempre referencia nomes de campo em atributos XML e em
    expressões (ex: field="nome_antigo", "nome_antigo" || 'x').
    Isso evita substituições parciais indevidas em outros textos do
    estilo (rótulos de regra, nomes de camada, etc.).

    Processa os campos do mais longo para o mais curto, para evitar
    que um nome curto seja substituído dentro de um nome mais longo
    que o contenha como substring.
    """
    pares_ordenados = sorted(
        mapeamento.items(), key=lambda par: len(par[0]), reverse=True
    )

    delimitadores = ['"', "'", "&quot;", "&apos;"]

    for nome_original, nome_final in pares_ordenados:
        nome_escapado = re.escape(nome_original)
        for delimitador in delimitadores:
            padrao = re.compile(
                f"(?<={re.escape(delimitador)})"
                f"{nome_escapado}"
                f"(?={re.escape(delimitador)})"
            )
            texto_estilo = padrao.sub(nome_final, texto_estilo)

    return texto_estilo


def atualizar_estilos_da_camada(datasource, nome_tabela: str, mapeamento: dict,
                                 dry_run: bool) -> None:
    """
    Localiza entradas de estilo (tabela 'layer_styles') associadas à
    tabela informada e atualiza as referências de campo dentro do
    styleQML e styleSLD, preservando a renderização do mapa.
    """
    if not mapeamento:
        return

    if datasource.GetLayerByName(NOME_TABELA_ESTILOS) is None:
        return  # GeoPackage não possui estilos salvos no banco

    nome_tabela_sql = nome_tabela.replace("'", "''")
    consulta = (
        f"SELECT id, styleQML, styleSLD FROM {NOME_TABELA_ESTILOS} "
        f"WHERE f_table_name = '{nome_tabela_sql}'"
    )
    resultado_sql = datasource.ExecuteSQL(consulta)
    if resultado_sql is None:
        return

    linhas = [
        (feicao.GetFID(), feicao.GetField("styleQML"), feicao.GetField("styleSLD"))
        for feicao in resultado_sql
    ]
    datasource.ReleaseResultSet(resultado_sql)

    for id_estilo, style_qml, style_sld in linhas:
        novo_qml = substituir_referencias_de_campo(style_qml or "", mapeamento)
        novo_sld = substituir_referencias_de_campo(style_sld or "", mapeamento)

        if novo_qml == style_qml and novo_sld == style_sld:
            continue

        if dry_run:
            print(f"    [SIMULAÇÃO] Estilo id={id_estilo} seria atualizado "
                  f"para refletir os novos nomes de coluna.")
            continue

        qml_escapado = novo_qml.replace("'", "''")
        sld_escapado = novo_sld.replace("'", "''")
        atualizacao = (
            f"UPDATE {NOME_TABELA_ESTILOS} "
            f"SET styleQML = '{qml_escapado}', styleSLD = '{sld_escapado}' "
            f"WHERE id = {id_estilo}"
        )
        datasource.ExecuteSQL(atualizacao)
        print(f"    [ESTILO ATUALIZADO] id={id_estilo} "
              f"({len(mapeamento)} referência(s) de campo corrigida(s))")


# ---------------------------------------------------------------------------
# Função principal
# ---------------------------------------------------------------------------

def normalizar_colunas_gpkg(caminho_gpkg: str, dry_run: bool = False) -> None:
    """
    Percorre todas as camadas do GeoPackage e normaliza os nomes de
    coluna, mantendo os estilos salvos no banco sincronizados.
    """
    datasource = ogr.Open(caminho_gpkg, 1)  # 1 = modo de atualização
    if datasource is None:
        raise RuntimeError(f"Não foi possível abrir o GeoPackage: {caminho_gpkg}")

    total_camadas = datasource.GetLayerCount()
    print(f"GeoPackage: {caminho_gpkg}")
    print(f"Total de camadas encontradas: {total_camadas}\n")

    total_colunas_renomeadas = 0

    for indice_camada in range(total_camadas):
        layer = datasource.GetLayerByIndex(indice_camada)
        nome_tabela = layer.GetName()

        if nome_tabela == NOME_TABELA_ESTILOS:
            print(f"[IGNORADO]  '{nome_tabela}' (tabela de controle do QGIS)")
            continue

        mapeamento = calcular_mapeamento_colunas(layer)

        if not mapeamento:
            print(f"[OK]        '{nome_tabela}': colunas já padronizadas.")
            continue

        print(f"[CAMADA]    '{nome_tabela}': {len(mapeamento)} coluna(s) a renomear.")

        if dry_run:
            for nome_original, nome_final in mapeamento.items():
                observacao = (
                    " (via nome temporário, mudança apenas de caixa)"
                    if eh_apenas_mudanca_de_caixa(nome_original, nome_final)
                    else ""
                )
                print(f"    [SIMULAÇÃO] '{nome_original}' -> '{nome_final}'{observacao}")
        else:
            aplicar_renomeacao_colunas(layer, mapeamento)

        atualizar_estilos_da_camada(datasource, nome_tabela, mapeamento, dry_run)
        total_colunas_renomeadas += len(mapeamento)

    datasource = None  # fecha o datasource e persiste as alterações

    print(f"\nConcluído. {total_colunas_renomeadas} coluna(s) "
          f"{'seriam renomeadas' if dry_run else 'renomeadas'} no total.")


# ---------------------------------------------------------------------------
# Execução
# ---------------------------------------------------------------------------

if __name__ == "__console__" or __name__ == "__main__":
    normalizar_colunas_gpkg(GPKG_PATH, dry_run=DRY_RUN)