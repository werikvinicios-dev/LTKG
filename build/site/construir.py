"""Gera os dados e os recursos do site imersivo "Leis para Matar Deuses" em exportacoes/site/.
Texto: manuscrito/V2. Arte, partes e posições das ilustrações: build/edicao/montar_edicao.py (a mesma edição imersiva).
Peças da logo e das leis: recortadas como no trailer (build/trailer/cenas.py). Nada vem das pastas de spoiler.
Uso: python3 build/site/construir.py [--sem-midia]"""
import json, os, re, subprocess, sys, hashlib
import numpy as np
from PIL import Image

ROOT = "/home/user/LTKG"
OUT = f"{ROOT}/exportacoes/site"
sys.path.insert(0, f"{ROOT}/build/edicao")
sys.path.insert(0, f"{ROOT}/build/trailer")
import montar_edicao as ME
import especiais as ESP
import mapas as MP

os.makedirs(f"{OUT}/img", exist_ok=True)
for d in ("data", "pecas", "mapas", "midia", "fontes"):
    os.makedirs(f"{OUT}/{d}", exist_ok=True)
_FEITAS = {}


def webp(caminho, larg=1500, q=74, nome=None):
    """Converte uma imagem do projeto para WebP (uma vez só) e devolve o caminho publicado."""
    p = caminho if os.path.isabs(caminho) else f"{ROOT}/{caminho}"
    if p in _FEITAS:
        return _FEITAS[p]
    base = nome or (os.path.splitext(os.path.basename(p))[0][:40] + "-" + hashlib.md5(p.encode()).hexdigest()[:6])
    dst = f"img/{base}.webp"
    if not os.path.exists(f"{OUT}/{dst}"):
        im = Image.open(p)
        im = im.convert("RGBA" if im.mode in ("RGBA", "LA", "P") else "RGB")
        if im.width > larg:
            im = im.resize((larg, round(im.height * larg / im.width)), Image.LANCZOS)
        im.save(f"{OUT}/{dst}", "WEBP", quality=q, method=6)
    w, h = Image.open(f"{OUT}/{dst}").size
    _FEITAS[p] = {"src": dst, "w": w, "h": h}
    return _FEITAS[p]


def inline(t):
    """Marcação mínima do manuscrito para HTML seguro: escapa e converte *itálico*."""
    t = t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return re.sub(r"\*([^*]+)\*", r"<em>\1</em>", t)


