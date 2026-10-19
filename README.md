# Leis para Matar Deuses — Volume 1

**Autor:** Werik Martins
**Volume 1:** *O Deus que Caiu do Céu*

Romance integral (≈162.000 palavras, 30 capítulos + epílogo), primeiro volume da saga
de fantasia épica adulta ambientada em **Aresta**.

## Estrutura do repositório

```
manuscrito/capitulos/        Fonte do manuscrito, um arquivo .md por capítulo (01–30 + 31 epílogo)
exportacoes/                 Entregáveis finais
  ├─ Leis_para_Matar_Deuses_Vol1.md     Markdown de leitura (integral)
  ├─ Leis_para_Matar_Deuses_Vol1.docx   Word editável (com sumário)
  ├─ Leis_para_Matar_Deuses_Vol1.epub   EPUB refluível (capa + navegação)
  ├─ Leis_para_Matar_Deuses_Vol1.pdf    PDF de leitura (A5, 589 páginas)
  └─ capa.png                           Capa tipográfica
relatorio/RELATORIO_EDITORIAL.md        Relatório sem spoilers (métricas, auditoria, pendências)
pacote_original/                        Bíblias e prompt originais recebidos
build/                                  Scripts de montagem (capa, PDF) e arquivos intermediários
CONTEM_SPOILERS_NAO_ABRIR_ANTES_DA_LEITURA/   ⚠️ planejamento interno com spoilers — NÃO abrir antes de ler
```

## Aviso ao autor-leitor

A pasta `CONTEM_SPOILERS_NAO_ABRIR_ANTES_DA_LEITURA/` contém a bíblia interna de
autoria (verdade dos mistérios, pistas, continuidade). **Não abra antes de ler o
romance** — as grandes revelações estão guardadas para a experiência de leitura.

## Como reconstruir os entregáveis

```sh
python3 build/make_cover.py                 # gera a capa
pandoc build/manuscrito_completo.md ... \   # DOCX e EPUB (ver histórico de build)
python3 build/make_pdf.py                    # gera o PDF de leitura
```
