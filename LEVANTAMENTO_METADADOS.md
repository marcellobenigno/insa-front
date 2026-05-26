# Levantamento de Metadados — Interface Cartográfica INSA

**Documento:** Questionário técnico para validação e enriquecimento da interface  
**Destinatários:** Equipe responsável pela preparação e curadoria dos dados geoespaciais  
**Versão atual da interface:** `main` (estado atual do repositório)

---

## Contexto e Objetivo

A interface cartográfica do INSA exibe camadas vetoriais sobre o Semiárido paraibano. Cada camada é
carregada a partir de um GeoPackage, convertida em vector tiles e renderizada no navegador.

Para que a interface seja útil ao usuário final, ela precisa apresentar informações legíveis e
relevantes — não apenas os dados brutos do arquivo geográfico. Isso envolve:

- **Nomenclatura** adequada para categorias e camadas no menu lateral
- **Descrições** (metadados) que expliquem o que cada camada representa
- **Campos** significativos para exibição no popup de clique no mapa
- **Campos** adequados para a barra de busca (filtro por atributo)

Este documento lista o estado atual da interface e solicita a revisão da equipe de dados em cada
ponto. **Preencha diretamente neste arquivo**, substituindo os campos marcados com
`[ PREENCHER ]` ou editando as tabelas conforme necessário.

---

## Como Preencher

- Campos marcados com `[ PREENCHER ]` aguardam resposta da equipe.
- Tabelas com coluna **"Aprovado?"** devem ser marcadas com `✅` (manter) ou `❌` (alterar).
- Quando a resposta for `❌`, preencha a coluna **"Sugestão / Correção"**.
- Campos opcionais podem ser deixados em branco se não houver informação disponível no momento.
- Dúvidas técnicas sobre o impacto de cada campo na interface estão descritas em cada seção.

---

---

## 1. Categorias de Camadas

### Por que isso importa

As camadas são agrupadas em **categorias** no menu lateral (accordion). O agrupamento define como
o usuário navega pela interface. Uma categoria com nome impreciso ou que mistura temas distintos
prejudica a usabilidade.

### Estado atual

| # | ID interno | Nome exibido na interface | Aprovado? | Sugestão / Correção |
|---|---|---|---|---|
| 1 | `semiarido_pb` | Semiárido PB | | |
| 2 | `indices_qualidade` | Índices de Qualidade | | |
| 3 | `declividade` | Declividade | | |
| 4 | `geologia` | Geologia | | |
| 5 | `solos` | Solos | | |
| 6 | `agroclimatologia` | Agroclimatologia | | |

### Perguntas adicionais

**1.1** Há temas temáticos que deveriam ser agrupados de forma diferente? (ex.: "Declividade" e
"Geologia" poderiam fazer parte de uma categoria "Características Físicas do Solo"?)

> [ PREENCHER ]

**1.2** Há novas categorias previstas para versões futuras que já devemos reservar espaço?

> [ PREENCHER ]

---

---

## 2. Nomenclatura das Camadas

### Por que isso importa

O **nome da camada** é exibido: (a) no menu lateral ao lado do checkbox de visibilidade; (b) como
título da seção no popup de clique no mapa. Um nome técnico como `"IQS (Qualidade do Solo)"` pode
ser suficientemente claro, mas um nome como `"Declividade (Original)"` pode gerar dúvida — original
em relação a quê?

### Estado atual