# ------------------------------------------------------------------ o livro
def livro():
    partes = []
    for num, tit, c0, c1, epi, fonte, im, pos in ME.PARTES:
        partes.append({"num": num, "titulo": tit, "de": c0, "ate": c1, "epigrafe": epi, "lei": fonte, "img": webp(im, 1800), "pos": pos})
    caps = []
    textos = {}
    for n in range(1, 32):
        rot, titulo, corpo = ME.ler_capitulo(n)
        pl = ME.PLANO.get(n, {})
        abertura, bandas, finais = ME.ARTE[n]
        blocos_md = [b.strip() for b in corpo.strip().split("\n\n") if b.strip()]
        ins = {}
        alvos = [i for i in pl.get("ilustracoes", []) if i["tipo"] in ("dupla", "spot")]
        for k, b in enumerate(bandas):
            tr = alvos[k]["trecho_ancora"] if k < len(alvos) else ""
            i = ME.achar_paragrafo(blocos_md, tr, .45 + .2 * k)
            ins.setdefault(i, []).append({"t": "img", "img": webp(ME.arq(b), 1600)})
        for d in pl.get("documentos_do_mundo", [])[:2]:
            i = ME.achar_paragrafo(blocos_md, d.get("onde_entra", ""), .3)
            ins.setdefault(i, []).append({"t": "doc", "tipo": d.get("tipo", ""), "x": inline(d.get("conteudo", ""))})
        blocos, puro = [], []
        for i, b in enumerate(blocos_md):
            if b.strip() == "---":
                blocos.append({"t": "sep"})
            elif b.startswith("#"):
                blocos.append({"t": "h", "x": inline(b.lstrip("# ").strip())})
            else:
                blocos.append({"t": "p", "x": inline(" ".join(b.split("\n")))})
                puro.append(b)
            blocos += ins.get(i, [])
        texto = "\n".join(puro)
        textos[n] = texto
        parte = next(p["num"] for p in partes if p["de"] <= n <= p["ate"])
        caps.append({"n": n, "rotulo": rot, "titulo": titulo, "parte": parte, "pov": pl.get("pov", ""),
                     "abertura": webp(ME.arq(abertura), 1600), "finais": [webp(ME.arq(f), 1600) for f in finais],
                     "epigrafe": inline(pl.get("epigrafe_sugerida") or ""), "respiro": inline(pl.get("citacao_respiro") or ""),
                     "palavras": len(re.findall(r"\w+", texto)), "resumo": pl.get("resumo", ""), "blocos": blocos})
    obra = {"titulo": "Leis para Matar Deuses", "volume": "Volume I", "autor": "Werik Martins", "partes": partes,
            "capitulos": [{k: v for k, v in c.items() if k not in ("blocos", "resumo")} for c in caps]}
    json.dump(obra, open(f"{OUT}/data/obra.json", "w"), ensure_ascii=False, separators=(",", ":"))
    for c in caps:
        json.dump({"n": c["n"], "blocos": c["blocos"]}, open(f"{OUT}/data/cap{c['n']:02d}.json", "w"), ensure_ascii=False, separators=(",", ":"))
    # resumos só aparecem depois de o capítulo ser lido (anti-spoiler)
    json.dump({c["n"]: c["resumo"] for c in caps}, open(f"{OUT}/data/resumos.json", "w"), ensure_ascii=False, separators=(",", ":"))
    return caps, textos


def primeira_mencao(textos, termos):
    for n in range(1, 32):
        t = textos[n].lower()
        if any(x.lower() in t for x in termos):
            return n
    return 31


# ------------------------------------------------------------------ o Registro (anti-spoiler: cada verbete abre no capítulo em que aparece)
def registro(textos):
    SIM = ESP.SIM
    leis = [{"num": r, "nome": n, "id": k, "frase": x, "img": webp(f"{SIM}/leis/{k}_decorativa.png", 520)} for r, n, k, x in ESP.LEIS]
    disc = [{"nome": n, "id": k, "faz": x, "cor": c, "img": webp(f"{SIM}/disciplinas/{k}_decorativa.png", 520)} for n, k, x, c in ESP.DISC]
    etapas = [("Fonte", "fonte", "de onde sai"), ("Selo", "ancora", "onde se prende"), ("Vínculo", "elo", "por onde passa"),
              ("Destino", "destino", "para onde vai"), ("Controle", "controle", "quem segura"), ("Retorno", "retorno", "o que volta")]
    etapas = [{"nome": n, "x": x, "img": webp(f"{SIM}/etapas_transposicao/{k}_decorativa.png", 420)} for n, k, x in etapas]
    glos = [{"termo": t, "x": x, "cap": primeira_mencao(textos, [t.split(",")[0].split(" de ")[0]])} for t, x in ME.GLOSSARIO]
    elenco = [{"nome": n, "x": x, "img": webp(p, 900), "cap": primeira_mencao(textos, [n.split()[0]])} for n, p, x in ME.ELENCO]
    lugares, vistos = [], set()
    for n in range(1, 32):
        for l in ME.PLANO.get(n, {}).get("locais", []):
            nome = l.get("nome", "").strip()
            if not nome or nome.lower() in vistos:
                continue
            vistos.add(nome.lower())
            lugares.append({"nome": nome, "onde": l.get("cidade_ou_regiao", ""), "x": l.get("descricao_fisica", ""), "cap": n})
    json.dump({"leis": leis, "disciplinas": disc, "etapas": etapas, "glossario": glos, "elenco": elenco, "lugares": lugares},
              open(f"{OUT}/data/registro.json", "w"), ensure_ascii=False, separators=(",", ":"))


