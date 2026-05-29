# Inspecionar camada

Inspeciona uma camada em profundidade — útil para configurar `popUpFields`,
`descFields`, `searchFields` e `fieldTypes` corretamente.

Informe o nome da camada (valor de `sourceLayer`) para continuar.

## O que será feito

### 1 — Campos disponíveis no GeoPackage

```bash
ogrinfo -al -so data/dados_insa.gpkg <nome_camada>
```

Lista todos os campos com seus tipos (String, Integer, Real, etc.).

### 2 — Amostra de valores reais

```bash
python3 - <<'EOF'
import sqlite3, json

conn = sqlite3.connect("data/dados_insa.gpkg")
cur = conn.cursor()

# descobre o nome da tabela
cur.execute("SELECT table_name FROM gpkg_contents WHERE table_name LIKE '%<nome_camada>%'")
table = cur.fetchone()[0]

# lê primeiras 3 feições
cur.execute(f"SELECT * FROM \"{table}\" LIMIT 3")
cols = [d[0] for d in cur.description]
rows = cur.fetchall()

for row in rows:
    print(json.dumps(dict(zip(cols, row)), ensure_ascii=False, indent=2))

conn.close()
EOF
```

### 3 — Entrada atual em `layers.js`

Ler `src/config/layers.js` e exibir o objeto completo da camada, se já existir.

### 4 — Entrada em `styles.json`

Ler `src/assets/styles.json` e exibir a entrada correspondente à camada.

### 5 — Recomendações

Com base nos campos e valores inspecionados, sugerir:

- `searchFields`: campo(s) mais úteis para busca (priorizar campos textuais identificadores)
- `fieldTypes`: tipo correto para cada campo (`'string'` ou `'number'`)
- `popUpFields`: campos relevantes para exibir no popup (excluir `id`, `gid`, `fid`, `objectid`, `geom`)
- `descFields`: sugestão de rótulos amigáveis em português para cada campo
- `zIndex`: valor recomendado conforme a categoria da camada

Apresentar a sugestão como um objeto JavaScript pronto para colar em `layers.js`.
