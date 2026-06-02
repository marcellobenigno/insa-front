# Atualizar metadados das camadas

Leia o arquivo LEVANTAMENTO_METADADOS.docx na raiz do projeto (ou em data/).
Para cada camada definida em `src/config/layers.js`, localize os campos 
correspondentes no documento e atualize os `descFields` com os nomes amigáveis 
e descrições encontrados no levantamento.

Regras:
- Não altere nenhum outro campo além de `descFields`
- Se um campo do levantamento não existir na camada, ignore-o
- Mantenha a formatação e estilo do arquivo layers.js
