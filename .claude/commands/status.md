# Status do projeto insa-front

Faz um diagnóstico completo do estado atual antes de começar qualquer trabalho.

## 1 — Git: o que foi feito recentemente

```bash
git log --oneline -15
git status
```

## 2 — Camadas: consistência entre código e dados

Ler `src/config/layers.js` e extrair todos os valores de `sourceLayer` das camadas ativas.

Comparar com:
- GeoJSONs presentes em `data/geojson/`
- Camadas no GeoPackage: `ogrinfo -q data/dados_insa.gpkg`
- Tiles gerados: `ls public/tiles/insa_layers/ | head -5` (verificar se existe)

Reportar:
- Camadas em `layers.js` sem GeoJSON correspondente
- Camadas em `layers.js` sem tiles gerados
- Camadas no GeoPackage não registradas em `layers.js`

## 3 — Styles: cobertura do styles.json

Ler `src/assets/styles.json` e comparar com os `sourceLayer` registrados em `layers.js`.

Reportar quais camadas não têm entrada em `styles.json` (podem ser stroke-only não adicionadas manualmente).

## 4 — Dependências

```bash
node --version
npm --version
cat package.json | grep -E '"version"|"vue"|"leaflet"|"pinia"|"vite"'
```

## 5 — Resumo final

Apresentar um resumo com:
- Total de camadas registradas em `layers.js`
- Camadas com `active: true` (visíveis ao carregar)
- Categorias existentes na sidebar
- Problemas encontrados (se houver)
- Sugestão do próximo passo mais lógico baseado no git log
