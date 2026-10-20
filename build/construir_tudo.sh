#!/bin/sh
# Regenera todas as saídas da edição de luxo a partir de manuscrito/V1_revisao_linguagem/.
# Requisitos: python3 (reportlab, pyphen, svglib, uharfbuzz, fonttools, Pillow, python-docx),
# pandoc 3, Chromium headless (Playwright). Uso: sh build/construir_tudo.sh
set -e
cd "$(dirname "$0")"
python3 make_logo.py                       # identidade visual (SVG + PNG)
python3 make_pdf_luxo.py                   # PDF de leitura/impressão sem sangria
python3 make_pdf_luxo.py --sangria         # PDF de gráfica, 3 mm de sangria e marcas de corte
PAGINAS=$(python3 -c "from pypdf import PdfReader; n=len(PdfReader('../exportacoes/Leis_para_Matar_Deuses_Vol1_LUXO.pdf').pages); print(n + n % 2)" 2>/dev/null || echo 500)
python3 make_capa_luxo.py "$PAGINAS"       # capa: frente, completa (lombada calculada), capa do EPUB
python3 montar_saidas.py                   # manuscrito MD + DOCX e EPUB de luxo
pdftoppm -f 7 -l 8 -r 110 -png ../exportacoes/Leis_para_Matar_Deuses_Vol1_LUXO.pdf arte/miolo
python3 make_caderno_arte.py               # caderno de arte
echo "pronto."