# ------------------------------------------------------------------ Atlas (mapas vetoriais da edição) e Galeria
def atlas():
    mapas = []
    for nome, f, tit in (("aresta", MP.mapa_aresta, "Aresta, o continente"), ("norte", MP.mapa_norte, "Os Reinos do Norte"),
                         ("vhalessa", MP.planta_vhalessa, "Vhalessa, planta da cidade")):
        h = f()
        m = re.search(r"<svg.*</svg>", h, re.S)
        if not m:
            continue
        svg = m.group(0)
        svg = re.sub(r'\swidth="[^"]+mm"', "", svg, count=1); svg = re.sub(r'\sheight="[^"]+mm"', "", svg, count=1)
        open(f"{OUT}/mapas/{nome}.svg", "w").write(svg)
        mapas.append({"id": nome, "titulo": tit, "src": f"mapas/{nome}.svg"})
    return mapas


def galeria():
    BA = f"{ROOT}/exportacoes/banco_de_arte"
    itens = []
    for pasta, grupo in (("06_personagens", "Rostos"), ("05_mundo", "Lugares"), ("04_objetos", "Objetos"), ("03_faccoes", "Casas e ordens")):
        for f in sorted(os.listdir(f"{BA}/{pasta}")):
            if not f.endswith(".png"):
                continue
            leg = re.sub(r"^[A-Z]{2}-\d+_", "", f[:-4]).replace("_", " ")
            itens.append({"grupo": grupo, "leg": leg[:1].upper() + leg[1:], "img": webp(f"{BA}/{pasta}/{f}", 1400)})
    return itens


# ------------------------------------------------------------------ peças animadas: a logo do trailer e as sete leis
def salvar_peca(rgba, nome, fator=1.0):
    a = (np.clip(rgba, 0, 1) * 255).astype(np.uint8)
    ys, xs = np.nonzero(a[..., 3] > 2)
    if not len(xs):
        return None
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    im = Image.fromarray(a[y0:y1, x0:x1], "RGBA")
    if fator != 1:
        im = im.resize((max(1, round(im.width * fator)), max(1, round(im.height * fator))), Image.LANCZOS)
    im.save(f"{OUT}/pecas/{nome}.webp", "WEBP", quality=82, method=6)
    return {"src": f"pecas/{nome}.webp", "x": int(x0), "y": int(y0), "w": int(x1 - x0), "h": int(y1 - y0)}


def pecas():
    import base as B, cenas as C
    B.formato(1920, 1080)
    pc = C.pecas_emblema()
    emb = {k: salvar_peca(pc[k], f"emb_{k}") for k in ("halo", "arco_e", "arco_d", "estandarte", "travessao", "prato_e", "prato_d", "eixo", "coroa")}
    emb["perolas"] = [salvar_peca(p, f"emb_perola{i}") for i, p in enumerate(pc["perolas"])]
    emb["ganchos"] = pc["ganchos"]; emb["pivo"] = C.PIVO; emb["ponta"] = C.PONTA; emb["tam"] = 1024
    glifos, centros, filete, sub = C.letras_titulo()
    let = {"glifos": [dict(salvar_peca(g, f"let_{i}"), cx=float(c[0]), cy=float(c[1])) for i, (g, c) in enumerate(zip(glifos, centros))],
           "filete": salvar_peca(filete, "let_filete"), "sub": salvar_peca(sub, "let_sub"), "tam": [1024, 410]}
    leis = {}
    for k, _ in C.LEIS:
        P = C.pecas_lei(k)
        h, w = P["hw"]
        leis[k] = {"tam": [w, h], "ax": float(P["ax"]), "cen": [float(v) for v in P["cen"]],
                   "eixo": salvar_peca(P["eixo"], f"lei_{k}_eixo", .6), "estrutura": salvar_peca(P["estrutura"], f"lei_{k}_estrutura", .6),
                   "pecas": [dict(salvar_peca(c, f"lei_{k}_p{j}", .6), tipo=tp) for j, (tp, c, _) in enumerate(P["pecas"])]}
    selo = C.selo_ordem()
    Image.fromarray((np.clip(selo, 0, 1) * 255).astype(np.uint8), "RGBA").resize((520, round(520 * selo.shape[0] / selo.shape[1])), Image.LANCZOS) \
        .save(f"{OUT}/pecas/selo_ordem.webp", "WEBP", quality=84)
    return {"emblema": emb, "letreiro": let, "leis": leis, "fator_leis": .6}