| Categoria | ID interno da camada | Nome atual | Aprovado? | Sugestão / Correção |
|---|---|---|---|---|
| Semiárido PB | `municipios_pb_semiarido` | Municípios | | |
| Índices de Qualidade | `iqs_sab_pb` | IQS (Qualidade do Solo) | | |
| Índices de Qualidade | `iqc_sab_pb` | IQC (Capacidade do Solo) | | |
| Declividade | `declividade_sab_pb_original` | Declividade (Original) | | |
| Declividade | `declividade_sab_pb_pesos` | Declividade (Pesos) | | |
| Geologia | `geologia_sab_pb_original` | Geologia (Original) | | |
| Geologia | `geologia_sab_pb_pesos` | Geologia (Pesos) | | |
| Solos | `solos_tipos_sab_pb_original` | Tipos de Solos (Original) | | |
| Solos | `solos_tipos_sab_pb_pesos` | Tipos de Solos (Pesos) | | |
| Solos | `textura_sab_pb_original` | Textura do Solo (Original) | | |
| Solos | `textura_sab_pb_pesos` | Textura do Solo (Pesos) | | |
| Agroclimatologia | `eto_sab_pb_original` | Evapotranspiração (ETo) | | |
| Agroclimatologia | `eto_sab_pb_pesos` | Evapotranspiração (Pesos) | | |
| Agroclimatologia | `ia_sab_pb_original` | Índice de Aridez (IA) | | |
| Agroclimatologia | `ia_sab_pb_pesos` | Índice de Aridez (Pesos) | | |
| Agroclimatologia | `precipitacao_sab_pb_original` | Precipitação Pluviométrica | | |
| Agroclimatologia | `precipitacao_sab_pb_pesos` | Precipitação (Pesos) | | |

### Perguntas adicionais

**2.1** O sufixo "(Original)" indica os dados brutos/classificados antes da atribuição de pesos?
Se sim, há um termo mais preciso que deva ser adotado (ex.: "Classificada", "Bruta", "Por Classe")?

> [ PREENCHER ]

**2.2** O sufixo "(Pesos)" é suficientemente claro para o público-alvo? Há uma denominação mais
adequada (ex.: "Ponderada", "Normalizada")?

> [ PREENCHER ]

---

---

## 3. Descrição Resumida de Cada Camada (Metadado)

### Por que isso importa

Cada camada possui um campo `meta` — uma frase curta (até ~60 caracteres) exibida abaixo do nome
no menu lateral. Serve para contextualizar o usuário sobre o que está ativando, sem que precise
abrir o popup ou clicar no mapa. Funciona como a legenda de uma figura científica.

### Estado atual e solicitação de revisão

Preencha a coluna **"Descrição Aprovada / Revisada"** com o texto definitivo. Se o texto atual
estiver correto, repita-o.

| Camada | Descrição atual | Descrição Aprovada / Revisada |
|---|---|---|
| Municípios | Limites municipais do semiárido paraibano | |
| IQS (Qualidade do Solo) | Índice de Qualidade do Solo | |
| IQC (Capacidade do Solo) | Índice de Capacidade de Carga | |
| Declividade (Original) | Classes de declividade em % | |
| Declividade (Pesos) | Pesos atribuídos à declividade | |
| Geologia (Original) | Formações litológicas e rochas | |
| Geologia (Pesos) | Pesos atribuídos às formações rochosas | |
| Tipos de Solos (Original) | Classificação pedológica (SiBCS) | |
| Tipos de Solos (Pesos) | Pesos atribuídos aos tipos de solo | |
| Textura do Solo (Original) | Grupamento de textura física | |
| Textura do Solo (Pesos) | Pesos atribuídos à textura do solo | |
| Evapotranspiração (ETo) | Evapotranspiração de referência acumulada | |
| Evapotranspiração (Pesos) | Pesos atribuídos à ETo regional | |
| Índice de Aridez (IA) | Índice de aridez meteorológica | |
| Índice de Aridez (Pesos) | Pesos atribuídos ao Índice de Aridez | |
| Precipitação Pluviométrica | Precipitação média anual acumulada | |
| Precipitação (Pesos) | Pesos atribuídos às faixas de chuva | |

---

---

## 4. Visibilidade Padrão das Camadas na Interface

### Por que isso importa

Ao abrir a aplicação, algumas camadas já aparecem visíveis no mapa (estado `active: true`). Carregar
muitas camadas ao mesmo tempo degrada a performance e confunde o usuário. A definição de quais
camadas devem estar ativas por padrão é uma decisão editorial — cabe à equipe de dados definir
qual é o "ponto de entrada" mais adequado para o usuário.

### Estado atual

