import sys; sys.path.insert(0, "/home/user/LTKG/build/edicao")
from mapas import *
from especiais import CSS_ESP
E = "exportacoes/banco_de_arte/11_edicao"
ims = {1: f"{E}/C02-2.png", 2: f"{E}/C22-0.png", 3: f"{E}/C09-0.png", 4: f"{E}/C03-3.png", 5: f"{E}/C08-0.png", 6: f"{E}/C04-0.png", 7: f"{E}/C15-2.png",
       8: f"{E}/C15-1.png", 9: f"{E}/C02-0.png", 10: f"{E}/C01-b.png", 11: f"{E}/C05-0.png", 12: f"{E}/C12-1.png", 13: f"{E}/C13-1.png", 14: f"{E}/C12-0.png"}
p = compor([pagina_mapa(planta_vhalessa()), legenda_vhalessa(ims), pagina_mapa(mapa_norte()), pagina_mapa(mapa_aresta())], [],
           "/tmp/claude-0/-home-user-LTKG/0ae43a17-9955-54f0-9172-040bd4d1f0e3/scratchpad/mapas.pdf", extra_css=CSS_ESP + CSS_MAPA)
