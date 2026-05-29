# Fechar sessão

Ritual de encerramento. Executar sempre ao terminar uma sessão de desenvolvimento.

## 1 — Resumo do que foi feito

Listar em bullet points tudo que foi alterado nesta sessão:
- Arquivos criados ou modificados
- Camadas adicionadas ou alteradas
- Pipeline executado (se foi)
- Bugs corrigidos
- Decisões tomadas (e por quê)

## 2 — Verificar se o CLAUDE.md precisa de atualização

Checar se alguma das mudanças desta sessão torna o CLAUDE.md desatualizado:

- Nova camada adicionada → atualizar tabela de camadas e comando Tippecanoe
- Nova convenção de código adotada → adicionar em "What NOT to do" ou na seção relevante
- Problema encontrado e resolvido → documentar para evitar repetição
- Dependência nova instalada → atualizar tabela de stack

Se houver atualizações, aplicá-las no `CLAUDE.md` agora.

## 3 — Commit semântico

Sugerir uma mensagem de commit clara que descreva o que foi feito.
Formato recomendado:

```
<tipo>(<escopo>): <descrição curta>

<corpo opcional explicando decisões não óbvias>
```

Tipos: `feat`, `fix`, `refactor`, `docs`, `chore`, `style`

Exemplos para este projeto:
- `feat(layers): add textura_sab_pb_original layer with popup fields`
- `fix(renderer): add DSC_TEXTUR to possibleValues for texture layer`
- `chore(pipeline): regenerate tiles after adding ia_sab_pb layers`
- `docs(claude): update layer table and tippecanoe command`

## 4 — Próximos passos

Listar o que ficou pendente ou o que faz sentido abordar na próxima sessão.
Isso será o ponto de partida quando você rodar `/status` na próxima vez.
