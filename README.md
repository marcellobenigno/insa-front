# INSA Front

Aplicação web de mapeamento GIS desenvolvida com Vue 3 + Vite. Exibe camadas vetoriais do INSA sobre um mapa base interativo (Google Satellite, Google Streets, OSM e outros), com suporte a vector tiles locais e legendas dinâmicas por camada.

## Ambiente de homologação

[![Abrir aplicação](https://img.shields.io/badge/Abrir%20aplicação-insa--front-blue?style=for-the-badge)](https://marcellobenigno.github.io/insa-front/)

Ambiente atualizado automaticamente a cada push na branch `main`.
Use este link para visualizar e validar as camadas junto à equipe.

## Pré-requisitos

- **Node.js** `^20.19.0` ou `>=22.12.0`

## Instalação e execução

```sh
npm install
npm run dev       # servidor de desenvolvimento com hot-reload
npm run build     # build de produção em dist/
npm run preview   # preview do build de produção
```

## Comandos disponíveis

| Comando | Descrição |
|---|---|
| `npm run dev` | Servidor de desenvolvimento (Vite) |
| `npm run build` | Build de produção |
| `npm run preview` | Preview do build de produção |
| `npm run lint` | Executa oxlint + eslint com auto-fix |
| `npm run format` | Formata os arquivos de `src/` com Prettier |
| `npm run deploy:tiles` | Empacota e envia os tiles para o servidor de produção |

## Arquitetura

```
src/
├── components/
│   ├── MapContainer.vue   # instância do Leaflet; reage ao store
│   ├── AppSidebar.vue     # painel lateral: accordion de camadas + filtro por nome
│   ├── LayerCard.vue      # card por camada (visibilidade, opacidade, legenda, busca por atributo)
│   ├── GeoSearch.vue      # busca geocodificada + coordenadas (DD, DMS, endereço)
│   └── CoordDisplay.vue   # overlay de coordenadas do cursor em tempo real (DD e DMS)
├── composables/
│   └── useSidebar.js      # estado do accordion e colapso da sidebar
├── stores/
│   └── mapStore.js        # Pinia — estado das camadas, filtros de busca, localização
├── config/
│   └── layers.js          # definição das camadas base e overlays por categoria
├── utils/
│   ├── mapRenderer.js     # renderiza feições no canvas via styles.json
│   └── mapPopup.js        # monta o HTML do popup de clique no mapa
├── router/
│   └── index.js           # Vue Router (rota única: HomeView)
├── views/
│   └── HomeView.vue       # layout principal
└── assets/
    └── styles.json        # estilos de legenda gerados por scripts/styles.py
```

**Fluxo de dados das camadas:**

1. `mapStore.js` mantém o estado reativo: qual camada base está ativa e a visibilidade/opacidade de cada overlay.
2. `AppSidebar.vue` / `LayerCard.vue` leem e mutam o store diretamente.
3. `MapContainer.vue` observa o store com watchers e aplica as mudanças ao mapa via Leaflet — nunca guarda estado de camada próprio.

> **Restrição importante:** Leaflet não funciona em SSR. O mapa é inicializado em `onMounted` e destruído em `onUnmounted`. Não acesse `L` nem a instância do mapa fora desses hooks.

---

## Funcionalidades da interface

### Sidebar

- **Filtro de camadas por nome** — campo de texto acima das categorias filtra as camadas em tempo real (case-insensitive). Categorias sem resultado são ocultadas; as que têm resultado expandem automaticamente. O badge "Análise Temática" exibe `N de 17` ao filtrar.
- **Accordion por categoria** — cada categoria pode ser expandida/recolhida individualmente.
- **Badge de visibilidade** — indicador numérico por categoria mostra quantas camadas estão ativas no mapa.

### Painel de busca por atributo (por camada)

Acessado pelo ícone de lupa em cada `LayerCard`. Permite filtrar feições por valor de campo:

- **Campos string** — busca por substring, case-insensitive
- **Campos numérico** — suporta operadores `=`, `>`, `>=`, `<`, `<=`
- **Feedback visual** — feições que batem ficam destacadas com borda amarela; as demais ficam acinzentadas
- **Badge de resultado** — exibe "Nenhum resultado encontrado" (vermelho) quando o filtro não encontra feições; o resultado é atualizado à medida que novos tiles carregam

### GeoSearch (rodapé da sidebar)

- Busca por endereço via Nominatim (geocodificação)
- Entrada de coordenadas em DD (decimal) ou DMS (graus, minutos, segundos)
- Resultados restritos ao bounding box do Semiárido da PB

### CoordDisplay

Overlay no canto inferior do mapa exibe as coordenadas do cursor em DD e DMS em tempo real.

---

## Referência: `src/config/layers.js`

Este é o **único arquivo que você precisa editar** para controlar quais camadas existem, como elas aparecem na sidebar e o que o popup de clique exibe. Não há nenhuma outra configuração de camadas espalhada pela aplicação.

### Estrutura geral

O arquivo exporta dois objetos principais:

| Export | Usado por |
|---|---|
| `BASE_LAYERS` | 6 mapas de fundo (Google Satellite ★, Google Streets, Google Hybrid, Google Terrain, OSM, OSM Dark) — selecionados via radio button. ★ = ativo por padrão. |
| `OVERLAY_CATEGORIES` | Camadas de sobreposição agrupadas por categoria — exibidas no accordion da sidebar |

`OVERLAY_LAYERS` (export derivado) é gerado automaticamente a partir de `OVERLAY_CATEGORIES` para retrocompatibilidade interna — não edite diretamente.

---

### Campos de cada camada overlay

```js
nome_da_camada: {
  // ── Obrigatórios ──────────────────────────────────────────────────────────
  label:       'Rótulo exibido no menu e no popup',
  meta:        'Descrição curta exibida abaixo do rótulo na sidebar',
  url:         VECTOR_TILES_URL,          // URL do servidor de tiles (não alterar)
  sourceLayer: 'nome_exato_no_gpkg',      // deve bater com o layer_id dentro do .pbf
  zIndex:      20,                        // maior = fica acima de outras camadas no mapa
  active:      false,                     // true = camada visível ao carregar a página

  // ── Pesquisa (barra de busca) ─────────────────────────────────────────────
  searchFields: ['campo1', 'campo2'],     // campos pesquisáveis na barra de busca
  fieldTypes:   { campo1: 'string',       // tipo de cada campo: 'string' ou 'number'
                  campo2: 'number' },     // usado para aplicar operadores de comparação

  // ── Popup de clique ───────────────────────────────────────────────────────
  popUpFields: ['campo1'],               // quais campos aparecem no popup, em qual ordem
                                          // se omitido, exibe todos os campos da feição
  descFields:  { campo1: 'Descrição',    // rótulo amigável para cada campo no popup
                 campo2: 'Valor Peso' }, // se um campo não estiver aqui, usa o nome técnico
},
```

#### Detalhes por campo

**`sourceLayer`**
Deve ser idêntico ao nome da camada no GeoPackage. O Tippecanoe usa o nome do arquivo GeoJSON (sem extensão) como `layer_id` dentro do `.pbf` — qualquer divergência faz os tiles não renderizarem.

**`zIndex`**
Controla a ordem de empilhamento visual. Camadas com `zIndex` maior ficam na frente. Sugestão de faixas do projeto:

| Faixa | Uso |
|---|---|
| 1 | Camadas base (tile layers) |
| 10–19 | Índices e dados temáticos |
| 20–29 | Solos e textura |
| 30+ | Limites administrativos (sempre na frente) |

**`searchFields`**
Lista dos campos que a barra de busca inspeciona. Funciona com operadores: `>`, `<`, `>=`, `<=`, `=` para campos numéricos; substring case-insensitive para strings. Deve incluir pelo menos um campo que identifique a feição de forma legível.

**`fieldTypes`**
Dicionário `{ nomeDoCampo: 'string' | 'number' }`. Usado pela busca para decidir se aplica comparação numérica ou textual. Campos ausentes aqui são tratados como string.

**`popUpFields`**
Array com os nomes dos campos que devem aparecer no popup ao clicar no mapa — **na ordem declarada**. Campos que existem na feição mas não estão nesta lista são silenciosamente ignorados.

Se `popUpFields` for omitido, o popup exibe todos os campos da feição (exceto `id`, `gid`, `fid`, `objectid`), que é o comportamento legado.

**`descFields`**
Dicionário que mapeia nome técnico do campo → rótulo legível exibido na coluna esquerda do popup. Exemplo:

```js
descFields: {
  DSC_TEXTUR: 'Descrição',
  SoilTextur: 'Textura do Solo',
}
```

Se um campo estiver em `popUpFields` mas não em `descFields`, o nome técnico (`DSC_TEXTUR`) é usado como fallback — então é seguro preencher `descFields` gradualmente conforme os metadados forem levantados.

---

### Adicionando uma nova categoria

```js
export const OVERLAY_CATEGORIES = {
  // ... categorias existentes ...

  nova_categoria: {
    label: 'Nome no accordion',
    color: '#34d399',          // cor do indicador visual na sidebar (CSS color)
    icon:  'bi-tree',          // classe Bootstrap Icons
    layers: {
      // ... suas camadas aqui ...
    },
  },
}
```

---

## Pipeline de dados (GeoPackage → Vector Tiles)

Esta seção documenta como os dados brutos em `data/dados_insa.gpkg` são convertidos em vector tiles servidos pela aplicação.

> ⚠️ **ATENÇÃO — leia antes de qualquer alteração**
>
> Sempre que uma camada for adicionada, removida ou alterada no GeoPackage, **todos os passos abaixo devem ser refeitos do zero**, incluindo a exclusão completa do diretório `public/tiles/insa_layers/` antes de reextrair.
>
> **Não existe atualização parcial.** Cada arquivo `.pbf` em `public/tiles/` contém *todas* as camadas embutidas naquele tile — não é possível apenas "adicionar os tiles da nova camada" sem sobrescrever tudo. Se o diretório antigo não for apagado, tiles obsoletos permanecem e podem causar comportamento inesperado.

### Por que regenerar tudo?

Os tiles em `public/tiles/insa_layers/{z}/{x}/{y}.pbf` **não são arquivos por camada** — cada arquivo `.pbf` contém *todas* as camadas embutidas naquele tile. Isso é gerado pelo Tippecanoe, que empacota múltiplos GeoJSONs em um único `.mbtiles`. Por isso, **não é possível adicionar só os tiles de uma nova camada** sem regenerar o arquivo inteiro. O processo completo precisa ser repetido a cada mudança.

### Ferramentas necessárias

Instale antes de começar:

```bash
# macOS
brew install gdal tippecanoe python3

# Verifica as versões
ogr2ogr --version   # GDAL 3.x
tippecanoe --version  # tippecanoe v2.x
python3 --version   # Python 3.x
```

### Diretório de trabalho

Todos os comandos a seguir devem ser executados da **raiz do projeto**.

### Passo 1 — Exportar camadas do GeoPackage para GeoJSON

Use `ogr2ogr` para exportar **cada camada de interesse** para um arquivo GeoJSON reprojetado em WGS-84 (EPSG:4326). Um arquivo por camada:

```bash
ogr2ogr -f GeoJSON data/geojson/<nome_da_camada>.geojson \
  data/dados_insa.gpkg <nome_da_camada> \
  -t_srs EPSG:4326
```

Para listar todas as camadas disponíveis no GeoPackage:

```bash
ogrinfo -q data/dados_insa.gpkg
```

> **Nota:** o arquivo `geojson/layer_styles.geojson` é gerado automaticamente ao exportar a tabela interna de estilos do QGIS. Ele deve ser incluído no comando do Tippecanoe (passo 2), mas não precisa ser cadastrado como camada na aplicação.

### Passo 2 — Gerar o `.mbtiles` com Tippecanoe

Este passo empacota **todos** os GeoJSONs em um único arquivo de vector tiles. O comando abaixo é o definitivo do projeto — atualize-o sempre que adicionar ou remover uma camada:

```bash
tippecanoe \
  -o data/mbtiles/insa_layers.mbtiles \
  -z14 -Z2 \
  --no-feature-limit \
  --no-tile-size-limit \
  --extend-zooms-if-still-dropping \
  --no-tile-compression \
  --force \
  data/geojson/declividade_sab_pb_original.geojson \
  data/geojson/declividade_sab_pb_pesos.geojson \
  data/geojson/eto_sab_pb_original.geojson \
  data/geojson/eto_sab_pb_pesos.geojson \
  data/geojson/geologia_sab_pb_original.geojson \
  data/geojson/geologia_sab_pb_pesos.geojson \
  data/geojson/ia_sab_pb_original.geojson \
  data/geojson/ia_sab_pb_pesos.geojson \
  data/geojson/iqc_sab_pb.geojson \
  data/geojson/iqs_sab_pb.geojson \
  data/geojson/layer_styles.geojson \
  data/geojson/municipios_pb_semiarido.geojson \
  data/geojson/precipitacao_sab_pb_original.geojson \
  data/geojson/precipitacao_sab_pb_pesos.geojson \
  data/geojson/solos_tipos_sab_pb_original.geojson \
  data/geojson/solos_tipos_sab_pb_pesos.geojson \
  data/geojson/textura_sab_pb_original.geojson \
  data/geojson/textura_sab_pb_pesos.geojson
```

Flags usadas:

| Flag | Motivo |
|---|---|
| `-z14 -Z2` | Gera tiles do zoom 2 (visão geral) ao 14 (detalhe) |
| `--no-feature-limit` | Não descarta feições por limite de quantidade por tile |
| `--no-tile-size-limit` | Não descarta feições por limite de tamanho do tile |
| `--extend-zooms-if-still-dropping` | Aumenta zoom máximo se ainda estiver descartando dados |
| `--no-tile-compression` | Salva os `.pbf` sem compressão (necessário para leitura direta pelo browser) |
| `--force` | Sobrescreve o `.mbtiles` existente sem perguntar |

> **Atenção:** o Tippecanoe pode demorar alguns minutos dependendo do volume de dados. O arquivo gerado (`insa_layers.mbtiles`) tem em torno de 90 MB — não comitar no git.

### Passo 3 — Apagar tiles antigos e reextrair

> ⚠️ **O `rm -rf` é obrigatório** — nunca pule este passo. Os tiles antigos não são sobrescritos, apenas somados. Se uma camada for removida do `.mbtiles`, os tiles dela permaneceriam em disco e seriam servidos pelo browser mesmo depois da atualização.

```bash
# Apaga TODOS os tiles antigos
rm -rf public/tiles/insa_layers

# Reextrai do .mbtiles recém-gerado
python scripts/export.py
```

O script lê `data/mbtiles/insa_layers.mbtiles` e grava cada tile em `public/tiles/insa_layers/{z}/{x}/{y}.pbf`, aplicando a inversão de eixo Y necessária para compatibilidade com o padrão XYZ do Leaflet.

### Passo 4 — Extrair estilos do GeoPackage

```bash
python scripts/styles.py
```

Lê a tabela `layer_styles` do GeoPackage (criada pelo QGIS ao salvar estilos), extrai as cores de preenchimento por categoria e grava em `../src/assets/styles.json`. Esse arquivo é consumido pelo componente `LayerCard.vue` para montar a legenda e por `mapRenderer.js` para colorir as feições no canvas.

#### Quando `styles.py` não captura uma camada

O script só extrai cores de **preenchimento** (`fill`). Se uma camada no QGIS for estilizada apenas com **borda** (stroke), sem preenchimento, ela não aparecerá no `styles.json` gerado. Nesse caso, adicione a entrada manualmente:

```json
"nome_da_camada": {
  "Rótulo legenda": "stroke:#rrggbb"
}
```

O prefixo `stroke:` instrui o renderer a desenhar apenas o contorno do polígono, sem preenchimento. Exemplo real do projeto:

```json
"municipios_pb_semiarido": {
  "Limite municipal": "stroke:#ffffff"
}
```

---

## Deploy dos tiles para produção

Após regenerar os tiles localmente (passos 2–3 acima), publique no servidor com:

```bash
npm run deploy:tiles
```

O script `scripts/deploy-tiles.sh` executa automaticamente:

1. Compacta `public/tiles/insa_layers/` em `insa_layers.tar.gz` (~20 MB)
2. Envia o arquivo via SCP para `ubuntu@geoserver.multisig.com.br`
3. No servidor: remove os tiles antigos, extrai o novo arquivo em `/var/lib/tomcat9/webapps/tiles/`
4. Remove o `.tar.gz` local e remoto

> O servidor aceita chave SSH sem senha. Certifique-se de que sua chave pública está em `~/.ssh/authorized_keys` no servidor antes de executar.

---

## Como adicionar uma nova camada

Siga a checklist abaixo na ordem:

### 1. Dados

- [ ] Adicione a camada ao `dados_insa.gpkg` no QGIS e salve o estilo
- [ ] Exporte para GeoJSON: `ogr2ogr -f GeoJSON data/geojson/<camada>.geojson data/dados_insa.gpkg <camada> -t_srs EPSG:4326`
- [ ] Adicione o novo `.geojson` ao comando do Tippecanoe no Passo 2 acima (e atualize este README)
- [ ] Regere o `.mbtiles` (Passo 2)
- [ ] Regere os tiles (Passo 3: `rm -rf public/tiles/insa_layers` + `python scripts/export.py`)
- [ ] Regere os estilos (Passo 4: `python scripts/styles.py`)
- [ ] Regere as estatísticas (Passo 5: `python scripts/stats.py`)
- [ ] Se a camada for stroke-only, adicione a entrada manualmente em `src/assets/styles.json`

### 2. Código

Abra `src/config/layers.js` e adicione um objeto na categoria adequada (ou crie uma nova). Veja a [Referência: `src/config/layers.js`](#referência-srcconfiglayersjs) para a descrição completa de cada campo.

```js
nova_camada: {
  label: 'Rótulo no menu',
  meta: 'Descrição curta',
  url: VECTOR_TILES_URL,
  sourceLayer: 'nome_exato_no_gpkg',    // deve bater com o nome da camada no Tippecanoe
  zIndex: 31,                            // maior = fica acima de outras camadas
  active: false,                         // false = camada começa oculta
  searchFields: ['campo1', 'campo2'],    // campos inspecionados pela barra de busca
  fieldTypes:   { campo1: 'string',      // tipo de cada campo: 'string' ou 'number'
                  campo2: 'number' },
  popUpFields:  ['campo1', 'campo2'],    // campos exibidos no popup de clique (em ordem)
  descFields:   { campo1: 'Descrição',   // rótulo amigável por campo no popup
                  campo2: 'Valor' },
},
```

> `sourceLayer` deve ser **idêntico** ao nome da camada no GeoPackage (e ao nome usado no GeoJSON exportado). O Tippecanoe usa o nome do arquivo sem a extensão como `layer_id` dentro do `.pbf`.

### 3. Renderer (se necessário)

Se a nova camada tiver campos não listados em `src/utils/mapRenderer.js` → `possibleValues`, adicione-os para que o renderer consiga associar o valor da feição à cor correta da legenda:

```js
featureProps?.nome_do_campo_novo,
```

---

## Estrutura de `data/`

```
data/
├── dados_insa.gpkg          # fonte primária — GeoPackage com todas as camadas e estilos
├── geojson/                 # camadas exportadas em GeoJSON (intermediário)
│   ├── <camada>.geojson
│   └── ...
├── mbtiles/
│   └── insa_layers.mbtiles  # vector tiles empacotados (~90 MB, não versionar)
├── export.py                # extrai tiles do .mbtiles para public/tiles/
└── styles.py                # extrai estilos do .gpkg para src/assets/styles.json
```

> **`.mbtiles` e `geojson/` não devem ser versionados no git** por causa do tamanho. Certifique-se de que estão no `.gitignore`.

---

## Stack

| Lib | Uso |
|---|---|
| Vue 3 (Composition API + `<script setup>`) | Framework UI |
| Pinia | Gerenciamento de estado |
| Leaflet 1.x | Renderização do mapa |
| leaflet.vectorgrid | Plugin Leaflet para renderizar vector tiles `.pbf` |
| Bootstrap 5 | Layout e componentes visuais |
| Bootstrap Icons | Ícones carregados via CDN em `index.html` |
| FontAwesome 7 | Ícones adicionais (tree-shaken via `src/main.js`) |
| Oxlint + ESLint + Prettier | Qualidade de código |

## IDE recomendada

[VS Code](https://code.visualstudio.com/) com a extensão [Vue (Official)](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (desative o Vetur se estiver instalado).
