#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Conferência comparativa entre um capítulo original e sua versão revisada.

Uso: python3 build/compara_capitulo.py NN
Compara manuscrito/V1_original_preservado/NN.md com manuscrito/V1_revisao_linguagem/NN.md e
lista: palavras, quebras de cena, título, números (algarismos e por extenso), nomes próprios e
trechos entre aspas que aparecem só de um lado. Serve para achar perdas acidentais de informação.
"""
import re, sys, collections

BASE = "/home/user/LTKG/manuscrito"
NUM_WORDS = ("zero um uma dois duas três quatro cinco seis sete oito nove dez onze doze treze "
             "catorze quatorze quinze dezesseis dezessete dezoito dezenove vinte trinta quarenta "
             "cinquenta sessenta setenta oitenta noventa cem cento duzentos duzentas trezentos "
             "trezentas quatrocentos quatrocentas quinhentos quinhentas seiscentos seiscentas "
             "setecentos oitocentos novecentos mil milhão milhões meio meia metade dobro triplo "
             "primeiro primeira segundo segunda terceiro terceira quarto quarta quinto quinta "
             "sexto sexta sétimo sétima oitavo oitava nono nona décimo décima vigésimo").split()
NUM_SET = set(NUM_WORDS)
# palavras capitalizadas comuns em início de frase que não são nomes
STOP = set("""A O As Os Um Uma Uns Umas E Mas Era Eram Foi Não Sim Ele Ela Eles Elas Eu Você Vocês
Nós Isso Isto Aquilo Esse Essa Este Esta Aquele Aquela Depois Antes Quando Onde Como Que Quem Por
Para Pelo Pela Com Sem Se Na No Nas Nos Da Do Das Dos De Em Ao Aos À Às Mais Menos Muito Tudo Nada
Ninguém Alguém Já Ainda Também Só Então Agora Hoje Ontem Amanhã Aqui Ali Lá Talvez Porque Senhor
Senhora Tinha Tem Há Houve Estava Está Estou Vou Vai Ia Fez Faz Disse Deu Pôs Olhou Ficou Saiu
Entrou Voltou Era É Seria Será Pode Podia Quer Queria Sabe Sabia Sei Acho Achou Viu Vejo Ouviu
Tirou Abriu Fechou Pegou Levou Chegou Subiu Desceu Mesmo Mesma Outro Outra Cada Todo Toda Todos
Todas Algum Alguma Nenhum Nenhuma Qual Quais Quanto Quantos Meu Minha Seu Sua Dele Dela Nosso
Nossa Primeiro Primeira Bom Boa Certo Claro Obrigado Obrigada Ah Oh Ei Hum Bem Pois Até Entre
Sobre Sob Contra Desde Durante Enquanto Embora Mesmo Assim Porém Ou Nem Aliás Afinal Logo Cedo
Tarde Sempre Nunca Jamais Quase Apenas Somente Devagar Rápido Longe Perto Dentro Fora Cima Baixo
Atrás Frente Lado Meio Parte Fim Começo Vez Vezes Dia Noite Manhã Hora Horas Minutos Anos Ano""".split())

def load(path):
    return open(path, encoding="utf-8").read()

def words(t):
    return re.findall(r"[\wÀ-ÿ'-]+", t)

def numbers(t):
    digits = collections.Counter(re.findall(r"\d[\d.,]*", t))
    low = [w.lower() for w in words(t)]
    nw = collections.Counter(w for w in low if w in NUM_SET)
    return digits, nw

def names(t):
    c = collections.Counter()
    for m in re.finditer(r"(?<![\wÀ-ÿ])([A-ZÁÉÍÓÚÂÊÔÃÕÇ][\wÀ-ÿ'-]+)", t):
        w = m.group(1)
        if w in STOP:
            continue
        c[w] += 1
    return c

def quotes(t):
    return collections.Counter(re.findall(r"\"([^\"]{3,})\"", t))

def diff(name, a, b, show_counts=True):
    only_a = {k: v for k, v in a.items() if k not in b}
    only_b = {k: v for k, v in b.items() if k not in a}
    changed = {k: (a[k], b[k]) for k in a if k in b and a[k] != b[k]}
    print(f"\n## {name}")
    if only_a:
        print("  só no ORIGINAL:", ", ".join(f"{k}×{v}" for k, v in sorted(only_a.items())))
    if only_b:
        print("  só no REVISADO:", ", ".join(f"{k}×{v}" for k, v in sorted(only_b.items())))
    if show_counts and changed:
        print("  contagem mudou:", ", ".join(f"{k} {x}→{y}" for k, (x, y) in sorted(changed.items())))
    if not (only_a or only_b or (show_counts and changed)):
        print("  idêntico")

def main():
    nn = sys.argv[1].zfill(2)
    a = load(f"{BASE}/V1_original_preservado/{nn}.md")
    b = load(f"{BASE}/V1_revisao_linguagem/{nn}.md")
    wa, wb = len(words(a)), len(words(b))
    print(f"# Capítulo {nn}")
    print(f"palavras: {wa} → {wb} ({(wb-wa)/wa*100:+.1f}%)")
    print("título:", "OK" if a.split("\n")[0] == b.split("\n")[0] else f"DIFERENTE: {a.splitlines()[0]!r} × {b.splitlines()[0]!r}")
    sa = len(re.findall(r"^---\s*$", a, re.M)); sb = len(re.findall(r"^---\s*$", b, re.M))
    print(f"quebras de cena: {sa} → {sb}", "OK" if sa == sb else "DIFERENTE")
    pa = len([p for p in re.split(r"\n\s*\n", a) if p.strip()]); pb = len([p for p in re.split(r"\n\s*\n", b) if p.strip()])
    print(f"parágrafos: {pa} → {pb}")
    da, na = numbers(a); db, nb = numbers(b)
    diff("algarismos", da, db)
    diff("números por extenso", na, nb)
    diff("nomes próprios / capitalizados", names(a), names(b), show_counts=False)
    diff("trechos entre aspas (documentos/citações)", quotes(a), quotes(b), show_counts=False)

if __name__ == "__main__":
    main()
