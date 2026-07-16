# Organização dos arquivos Claude neste projeto

Este documento descreve onde vive cada tipo de arquivo relacionado ao Claude Code
dentro do repositório `insa-front`, e onde vive o que **não** está no repositório.

---

## No repositório (versionado)

```
insa-front/
├── CLAUDE.md                        ← instruções do projeto (arquitetura, pipeline, convenções)
├── CLAUDE_ORGANIZATION.md           ← este arquivo
└── .claude/
    ├── settings.local.json          ← permissões locais desta máquina (NÃO versionado)
    └── commands/                    ← skills / slash commands do projeto (versionados)
        ├── add-layer.md             → /add-layer
        ├── atualizar-metadados.md   → /atualizar-metadados
        ├── inspect-layer.md         → /inspect-layer
        ├── pipeline.md              → /pipeline
        ├── status.md                → /status
        └── wrap-up.md               → /wrap-up
```

- **`CLAUDE.md`** é a fonte única de verdade sobre arquitetura, pipeline de dados
  e convenções do projeto. Deve ser lido no início de toda sessão.
- **`.claude/commands/*.md`** são os slash commands específicos deste projeto.
  Cada arquivo vira um comando `/nome-do-arquivo` disponível no Claude Code
  quando a sessão é aberta na raiz do `insa-front`.
- **`.claude/settings.local.json`** guarda permissões de ferramentas aprovadas
  nesta máquina (ex.: quais comandos `Bash` rodar sem confirmação). É pessoal
  por máquina — por isso não é commitado, mesmo não estando listado
  explicitamente no `.gitignore` (nunca foi adicionado ao índice do git).
- **`.claude/.DS_Store`** é lixo do macOS (Finder), já coberto pela regra
  genérica `.DS_Store` no `.gitignore` raiz.

## Fora do repositório (estado global do Claude Code)

Tudo abaixo mora em `~/.claude/` e é **compartilhado por todos os projetos**
da máquina (insa-front, hydrogis, sigitr, geoserver-migration, etc.) — não é
específico deste repositório e não deve ser editado manualmente:

| O quê | Onde |
|---|---|
| Memória automática deste projeto (fatos, preferências, feedback) | `~/.claude/projects/-Users-marcellodebarrosfilho-code-insa-front/memory/` |
| Histórico de sessões/conversas | `~/.claude/projects/-Users-marcellodebarrosfilho-code-insa-front/*.jsonl` |
| Config global do Claude Code (todos os projetos) | `~/.claude/settings.json` |
| Plugins instalados | `~/.claude/plugins/` |
| Cache, backups, sessões, snapshots de shell | `~/.claude/cache/`, `~/.claude/backups/`, `~/.claude/sessions/`, `~/.claude/shell-snapshots/` |

Esses diretórios são gerenciados pelo próprio Claude Code — não fazem parte do
código do projeto e não devem ser reorganizados manualmente.

---

## Guideline para novos arquivos Claude

- **Nova skill/slash command específica deste projeto** → criar em
  `.claude/commands/<nome>.md` e commitar.
- **Nova instrução permanente sobre arquitetura/convenções** → editar
  `CLAUDE.md` na raiz.
- **Preferência pessoal ou permissão de ferramenta desta máquina** →
  `.claude/settings.local.json` (não commitar).
- Nunca criar pastas paralelas de config Claude fora de `.claude/` — a raiz do
  projeto e `.claude/commands/` são os únicos locais válidos para artefatos
  Claude versionados neste repositório.