| Camada | Visível ao abrir? | Aprovado? | Deve ficar visível? |
|---|---|---|---|
| Municípios | ✅ Sim | | |
| IQS (Qualidade do Solo) | ✅ Sim | | |
| IQC (Capacidade do Solo) | ❌ Não | | |
| Declividade (Original) | ❌ Não | | |
| Declividade (Pesos) | ❌ Não | | |
| Geologia (Original) | ❌ Não | | |
| Geologia (Pesos) | ❌ Não | | |
| Tipos de Solos (Original) | ❌ Não | | |
| Tipos de Solos (Pesos) | ❌ Não | | |
| Textura do Solo (Original) | ❌ Não | | |
| Textura do Solo (Pesos) | ❌ Não | | |
| Evapotranspiração (ETo) | ❌ Não | | |
| Evapotranspiração (Pesos) | ❌ Não | | |
| Índice de Aridez (IA) | ❌ Não | | |
| Índice de Aridez (Pesos) | ❌ Não | | |
| Precipitação Pluviométrica | ❌ Não | | |
| Precipitação (Pesos) | ❌ Não | | |

### Perguntas adicionais

**4.1** Há camadas que **não devem aparecer na interface** (seja temporariamente ou
definitivamente)? Se sim, quais e por quê?

> [ PREENCHER ]

**4.2** Há camadas previstas no GeoPackage que ainda **não estão cadastradas** na interface e
deveriam estar?

> [ PREENCHER ]

---

---

## 5. Significado dos Campos de Cada Camada

### Por que isso importa

Cada feição (polígono) no mapa possui atributos — colunas da tabela de atributos do GeoPackage.
Os nomes desses campos são técnicos/abreviados (ex.: `GLO_DS_LIT`, `PesosX10Ve`) e não são
legíveis pelo usuário final.

Esses rótulos legíveis são usados:
1. Na coluna esquerda do **popup** que aparece ao clicar em uma feição no mapa
2. Na **barra de busca**, como indicação do campo que está sendo filtrado

Preencha a coluna **"Descrição para o Usuário"** com o nome que deve aparecer na interface.

---

### 5.1 Municípios (`municipios_pb_semiarido`)

| Campo (técnico) | Tipo | Descrição para o Usuário | Observações |
|---|---|---|---|
| `nm_municip` | texto | | |
| `cod_ibge_m` | texto | | |
| `slug` | texto | | campo interno — confirmar se deve aparecer na interface |

---

### 5.2 IQS — Qualidade do Solo (`iqs_sab_pb`)

| Campo (técnico) | Tipo | Descrição para o Usuário | Observações |
|---|---|---|---|
| `IQS` | número | | |

---

### 5.3 IQC — Capacidade de Carga (`iqc_sab_pb`)

| Campo (técnico) | Tipo | Descrição para o Usuário | Observações |
|---|---|---|---|
| `IQC_Pes` | número | | |

---

### 5.4 Declividade — Classes originais (`declividade_sab_pb_original`)

| Campo (técnico) | Tipo | Descrição para o Usuário | Observações |
|---|---|---|---|
| `DN` | número | | ex.: "Número Digital", "Classe de Declividade (%)"? |

---

### 5.5 Declividade — Pesos (`declividade_sab_pb_pesos`)

| Campo (técnico) | Tipo | Descrição para o Usuário | Observações |
|---|---|---|---|
| `PesDecl` | número | | |
| `PesosX10Ve` | número | | o que representa o fator x10? |

---

### 5.6 Geologia — Classificação original (`geologia_sab_pb_original`)

| Campo (técnico) | Tipo | Descrição para o Usuário | Observações |
|---|---|---|---|
| `GLO_DS_LIT` | texto | | ex.: "Descrição Litológica"? |

---

### 5.7 Geologia — Pesos (`geologia_sab_pb_pesos`)

| Campo (técnico) | Tipo | Descrição para o Usuário | Observações |
|---|---|---|---|
| `GLO_DS_LIT` | texto | | idem 5.6 |
| `pes_Peso` | número | | |

---

### 5.8 Tipos de Solos — Classificação original (`solos_tipos_sab_pb_original`)

| Campo (técnico) | Tipo | Descrição para o Usuário | Observações |
|---|---|---|---|
| `DSC_COMPON` | texto | | ex.: "Componente Pedológico", "Tipo de Solo (SiBCS)"? |

