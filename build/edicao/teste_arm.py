import sys; sys.path.insert(0, "/home/user/LTKG/build/edicao")
from armorial import *
from especiais import CSS_ESP
pg = armorial()
from montar_edicao import CSS_LIVRO
compor(pg[:4] + pg[10:12] + pg[-2:], [], "/tmp/claude-0/-home-user-LTKG/0ae43a17-9955-54f0-9172-040bd4d1f0e3/scratchpad/arm.pdf", extra_css=CSS_ESP + CSS_ARM + CSS_LIVRO)
