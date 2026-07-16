# Atualizar dashboard após mudança nos dados

Regenera tudo que o dashboard de comparação (`/dashboard`) depende — legendas,
estatísticas por classe e cruzamento por município — sempre que o GeoPackage
(`data/dados_insa.gpkg`) mudar. Use este comando toda vez que uma camada de
índice for editada/adicionada no QGIS, em vez de lembrar manualmente quais
scripts rodar e em que ordem.

> ⚠️ Se as **geometrias ou tiles** também mudaram (não só atributos/estilo),
> rode `/pipeline` primeiro — este comando não reexporta GeoJSON nem regera
> `.mbtiles`/`.pbf`. Ele assume que o GeoPackage já está no estado final e
> cuida apenas da parte específica do dashboard.

Todos os comandos rodam a partir da **raiz do projeto**.

## Passo 1 — Reextrair estilos (legendas)

```bash
python scripts/styles.py
```

Isso **sobrescreve `src/assets/styles.json` inteiro**. Depois de rodar,
restaure imediatamente as entradas manuais de camadas stroke-only
(`municipios_pb_semiarido`, `limite_semiarido_pb`, `estados_ne`) — os blocos
exatos estão na seção "Step 4 — Extract styles" do `CLAUDE.md`. Confirme que
todas as camadas esperadas (ver tabela "Existing layers" no `CLAUDE.md`) estão
presentes no arquivo antes de continuar.

## Passo 2 — Regenerar estatísticas por classe

```bash
python scripts/stats.py
```

Gera `src/assets/stats.json` a partir do `styles.json` restaurado no Passo 1.
Alimenta tanto a legenda da sidebar (`LayerCard.vue`) quanto o gráfico de
pizza do dashboard (`DashboardPieChart.vue`) e o modal de gráfico
(`LayerChartModal.vue`). Rodar sempre — barato e idempotente mesmo que nenhum
dos 5 índices compostos tenha mudado.

## Passo 3 — Regenerar cruzamento por município

```bash
python scripts/dashboard_stats.py
```

Gera `src/assets/dashboard_stats.json`, cruzando `municipios_pb_semiarido`
com `iqs`/`iqv`/`iqc`/`iqm`/`ivd_sab`. Depende do `styles.json` do Passo 1 —
por isso a ordem dos passos importa. Estritamente necessário só quando um
desses 5 índices muda, mas seguro rodar sempre.

## Passo 4 — Limites municipais (só se mudaram no GeoPackage)

`public/data/municipios_pb_semiarido.geojson` é versionado e **não** faz parte
do pipeline de tiles — só regenerar se os limites municipais em si mudaram:

```bash
ogr2ogr -f GeoJSON public/data/municipios_pb_semiarido.geojson \
  data/dados_insa.gpkg municipios_pb_semiarido \
  -t_srs EPSG:4326 -simplify 0.0015
```

Pule este passo se só os valores/atributos dos índices mudaram.

## Passo 5 — Verificação final

```bash
npm run dev
```

Abrir `/dashboard` no navegador e conferir:

- Seletor de índice (IQS/IQV/IQC/IQM/IVS) atualiza tabela, gráfico de pizza e mini-mapa
- Gráfico de pizza: fatias e legenda na mesma ordem da legenda da sidebar (Baixa → Muito Alta)
- Tabela: valores e classe dominante preenchidos para os municípios (sem `null` inesperado)
- Mini-mapa: cores do índice corretas; clicar/selecionar uma linha da tabela destaca e dá zoom no município certo

Se algo divergir, o problema está em um dos três JSONs gerados acima — não em
código do componente.
