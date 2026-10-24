"""Bancos de som gravados usados no trailer (todos de uso livre, inclusive comercial).
Baixa o que faltar para _cache/fontes/ e escreve a lista de créditos. Uso: python3 banco.py

- VSCO-2-CE (Versilian Studios Chamber Orchestra, Community Edition): orquestra de câmara gravada, CC0.
- BigSoundBank (Joseph Sardin): efeitos gravados, CC0.
- Kenney RPG Audio e Impact Sounds: foley, CC0.
- OpenGameArt (pacotes CC0): espadas, bainhas e golpes de lâmina.
"""
import os, subprocess

F = "/home/user/LTKG/build/trailer/_cache/fontes"
VSCO = f"{F}/vsco"
PASTAS_VSCO = ["/LICENSE*", "/Strings/Cello Section/susvib/", "/Strings/Cello Section/spic/", "/Strings/Cello Section/trem/",
               "/Strings/Viola Section/susvib/", "/Strings/Violin Section/susVib/", "/Strings/Violin Section/Spic/",
               "/Strings/Violin Section/Trem/", "/Strings/Solo Contrabass/SusVib/", "/Strings/Solo Contrabass/Spic/",
               "/Strings/Harp/", "/Brass/F Horn/sus/", "/Brass/Tenor Trombone/sus/", "/Brass/Tuba/sus/", "/Brass/Trumpet/sus/",
               "/Woodwinds/Flute/susNV/", "/Percussion/*.wav", "/Percussion/Timpani/", "/Percussion/Glock/"]

# BigSoundBank: número → (nome, uso no trailer)
BSB = {
    "0595": ("Wind", "vento de fundo"), "0625": ("Strong Wind in a Village", "nevasca e rajadas"),
    "0830": ("1 church bell", "sino ao longe em Vhalessa"), "0135": ("Church Bell", "sino ao longe"),
    "1383": ("Drops, metal sink", "gota no aço"), "1382": ("Drops, metal pan", "gota no aço"),
    "0725": ("Instrument string", "fio sob tensão"), "0554": ("Rope", "tensão do fio"), "3426": ("Big rope", "tensão do fio"),
    "0128": ("Sword Through the Air", "golpes de ar"), "0129": ("Sword", "espada"), "0127": ("Sword That Cuts", "espada"),
    "0833": ("Sharpening knife against knife", "gravação no metal"), "0832": ("Whetstone", "gravação na pedra"),
    "3322": ("Fire, Foley", "Igneo, brasas"), "2131": ("Cigarette, Ignition", "ignição de calor"),
    "0164": ("Turned Page", "papel"), "0785": ("Paper", "papel"), "1588": ("Gavel, 1 blow", "sentença, livro"),
    "1567": ("Grandfather clock, ticking", "engrenagens"), "0007": ("Clock", "engrenagens"), "0378": ("Lock and big key", "mecanismo"),
    "2195": ("Man Breathing", "respiração"), "1404": ("Sigh by the nose", "respiração"),
    "0359": ("Heavy chain", "manopla"), "0619": ("Medium chain", "manopla"), "0013": ("Cloth", "tecido"),
    "0399": ("Tent or curtain shower", "estandarte ao vento"), "1022": ("Fall of Stone", "impactos"),
    "0616": ("Creaking metallic door", "metal sob tensão"), "0148": ("Glass Burst", "gelo partindo"),
    "2209": ("Ice cubes that melt", "gelo estalando"), "0606": ("Step, Shoe on Stone Staircase", "passos"),
}
KENNEY = {"rpg-audio": "https://kenney.nl/media/pages/assets/rpg-audio/8e99002d76-1677590336/kenney_rpg-audio.zip",
          "impact-sounds": "https://kenney.nl/media/pages/assets/impact-sounds/87b4ddecda-1677589768/kenney_impact-sounds.zip"}


