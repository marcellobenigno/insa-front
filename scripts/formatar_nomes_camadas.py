# -*- coding: utf-8 -*-

import re
import unicodedata
import uuid

from osgeo import ogr

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------

GPKG_PATH = "/Users/marcellodebarrosfilho/code/insa-front/data/insa2.gpkg"  # <-- ajuste aqui
DRY_RUN = False  # True = apenas mostra o que seria feito, sem alterar o arquivo


# ---------------------------------------------------------------------------
# Funções auxiliares
# ---------------------------------------------------------------------------

def remover_acentos(texto: str) -> str:
    """Remove acentos e diacríticos de uma string (ex: 'ç' -> 'c', 'ã' -> 'a')."""
    forma_normalizada = unicodedata.normalize("NFKD", texto)
    return "".join(
        caractere for caractere in forma_normalizada
        if not unicodedata.combining(caractere)
    )


def normalizar_nome_camada(nome: str) -> str:
    """
    Converte o nome de uma camada para um formato padronizado:
    minúsculo, sem acentos, sem espaços, apenas [a-z0-9_].
    """
    nome = remover_acentos(nome)
    nome = nome.lower()
    nome = re.sub(r"[^a-z0-9]+", "_", nome)
    nome = re.sub(r"_+", "_", nome).strip("_")
    return nome


def obter_nomes_tabelas_existentes(datasource) -> set:
    """
    Retorna, em minúsculas, o conjunto de TODOS os nomes de tabela
    atualmente presentes no arquivo SQLite/GeoPackage.

    Consulta diretamente o catálogo interno (sqlite_master) em vez de
    depender apenas das camadas expostas pelo OGR, pois o GeoPackage
    é case-insensitive para nomes de tabela e pode conter tabelas
    remanescentes que precisam ser consideradas para evitar colisões.
    """
    nomes = set()
    resultado_sql = datasource.ExecuteSQL(
        "SELECT name FROM sqlite_master WHERE type = 'table'"
    )
    if resultado_sql is not None:
        for feicao in resultado_sql:
            nomes.add(feicao.GetField(0).lower())
        datasource.ReleaseResultSet(resultado_sql)
    return nomes


def gerar_nome_unico(nome_base: str, nomes_em_uso_lower: set) -> str:
    """
    Garante que o nome gerado não colida com nenhum nome já existente,
    comparando de forma case-insensitive (regra do SQLite/GeoPackage).
    Adiciona sufixo numérico incremental em caso de conflito.
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
    tabela do ponto de vista do SQLite (case-insensitive), mas diferem
    na grafia (maiúsculas/minúsculas). Esse caso exige um rename em dois
    passos, via nome temporário, pois um rename direto é rejeitado por
    já haver uma tabela com esse nome (ela mesma).
    """
    return (
        nome_origem != nome_destino
        and nome_origem.lower() == nome_destino.lower()
    )


def renomear_camada(camada, nome_origem: str, nome_destino: str) -> None:
    """
    Executa o rename de uma camada, tratando automaticamente o caso
    especial de mudança apenas de caixa (ex: 'IQC' -> 'iqc') via um
    nome temporário intermediário.
    """
    if eh_apenas_mudanca_de_caixa(nome_origem, nome_destino):
        nome_temporario = f"__rename_tmp_{uuid.uuid4().hex[:8]}__"

        resultado = camada.Rename(nome_temporario)
        if resultado != ogr.OGRERR_NONE:
            raise RuntimeError(
                f"Falha ao mover '{nome_origem}' para nome temporário "
                f"'{nome_temporario}' (código OGR: {resultado})"
            )

        resultado = camada.Rename(nome_destino)
        if resultado != ogr.OGRERR_NONE:
            raise RuntimeError(
                f"Falha ao renomear de '{nome_temporario}' para "
                f"'{nome_destino}' (código OGR: {resultado})"
            )
    else:
        resultado = camada.Rename(nome_destino)
        if resultado != ogr.OGRERR_NONE:
            raise RuntimeError(
                f"Falha ao renomear '{nome_origem}' para '{nome_destino}' "
                f"(código OGR: {resultado})"
            )


# ---------------------------------------------------------------------------
# Função principal
# ---------------------------------------------------------------------------

def normalizar_camadas_gpkg(caminho_gpkg: str, dry_run: bool = False) -> None:
    """
    Percorre todas as camadas de um GeoPackage e renomeia apenas aquelas
    cujo nome normalizado difere do nome atual. Camadas já normalizadas
    permanecem intocadas. Colisões são resolvidas de forma case-insensitive,
    e o caso especial de rename "só-muda-a-caixa" é tratado via nome
    temporário intermediário.
    """
    datasource = ogr.Open(caminho_gpkg, 1)  # 1 = modo de atualização
    if datasource is None:
        raise RuntimeError(f"Não foi possível abrir o GeoPackage: {caminho_gpkg}")

    total_camadas = datasource.GetLayerCount()
    print(f"GeoPackage: {caminho_gpkg}")
    print(f"Total de camadas encontradas: {total_camadas}\n")

    # Nomes originais + normalizados de cada camada (mantendo o índice OGR)
    camadas_info = []
    for indice in range(total_camadas):
        nome_original = datasource.GetLayerByIndex(indice).GetName()
        nome_normalizado = normalizar_nome_camada(nome_original)
        camadas_info.append((indice, nome_original, nome_normalizado))

    # Conjunto "vivo" de nomes de tabela em uso no arquivo (case-insensitive)
    nomes_em_uso_lower = obter_nomes_tabelas_existentes(datasource)

    # Define o plano de renomeação, já resolvendo colisões previamente
    renomeacoes = []
    for indice, nome_original, nome_normalizado in camadas_info:
        if nome_original == nome_normalizado:
            print(f"[OK]        '{nome_original}' já está padronizado.")
            continue

        # Libera o nome atual da camada, pois ele deixará de existir após
        # o rename (evita que uma camada "bloqueie" seu próprio slot).
        nomes_em_uso_lower.discard(nome_original.lower())

        nome_final = gerar_nome_unico(nome_normalizado, nomes_em_uso_lower)
        nomes_em_uso_lower.add(nome_final.lower())
        renomeacoes.append((indice, nome_original, nome_final))

    # Aplica (ou simula) as renomeações
    for indice, nome_original, nome_final in renomeacoes:
        if dry_run:
            observacao = (
                " (via nome temporário, mudança apenas de caixa)"
                if eh_apenas_mudanca_de_caixa(nome_original, nome_final)
                else ""
            )
            print(f"[SIMULAÇÃO] '{nome_original}' -> '{nome_final}'{observacao}")
            continue

        camada = datasource.GetLayerByIndex(indice)
        try:
            renomear_camada(camada, nome_original, nome_final)
            print(f"[RENOMEADO] '{nome_original}' -> '{nome_final}'")
        except RuntimeError as erro:
            print(f"[ERRO]      {erro}")

    datasource = None  # fecha o datasource e persiste as alterações

    print(f"\nConcluído. {len(renomeacoes)} camada(s) "
          f"{'seriam renomeadas' if dry_run else 'renomeadas'}.")


# ---------------------------------------------------------------------------
# Execução
# ---------------------------------------------------------------------------

if __name__ == "__console__" or __name__ == "__main__":
    normalizar_camadas_gpkg(GPKG_PATH, dry_run=DRY_RUN)