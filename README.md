# insa-front

This template should help get you started developing with Vue 3 in Vite.

## Recommended IDE Setup

[VS Code](https://code.visualstudio.com/) + [Vue (Official)](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (and disable Vetur).

## Recommended Browser Setup

- Chromium-based browsers (Chrome, Edge, Brave, etc.):
  - [Vue.js devtools](https://chromewebstore.google.com/detail/vuejs-devtools/nhdogjmejiglipccpnnnanhbledajbpd)
  - [Turn on Custom Object Formatter in Chrome DevTools](http://bit.ly/object-formatters)
- Firefox:
  - [Vue.js devtools](https://addons.mozilla.org/en-US/firefox/addon/vue-js-devtools/)
  - [Turn on Custom Object Formatter in Firefox DevTools](https://fxdx.dev/firefox-devtools-custom-object-formatters/)

## Customize configuration

See [Vite Configuration Reference](https://vite.dev/config/).

## Project Setup

```sh
npm install
```

### Compile and Hot-Reload for Development

```sh
npm run dev
```

### Compile and Minify for Production

```sh
npm run build
```

### Lint with [ESLint](https://eslint.org/)

```sh
npm run lint
```

```
for camada in $(ogrinfo -q dados_insa.gpkg | awk -F': ' '{print $2}'); do
    echo "Convertendo camada: $camada ..."
    ogr2ogr -f "GeoJSON" "geojson/${camada}.geojson" dados_insa.gpkg "$camada" -t_srs EPSG:4326
done


tippecanoe -o mbtiles/insa_layers.mbtiles \
  -z14 -Z2 \
  --no-feature-limit \
  --no-tile-size-limit \
  --extend-zooms-if-still-dropping \
  --no-tile-compression \
  --force \
  geojson/*.geojson
```

```
python3 export.py

python3 styles.py
```