# ------------------------------------------------------------------ fontes, trailer e sons
def fontes():
    from fontTools.ttLib import TTFont
    for src, dst in (("ArestaTitular-Regular.ttf", "aresta-titular.woff2"), ("ArestaTitular-Bold.ttf", "aresta-titular-bold.woff2")):
        f = TTFont(f"{ROOT}/build/fonts/{src}"); f.flavor = "woff2"; f.save(f"{OUT}/fontes/{dst}")


def midia():
    T = f"{ROOT}/exportacoes/trailer"
    A = f"{ROOT}/build/trailer/_cache/audio"
    r = lambda *a: subprocess.run(a, check=True)
    r("ffmpeg", "-v", "error", "-y", "-i", f"{T}/LMD_trailer_oficial_96s_1080p.mp4", "-vf", "scale=1280:720", "-c:v", "libx264", "-crf", "26",
      "-maxrate", "1000k", "-bufsize", "2000k", "-preset", "slow", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "112k", "-movflags", "+faststart",
      f"{OUT}/midia/trailer.mp4")
    r("ffmpeg", "-v", "error", "-y", "-ss", "92.6", "-i", f"{T}/LMD_trailer_oficial_96s_1080p.mp4", "-frames:v", "1", "-vf", "scale=1280:720",
      "-q:v", "70", f"{OUT}/midia/trailer.webp")
    # vento de Vhalessa (BigSoundBank 0595, CC0): 32 s em laço sem emenda audível
    r("ffmpeg", "-v", "error", "-y", "-i", f"{ROOT}/build/trailer/_cache/fontes/bsb/0595.flac", "-filter_complex",
      "[0:a]atrim=10:44,asetpts=PTS-STARTPTS[a];[a]asplit[x][y];[x]atrim=0:32[x1];[y]atrim=32:34,asetpts=PTS-STARTPTS[y1];"
      "[x1][y1]acrossfade=d=2[z]", "-map", "[z]", "-ac", "2", "-c:a", "libopus", "-b:a", "64k", f"{OUT}/midia/vento.ogg")
    # tema de leitura: o violoncelo de Vhalessa e a harpa e a flauta de Aurelia, da trilha gravada do trailer
    r("ffmpeg", "-v", "error", "-y", "-i", f"{A}/musica.wav", "-filter_complex",
      "[0:a]atrim=7.5:24.5,asetpts=PTS-STARTPTS[a];[0:a]atrim=57.7:68.2,asetpts=PTS-STARTPTS[b];[a][b]acrossfade=d=2.5[c];"
      "[c]afade=t=in:d=2,loudnorm=I=-22:TP=-3[z]", "-map", "[z]", "-c:a", "libopus", "-b:a", "96k", f"{OUT}/midia/tema.ogg")


if __name__ == "__main__":
    caps, textos = livro()
    registro(textos)
    extra = {"mapas": atlas(), "galeria": galeria(), "pecas": pecas()}
    json.dump(extra, open(f"{OUT}/data/extras.json", "w"), ensure_ascii=False, separators=(",", ":"))
    fontes()
    if "--sem-midia" not in sys.argv:
        midia()
    tot = sum(os.path.getsize(os.path.join(d, f)) for d, _, fs in os.walk(OUT) for f in fs)
    print("ok", len(caps), "capítulos;", sum(len(fs) for _, _, fs in os.walk(OUT)), "arquivos;", round(tot / 1e6, 1), "MB")