---

### 5.9 Tipos de Solos — Pesos (`solos_tipos_sab_pb_pesos`)

| Campo (técnico) | Tipo | Descrição para o Usuário | Observações |
|---|---|---|---|
| `DSC_COMPON` | texto | | idem 5.8 |
| `TipSoilPes` | número | | |

---

### 5.10 Textura do Solo — Classificação original (`textura_sab_pb_original`)

| Campo (técnico) | Tipo | Descrição para o Usuário | Observações |
|---|---|---|---|
| `DSC_TEXTUR` | texto | | ex.: "Classe de Textura"? |

---

### 5.11 Textura do Solo — Pesos (`textura_sab_pb_pesos`)

| Campo (técnico) | Tipo | Descrição para o Usuário | Observações |
|---|---|---|---|
| `DSC_TEXTUR` | texto | | idem 5.10 |
| `SoilTextur` | número | | qual é o valor numérico representado? peso? índice? |

---

### 5.12 Evapotranspiração de Referência — Original (`eto_sab_pb_original`)

| Campo (técnico) | Tipo | Descrição para o Usuário | Observações |
|---|---|---|---|
| `ETo_Climat` | número | | unidade? (mm/ano, mm/mês?) |

---

### 5.13 Evapotranspiração de Referência — Pesos (`eto_sab_pb_pesos`)

| Campo (técnico) | Tipo | Descrição para o Usuário | Observações |
|---|---|---|---|
| `ETo_Pesos` | número | | |

---

### 5.14 Índice de Aridez — Original (`ia_sab_pb_original`)

| Campo (técnico) | Tipo | Descrição para o Usuário | Observações |
|---|---|---|---|
| `IA_climat` | número | | adimensional? qual metodologia (Thornthwaite, UNEP)? |

---

### 5.15 Índice de Aridez — Pesos (`ia_sab_pb_pesos`)

| Campo (técnico) | Tipo | Descrição para o Usuário | Observações |
|---|---|---|---|
| `IA_Pesos` | número | | |

---

### 5.16 Precipitação Pluviométrica — Original (`precipitacao_sab_pb_original`)

| Campo (técnico) | Tipo | Descrição para o Usuário | Observações |
|---|---|---|---|
| `Clim_Prec` | número | | unidade? (mm/ano?) período de referência? |

---

### 5.17 Precipitação Pluviométrica — Pesos (`precipitacao_sab_pb_pesos`)

| Campo (técnico) | Tipo | Descrição para o Usuário | Observações |
|---|---|---|---|
| `Pesos_Prec` | número | | |

---

---

## 6. Campos para Busca e Popup

### Por que isso importa

A interface possui dois mecanismos de acesso aos atributos das feições:

**Barra de busca:** permite ao usuário digitar um valor e encontrar polígonos que correspondam
(ex.: buscar por nome de município ou por faixa de IQS). A busca funciona sobre os campos
declarados em `searchFields`. Campos numéricos aceitam operadores como `> 0.5` ou `= 3`.

**Popup de clique:** ao clicar em qualquer ponto do mapa, exibe os atributos das feições ativas
sob aquele ponto. Apenas os campos declarados em `popUpFields` são exibidos, na ordem declarada.

Nem sempre faz sentido expor todos os campos — alguns são identificadores internos, outros são
redundantes ou sem significado para o usuário final.

### Solicitação

Para cada camada, indique quais campos devem ser usados em cada mecanismo. Use `✅` para incluir
e `❌` para excluir. Caso um campo deva aparecer com nome diferente no popup, indique na coluna
"Rótulo no popup".

---

### 6.1 Municípios

| Campo | Busca? | Popup? | Rótulo no popup |
|---|---|---|---|
| `nm_municip` | ✅ (atual) | ✅ (atual) | |
| `cod_ibge_m` | | ✅ (atual) | |
| `slug` | | | campo interno — ocultar? |

---

### 6.2 IQS — Qualidade do Solo