# OpenGameArt: pacotes CC0 (licença conferida na página de cada um)
OGA = {"weapons-apparel": ("https://opengameart.org/sites/default/files/weapons-apparel.zip", "Fantasy Weapons and Apparel SFX Library (Jan Schupke)", "lâmina entrando na bainha"),
       "sword_-_starninjas_1": ("https://opengameart.org/sites/default/files/sword_-_starninjas_1.zip", "20 Sword Sound Effects: espadas (StarNinjas)", "espada cortando o ar"),
       "sword_clash_-_starninjas_0": ("https://opengameart.org/sites/default/files/sword_clash_-_starninjas_0.zip", "20 Sword Sound Effects: choques (StarNinjas)", "metal da espada vibrando"),
       "80-CC0-RPG-SFX_0": ("https://opengameart.org/sites/default/files/80-CC0-RPG-SFX_0.zip", "80 CC0 RPG SFX", "lâminas e metais curtos")}


def sh(*a, **k):
    subprocess.run(a, check=True, **k)


def baixar():
    os.makedirs(F, exist_ok=True)
    if not os.path.isdir(VSCO):
        sh("git", "clone", "-q", "--filter=blob:none", "--no-checkout", "--depth", "1", "https://github.com/sgossner/VSCO-2-CE", VSCO)
        sh("git", "-C", VSCO, "sparse-checkout", "set", "--no-cone", *PASTAS_VSCO)
        sh("git", "-C", VSCO, "checkout", "-q", "HEAD")
    os.makedirs(f"{F}/bsb", exist_ok=True)
    for n in BSB:
        if any(os.path.exists(f"{F}/bsb/{n}.{e}") for e in ("flac", "aiff")):
            continue
        for e in ("flac", "aiff"):   # nem todo som tem FLAC; o AIFF também é sem perda
            dst = f"{F}/bsb/{n}.{e}"
            sh("curl", "-sL", "-m", "120", "-o", dst, f"https://bigsoundbank.com/UPLOAD/{e}/{n}.{e}")
            if b"<html" in open(dst, "rb").read(200).lower():
                os.remove(dst)
            else:
                break
    for nome, (url, _, _) in OGA.items():
        d = f"{F}/oga/{nome}"
        if not os.path.isdir(d):
            os.makedirs(d, exist_ok=True)
            z = f"{F}/oga/{nome}.zip"
            sh("curl", "-sL", "-m", "120", "-o", z, url)
            sh("unzip", "-q", "-o", z, "-d", d)
            os.remove(z)
    os.makedirs(f"{F}/kenney", exist_ok=True)
    if len(os.listdir(f"{F}/kenney")) < 100:
        for nome, url in KENNEY.items():
            z = f"{F}/{nome}.zip"
            sh("curl", "-sL", "-m", "120", "-o", z, url)
            sh("unzip", "-q", "-o", "-j", z, "Audio/*", "-d", f"{F}/kenney")
            os.remove(z)


def creditos():
    l = ["# Créditos de som do trailer", "",
         "Todos os sons são gravações reais de bancos de uso livre, inclusive comercial. Nenhuma licença exige crédito,",
         "mas fica registrado de onde veio cada um.", "",
         "## Trilha: VSCO-2-CE (Versilian Studios Chamber Orchestra, Community Edition), CC0",
         "Gravado por Sam Gossner e Simon Dalzell. https://github.com/sgossner/VSCO-2-CE", "",
         "Naipes usados: violoncelos, violas e violinos (sustentado, spiccato e trêmulo), contrabaixo, harpa, trompas,",
         "trombone tenor, tuba, trompete, flauta, tímpanos, bumbo sinfônico, gongo, bigorna, prato suspenso e glockenspiel.", "",
         "## Efeitos: BigSoundBank (Joseph Sardin), CC0", "https://bigsoundbank.com", "",
         "| Nº | Som | Uso |", "|---|---|---|"]
    l += [f"| {n} | {a} | {b} |" for n, (a, b) in BSB.items()]
    l += ["", "## Efeitos: Kenney (RPG Audio e Impact Sounds), CC0", "https://kenney.nl",
          "Passos na neve, livro, tecido, lâmina saindo da bainha, impactos de metal e sino.", "",
          "## Efeitos: OpenGameArt (pacotes CC0)", "https://opengameart.org", ""] + [f"- {a}: {b}" for _, a, b in OGA.values()] + [""]
    return "\n".join(l) + "\n"


if __name__ == "__main__":
    baixar()
    open("/home/user/LTKG/exportacoes/trailer/audio/CREDITOS_SOM.md", "w").write(creditos())
    print("ok")
