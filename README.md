# Leis para Matar Deuses — Volume 1

**Autor:** Werik Martins
**Volume 1:** *O Deus que Caiu do Céu*

Romance integral (30 capítulos + epílogo), primeiro volume da saga de fantasia épica adulta
ambientada em **Aresta**. Esta é a **edição de luxo ilustrada**, com o texto na **versão
revisada de linguagem (V1-RL)**.

## Para ler

| Arquivo | O que é |
|---|---|
| `exportacoes/Leis_para_Matar_Deuses_Vol1_LUXO.pdf` | PDF de luxo, 16 × 23 cm, 500 páginas |
| `exportacoes/Leis_para_Matar_Deuses_Vol1_LUXO.epub` | EPUB 3 de luxo (validado no EpubCheck) |
| `exportacoes/Caderno_de_Arte_Leis_para_Matar_Deuses_Vol1.pdf` | caderno de arte ilustrado, sem spoilers |

## Para editar e imprimir

| Arquivo | O que é |
|---|---|
| `exportacoes/MANUSCRITO_V1_REVISAO_LINGUAGEM.docx` / `.md` | manuscrito integral editável |
| `exportacoes/Leis_para_Matar_Deuses_Vol1_GRAFICA_sangria.pdf` | miolo para gráfica (3 mm de sangria) |
| `exportacoes/capa/` | capa frontal (300 dpi), capa do EPUB, capa completa com lombada |
| `exportacoes/grafico/logo/` | identidade visual da saga (SVG e PNG) |
| `relatorio/RELATORIO_EDITORA_SEM_SPOILERS.md` | relatório da revisão e da edição, sem spoilers |

## Estrutura do repositório

```
manuscrito/capitulos/              Versão canônica V1 (intocada; só substituir com aprovação do autor)
manuscrito/V1_original_preservado/ Cópia de segurança da V1, feita antes da revisão
manuscrito/V1_revisao_linguagem/   V1-RL: fonte de todas as exportações desta edição
exportacoes/                       Entregáveis da edição de luxo
exportacoes/V1_original_antes_da_revisao/  Exportações da V1, guardadas para comparação
relatorio/                         Relatórios sem spoilers (V1 e revisão de linguagem)
pacote_original/                   Bíblias e prompts originais recebidos
build/                             Scripts de composição, fontes (OFL) e arte
CONTEM_SPOILERS_NAO_ABRIR_ANTES_DA_LEITURA/   ⚠️ planejamento, auditorias e registro de continuidade
```

## Aviso ao autor-leitor

A pasta `CONTEM_SPOILERS_NAO_ABRIR_ANTES_DA_LEITURA/` contém a bíblia interna, as notas de
auditoria por capítulo e o registro de continuidade. **Não abra antes de ler o romance.**

## Como reconstruir os entregáveis

```sh
sh build/construir_tudo.sh
```

Etapas: logo → PDF de luxo → PDF de gráfica → capa (lombada calculada pelo número de páginas) →
manuscrito MD/DOCX e EPUB → caderno de arte. Usa reportlab, pandoc, fontTools/HarfBuzz e o
Chromium headless.