| Campo | Busca? | Popup? | Rótulo no popup |
|---|---|---|---|
| `IQS` | ✅ (atual) | ✅ (atual) | |

---

### 6.3 IQC — Capacidade de Carga

| Campo | Busca? | Popup? | Rótulo no popup |
|---|---|---|---|
| `IQC_Pes` | ✅ (atual) | ✅ (atual) | |

---

### 6.4 Declividade (Original)

| Campo | Busca? | Popup? | Rótulo no popup |
|---|---|---|---|
| `DN` | ✅ (atual) | ✅ (atual) | |

---

### 6.5 Declividade (Pesos)

| Campo | Busca? | Popup? | Rótulo no popup |
|---|---|---|---|
| `PesDecl` | ✅ (atual) | ✅ (atual) | |
| `PesosX10Ve` | ✅ (atual) | ✅ (atual) | |

---

### 6.6 Geologia (Original)

| Campo | Busca? | Popup? | Rótulo no popup |
|---|---|---|---|
| `GLO_DS_LIT` | ✅ (atual) | ✅ (atual) | |

---

### 6.7 Geologia (Pesos)

| Campo | Busca? | Popup? | Rótulo no popup |
|---|---|---|---|
| `GLO_DS_LIT` | ✅ (atual) | ✅ (atual) | |
| `pes_Peso` | ✅ (atual) | ✅ (atual) | |

---

### 6.8 Tipos de Solos (Original)

| Campo | Busca? | Popup? | Rótulo no popup |
|---|---|---|---|
| `DSC_COMPON` | ✅ (atual) | ✅ (atual) | |

---

### 6.9 Tipos de Solos (Pesos)

| Campo | Busca? | Popup? | Rótulo no popup |
|---|---|---|---|
| `DSC_COMPON` | ✅ (atual) | ✅ (atual) | |
| `TipSoilPes` | ✅ (atual) | ✅ (atual) | |

---

### 6.10 Textura do Solo (Original)

| Campo | Busca? | Popup? | Rótulo no popup |
|---|---|---|---|
| `DSC_TEXTUR` | ✅ (atual) | ✅ (atual) | |

---

### 6.11 Textura do Solo (Pesos)

| Campo | Busca? | Popup? | Rótulo no popup |
|---|---|---|---|
| `DSC_TEXTUR` | ✅ (atual) | ✅ (atual) | |
| `SoilTextur` | ✅ (atual) | ✅ (atual) | |

---

### 6.12 Evapotranspiração (ETo)

| Campo | Busca? | Popup? | Rótulo no popup |
|---|---|---|---|
| `ETo_Climat` | ✅ (atual) | ✅ (atual) | |

---

### 6.13 Evapotranspiração (Pesos)

| Campo | Busca? | Popup? | Rótulo no popup |
|---|---|---|---|
| `ETo_Pesos` | ✅ (atual) | ✅ (atual) | |

---

### 6.14 Índice de Aridez (IA)

| Campo | Busca? | Popup? | Rótulo no popup |
|---|---|---|---|
| `IA_climat` | ✅ (atual) | ✅ (atual) | |

---

### 6.15 Índice de Aridez (Pesos)

| Campo | Busca? | Popup? | Rótulo no popup |
|---|---|---|---|
| `IA_Pesos` | ✅ (atual) | ✅ (atual) | |

---

### 6.16 Precipitação Pluviométrica

| Campo | Busca? | Popup? | Rótulo no popup |
|---|---|---|---|
| `Clim_Prec` | ✅ (atual) | ✅ (atual) | |

---

### 6.17 Precipitação (Pesos)

| Campo | Busca? | Popup? | Rótulo no popup |
|---|---|---|---|
| `Pesos_Prec` | ✅ (atual) | ✅ (atual) | |

---

---

## 7. Observações Gerais

Utilize este espaço para registrar qualquer informação que não se encaixe nas seções anteriores:
inconsistências nos dados, camadas em processo de atualização, campos com valores desconhecidos,
ou qualquer outra observação relevante para o desenvolvimento da interface.

> [ PREENCHER ]

---

*Documento gerado a partir do estado atual de `src/config/layers.js` — versão do repositório: branch `main`.*
