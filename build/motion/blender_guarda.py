#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Guarda de Retorno em 3D (Blender/Cycles), como sequência de filme em três planos (24 fps, 8 s):
  1. close da manopla no antebraço esquerdo, células em vermelho sujo, neve caindo, relâmpagos ao longe;
  2. o arco branco-azulado entra na célula, que passa por vermelho, laranja e branco (saturada), com faíscas;
  3. contragolpe: a bota com chapa de lastro no gelo, as trincas correm pelo gelo e a neve explode para fora.
Segue o GUIA_VISUAL_DA_MAGIA: efeito físico real, fonte e custo à vista, sem escudo de luz.
Uso: python3 blender_guarda.py [--teste f1 f2 ...] [--amostras N] [--res 1280x720]"""
import math, os, random, sys
import bpy
from mathutils import Vector, Euler

ROOT = "/home/user/LTKG"
OUT = f"{ROOT}/build/_blender/guarda"; os.makedirs(OUT, exist_ok=True)
args = sys.argv[1:]
TESTE = []
if "--teste" in args:
    for a in args[args.index("--teste") + 1:]:
        if a.startswith("--"): break
        TESTE.append(int(a))
AMOSTRAS = int(args[args.index("--amostras") + 1]) if "--amostras" in args else 48
RES = tuple(int(v) for v in (args[args.index("--res") + 1] if "--res" in args else "1280x720").split("x"))
rnd = random.Random(11)

bpy.ops.wm.read_factory_settings(use_empty=True)
S = bpy.context.scene
S.render.engine = "CYCLES"; S.cycles.device = "CPU"; S.cycles.samples = AMOSTRAS
S.cycles.use_denoising = True; S.cycles.max_bounces = 6; S.cycles.volume_bounces = 1
S.render.resolution_x, S.render.resolution_y = RES; S.render.fps = 24
S.frame_start, S.frame_end = 1, 192
S.render.use_motion_blur = True; S.render.motion_blur_shutter = 0.45
S.render.image_settings.file_format = "PNG"; S.render.image_settings.color_depth = "8"
try:
    S.view_settings.view_transform = "AgX"; S.view_settings.look = "AgX - Medium High Contrast"
except TypeError:
    try: S.view_settings.look = "Medium High Contrast"
    except TypeError: pass


# ------------------------------------------------------------------ materiais
def mat(nome, cor=(.1, .1, .1), metal=0.0, rug=.5, emis=None, forca=0.0, bump=0.0, escala_bump=60.0):
    m = bpy.data.materials.new(nome); m.use_nodes = True
    nt = m.node_tree; p = nt.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*cor, 1); p.inputs["Metallic"].default_value = metal; p.inputs["Roughness"].default_value = rug
    if emis is not None:
        p.inputs["Emission Color"].default_value = (*emis, 1); p.inputs["Emission Strength"].default_value = forca
    if bump > 0:
        tx = nt.nodes.new("ShaderNodeTexNoise"); tx.inputs["Scale"].default_value = escala_bump; tx.inputs["Detail"].default_value = 8
        bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = bump
        nt.links.new(tx.outputs["Fac"], bp.inputs["Height"]); nt.links.new(bp.outputs["Normal"], p.inputs["Normal"])
        rg = nt.nodes.new("ShaderNodeTexNoise"); rg.inputs["Scale"].default_value = escala_bump / 6
        mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["To Min"].default_value = rug * .6; mr.inputs["To Max"].default_value = min(1, rug * 1.5)
        nt.links.new(rg.outputs["Fac"], mr.inputs["Value"]); nt.links.new(mr.outputs["Result"], p.inputs["Roughness"])
    return m


def mat_emissao(nome, cor, forca):
    m = bpy.data.materials.new(nome); m.use_nodes = True; nt = m.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    e = nt.nodes.new("ShaderNodeEmission"); e.inputs["Color"].default_value = (*cor, 1); e.inputs["Strength"].default_value = forca
    o = nt.nodes.new("ShaderNodeOutputMaterial"); nt.links.new(e.outputs["Emission"], o.inputs["Surface"])
    return m, e


def mat_celula(nome):
    """Cerâmica que emite pela escala de corpo negro; a temperatura e a força são animadas."""
    m = bpy.data.materials.new(nome); m.use_nodes = True; nt = m.node_tree; p = nt.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (.45, .42, .38, 1); p.inputs["Roughness"].default_value = .35
    bb = nt.nodes.new("ShaderNodeBlackbody"); nt.links.new(bb.outputs["Color"], p.inputs["Emission Color"])
    return m, bb, p


def poe(obj, m):
    obj.data.materials.clear(); obj.data.materials.append(m); return obj


def chave(alvo, campo, valores):
    for f, v in valores:
        setattr(alvo, campo, v) if not hasattr(alvo, "default_value") or campo != "default_value" else None
        if campo == "default_value": alvo.default_value = v
        alvo.keyframe_insert(campo, frame=f)


def suave(obj, nivel=2):
    obj.modifiers.new("sub", "SUBSURF").levels = nivel; obj.modifiers["sub"].render_levels = nivel
    for pol in obj.data.polygons: pol.use_smooth = True


AÇO = mat("aco", (.55, .56, .58), 1.0, .32, bump=.15, escala_bump=180)
AÇO_ESC = mat("aco_escuro", (.18, .18, .19), 1.0, .45, bump=.2, escala_bump=120)
LATÃO = mat("latao", (.72, .52, .25), 1.0, .3, bump=.1, escala_bump=200)
COURO = mat("couro", (.035, .03, .028), 0.0, .55, bump=.35, escala_bump=40)
LÃ = mat("la", (.045, .045, .05), 0.0, .9, bump=.3, escala_bump=90)
FERRO = mat("ferro", (.22, .21, .2), 1.0, .6, bump=.4, escala_bump=60)


def mat_gelo():
    m = bpy.data.materials.new("gelo"); m.use_nodes = True; nt = m.node_tree; p = nt.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (.05, .08, .1, 1); p.inputs["Roughness"].default_value = .12
    p.inputs["IOR"].default_value = 1.31
    vo = nt.nodes.new("ShaderNodeTexVoronoi"); vo.feature = "DISTANCE_TO_EDGE"; vo.inputs["Scale"].default_value = 3.0
    mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["From Max"].default_value = .03; mr.inputs["To Min"].default_value = 1; mr.inputs["To Max"].default_value = 0
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = .25
    nt.links.new(vo.outputs["Distance"], mr.inputs["Value"]); nt.links.new(mr.outputs["Result"], bp.inputs["Height"])
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 1.6; nz.inputs["Detail"].default_value = 6
    rp = nt.nodes.new("ShaderNodeValToRGB"); rp.color_ramp.elements[0].position = .52; rp.color_ramp.elements[0].color = (.05, .08, .1, 1)
    rp.color_ramp.elements[1].position = .62; rp.color_ramp.elements[1].color = (.7, .75, .8, 1)
    nt.links.new(nz.outputs["Fac"], rp.inputs["Fac"]); nt.links.new(rp.outputs["Color"], p.inputs["Base Color"])
    rr = nt.nodes.new("ShaderNodeMapRange"); rr.inputs["From Min"].default_value = .52; rr.inputs["From Max"].default_value = .62
    rr.inputs["To Min"].default_value = .08; rr.inputs["To Max"].default_value = .8
    nt.links.new(nz.outputs["Fac"], rr.inputs["Value"]); nt.links.new(rr.outputs["Result"], p.inputs["Roughness"])
    nt.links.new(bp.outputs["Normal"], p.inputs["Normal"])
    return m
GELO = mat_gelo()


def trincas_no_gelo(m, centro_obj):
    """Rede de trincas radial no próprio gelo: Voronoi em coordenadas polares, revelada até o raio R(t)."""
    nt = m.node_tree; p = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord"); tc.object = centro_obj
    sx = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Object"], sx.inputs["Vector"])
    at = nt.nodes.new("ShaderNodeMath"); at.operation = "ARCTAN2"; nt.links.new(sx.outputs["Y"], at.inputs[0]); nt.links.new(sx.outputs["X"], at.inputs[1])
    vl = nt.nodes.new("ShaderNodeVectorMath"); vl.operation = "LENGTH"; nt.links.new(tc.outputs["Object"], vl.inputs[0])
    m1 = nt.nodes.new("ShaderNodeMath"); m1.operation = "MULTIPLY"; m1.inputs[1].default_value = 5.0; nt.links.new(at.outputs[0], m1.inputs[0])
    lg = nt.nodes.new("ShaderNodeMath"); lg.operation = "POWER"; lg.inputs[1].default_value = .6; nt.links.new(vl.outputs["Value"], lg.inputs[0])
    m2 = nt.nodes.new("ShaderNodeMath"); m2.operation = "MULTIPLY"; m2.inputs[1].default_value = 1.1; nt.links.new(lg.outputs[0], m2.inputs[0])
    cx = nt.nodes.new("ShaderNodeCombineXYZ"); nt.links.new(m1.outputs[0], cx.inputs["X"]); nt.links.new(m2.outputs[0], cx.inputs["Y"])
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 7; nz.inputs["Detail"].default_value = 4
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    es = nt.nodes.new("ShaderNodeVectorMath"); es.operation = "SCALE"; es.inputs["Scale"].default_value = .22; nt.links.new(nz.outputs["Color"], es.inputs[0])
    ad = nt.nodes.new("ShaderNodeVectorMath"); ad.operation = "ADD"; nt.links.new(cx.outputs["Vector"], ad.inputs[0]); nt.links.new(es.outputs["Vector"], ad.inputs[1])
    vo = nt.nodes.new("ShaderNodeTexVoronoi"); vo.feature = "DISTANCE_TO_EDGE"; vo.inputs["Scale"].default_value = 2.0
    vo.inputs["Randomness"].default_value = 1.0; nt.links.new(ad.outputs["Vector"], vo.inputs["Vector"])
    lt = nt.nodes.new("ShaderNodeMapRange"); lt.inputs["From Min"].default_value = 0; lt.inputs["From Max"].default_value = .007
    lt.inputs["To Min"].default_value = 1; lt.inputs["To Max"].default_value = 0; nt.links.new(vo.outputs["Distance"], lt.inputs["Value"])
    raio = nt.nodes.new("ShaderNodeValue"); raio.name = "raio_trinca"
    sub = nt.nodes.new("ShaderNodeMath"); sub.operation = "SUBTRACT"; nt.links.new(raio.outputs[0], sub.inputs[0]); nt.links.new(vl.outputs["Value"], sub.inputs[1])
    msk = nt.nodes.new("ShaderNodeMapRange"); msk.inputs["From Min"].default_value = 0; msk.inputs["From Max"].default_value = .25
    nt.links.new(sub.outputs[0], msk.inputs["Value"])
    mu = nt.nodes.new("ShaderNodeMath"); mu.operation = "MULTIPLY"; nt.links.new(lt.outputs["Result"], mu.inputs[0]); nt.links.new(msk.outputs["Result"], mu.inputs[1])
    forca = nt.nodes.new("ShaderNodeValue"); forca.name = "forca_trinca"
    em = nt.nodes.new("ShaderNodeMath"); em.operation = "MULTIPLY"; nt.links.new(mu.outputs[0], em.inputs[0]); nt.links.new(forca.outputs[0], em.inputs[1])
    p.inputs["Emission Color"].default_value = (.62, .78, 1.0, 1); nt.links.new(em.outputs[0], p.inputs["Emission Strength"])
    return raio.outputs[0], forca.outputs[0]


# ------------------------------------------------------------------ mundo, neblina e luz
W_ = bpy.data.worlds.new("mundo"); S.world = W_; W_.use_nodes = True
bg = W_.node_tree.nodes["Background"]; bg.inputs["Color"].default_value = (.006, .008, .013, 1); bg.inputs["Strength"].default_value = 1
bpy.ops.mesh.primitive_cube_add(size=1, location=(2.5, 0, 2)); vol = bpy.context.object; vol.scale = (14, 12, 5); vol.name = "neblina"
mv = bpy.data.materials.new("neblina"); mv.use_nodes = True; nt = mv.node_tree
for n in list(nt.nodes): nt.nodes.remove(n)
pv = nt.nodes.new("ShaderNodeVolumePrincipled"); pv.inputs["Density"].default_value = .022; pv.inputs["Color"].default_value = (.7, .78, .9, 1)
pv.inputs["Anisotropy"].default_value = .35
o = nt.nodes.new("ShaderNodeOutputMaterial"); nt.links.new(pv.outputs["Volume"], o.inputs["Volume"]); poe(vol, mv)

bpy.ops.object.light_add(type="SUN", rotation=(math.radians(-55), math.radians(-25), math.radians(160)))
sol = bpy.context.object; sol.data.energy = 1.6; sol.data.color = (.62, .72, 1.0); sol.data.angle = math.radians(2)
bpy.ops.object.light_add(type="AREA", location=(4, -2.5, 2.2)); preench = bpy.context.object
preench.data.energy = 25; preench.data.color = (1, .55, .25); preench.data.size = 2.5
preench.rotation_euler = (Vector((5, 0, 1.2)) - preench.location).to_track_quat("-Z", "Y").to_euler()

bpy.ops.mesh.primitive_plane_add(size=40, location=(2.5, 0, 0)); gelo = poe(bpy.context.object, GELO); gelo.name = "gelo"


# ------------------------------------------------------------------ o braço com a manopla (planos 1 e 2)
BRACO = bpy.data.objects.new("braco", None); S.collection.objects.link(BRACO)
BRACO.location = (5, 0, 1.25); BRACO.rotation_euler = (math.radians(0), math.radians(-58), math.radians(28))


def filho(o): o.parent = BRACO; return o


bpy.ops.mesh.primitive_cylinder_add(radius=.058, depth=.62, vertices=48, location=(0, 0, -.12)); manga = filho(poe(bpy.context.object, COURO)); suave(manga, 1)
bpy.ops.mesh.primitive_cylinder_add(radius=.072, depth=.08, vertices=48, location=(0, 0, -.42)); punho_c = filho(poe(bpy.context.object, LÃ)); suave(punho_c, 1)
for k, z in enumerate((-.06, .02, .1, .18)):
    bpy.ops.mesh.primitive_cylinder_add(radius=.066 - k * .002, depth=.07, vertices=64, location=(0, 0, z)); b_ = filho(poe(bpy.context.object, AÇO))
    bv = b_.modifiers.new("bv", "BEVEL"); bv.width = .004; bv.segments = 3
    for a in range(0, 360, 45):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=.0042, location=(math.cos(math.radians(a)) * (.067 - k * .002), math.sin(math.radians(a)) * (.067 - k * .002), z + .028))
        filho(poe(bpy.context.object, LATÃO))
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, .072, .06)); trilho = filho(poe(bpy.context.object, AÇO_ESC)); trilho.scale = (.05, .022, .27)
bv = trilho.modifiers.new("bv", "BEVEL"); bv.width = .006; bv.segments = 3
CEL = []
for i, z in enumerate((-.03, .06, .15)):
    m, bb, p = mat_celula(f"celula{i}")
    bpy.ops.mesh.primitive_cylinder_add(radius=.0145, depth=.06, vertices=32, location=(0, .092, z)); c = filho(poe(bpy.context.object, m)); suave(c, 2)
    bpy.ops.mesh.primitive_torus_add(major_radius=.0175, minor_radius=.0032, location=(0, .092, z + .031)); filho(poe(bpy.context.object, LATÃO))
    bpy.ops.mesh.primitive_torus_add(major_radius=.0175, minor_radius=.0032, location=(0, .092, z - .031)); filho(poe(bpy.context.object, LATÃO))
    CEL.append((c, bb, p))
bpy.ops.mesh.primitive_uv_sphere_add(radius=.06, location=(0, 0, .27)); punho = filho(poe(bpy.context.object, AÇO_ESC)); punho.scale = (1, .85, .9); suave(punho, 1)
for k in range(4):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=.018, location=(-.03 + k * .02, .045, .31)); filho(poe(bpy.context.object, AÇO))

# estados das células: 0 e 1 em vermelho sujo; a 2 recebe o golpe e satura
for i, (c, bb, p) in enumerate(CEL):
    T = bb.inputs["Temperature"]; E = p.inputs["Emission Strength"]
    if i < 2:
        chave(T, "default_value", [(1, 1050), (192, 1050)]); chave(E, "default_value", [(1, 2.2 + .5 * i), (192, 2.2 + .5 * i)])
    else:
        chave(T, "default_value", [(1, 1050), (71, 1050), (78, 1700), (86, 2800), (96, 6500), (192, 6500)])
        chave(E, "default_value", [(1, 2.4), (71, 2.4), (76, 8), (86, 25), (96, 45), (132, 45), (192, 40)])

bpy.context.view_layer.update()
CEL_W = CEL[2][0].matrix_world.translation.copy()

# ------------------------------------------------------------------ o arco (plano 2): variantes que piscam
def zigue(a, b, ger=7, desv=.2, r=None):
    pts = [a, b]
    for _ in range(ger):
        novo = [pts[0]]
        for p, q in zip(pts, pts[1:]):
            L = (q - p).length * desv
            m = (p + q) / 2 + Vector((r.gauss(0, L), r.gauss(0, L), r.gauss(0, L * .6)))
            novo += [m, q]
        pts = novo
    return pts


def curva(nome, pts, raio, m):
    cu = bpy.data.curves.new(nome, "CURVE"); cu.dimensions = "3D"; cu.bevel_depth = raio; cu.bevel_resolution = 2; cu.use_fill_caps = True
    sp = cu.splines.new("POLY"); sp.points.add(len(pts) - 1)
    for k, p in enumerate(pts): sp.points[k].co = (p.x, p.y, p.z, 1)
    ob = bpy.data.objects.new(nome, cu); S.collection.objects.link(ob); poe(ob, m); return ob


M_ARCO, E_ARCO = mat_emissao("arco", (.72, .82, 1.0), 60)
ORIGEM = CEL_W + Vector((1.6, 1.1, 2.4))
ARCOS = []
for v in range(7):
    r = random.Random(100 + v)
    pts = zigue(ORIGEM, CEL_W + Vector((0, .012, 0)), 7, .17, r)
    grupo = [curva(f"arco{v}", pts, .0045, M_ARCO)]
    for k in range(3):
        p0 = pts[r.randrange(len(pts) // 4, len(pts) - 10)]
        grupo.append(curva(f"arco{v}_{k}", zigue(p0, p0 + Vector((r.uniform(-.5, .5), r.uniform(-.4, .4), r.uniform(-.6, .1))), 5, .2, r), .002, M_ARCO))
    ARCOS.append(grupo)
for f in range(1, 193):
    ativo = (f - 70) // 2 % len(ARCOS) if 70 <= f <= 96 and not (f in (79, 80, 88)) else -1
    for v, grupo in enumerate(ARCOS):
        for ob in grupo:
            ob.hide_render = v != ativo; ob.keyframe_insert("hide_render", frame=f)

bpy.ops.object.light_add(type="POINT", location=CEL_W + Vector((0, .08, 0))); clarao = bpy.context.object
clarao.data.shadow_soft_size = .02; clarao.data.color = (.75, .82, 1.0)
chave(clarao.data, "energy", [(1, 0), (69, 0), (70, 380), (72, 120), (74, 450), (77, 100), (81, 400), (86, 160), (90, 320), (96, 50), (100, 0), (192, 0)])
bpy.ops.object.light_add(type="POINT", location=CEL_W + Vector((0, .09, .02))); brilho_c = bpy.context.object
brilho_c.data.shadow_soft_size = .03; brilho_c.data.color = (1, .6, .3)
chave(brilho_c.data, "energy", [(1, 3), (71, 3), (86, 20), (96, 45), (192, 40)])
bpy.ops.object.light_add(type="POINT", location=(5.6, 3, 4)); relampago = bpy.context.object
relampago.data.color = (.7, .8, 1); relampago.data.shadow_soft_size = 1.5
chave(relampago.data, "energy", [(1, 0), (29, 0), (30, 3500), (32, 400), (33, 2500), (36, 0), (47, 0), (48, 2000), (50, 0), (192, 0)])

# faíscas do impacto
bpy.ops.mesh.primitive_ico_sphere_add(radius=.012, location=CEL_W); emissor = bpy.context.object; emissor.name = "faiscas"
M_FAI, _ = mat_emissao("faisca", (1, .7, .35), 40)
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, segments=8, ring_count=6, location=(0, -50, -50)); grao = poe(bpy.context.object, M_FAI); grao.name = "grao"
ps = emissor.modifiers.new("ps", "PARTICLE_SYSTEM").particle_system.settings
ps.count = 260; ps.frame_start = 70; ps.frame_end = 92; ps.lifetime = 14; ps.lifetime_random = .6
ps.emit_from = "FACE"; ps.normal_factor = 2.6; ps.factor_random = 1.6; ps.render_type = "OBJECT"; ps.instance_object = grao
ps.particle_size = .0016; ps.size_random = .6; ps.effector_weights.gravity = .6
emissor.show_instancer_for_render = False

# ------------------------------------------------------------------ a bota e o gelo (plano 3)
mb = bpy.data.metaballs.new("bota"); mb.resolution = .02; mb.render_resolution = .006; mb.threshold = .6
for co, (sx_, sy_, sz_), r_ in (((0, -.09, .075), (.1, .13, .13), 1.0), ((0, .03, .05), (.105, .2, .09), 1.0),
                                ((0, .15, .042), (.09, .11, .07), 1.0), ((0, -.07, .2), (.11, .11, .22), 1.0)):
    el = mb.elements.new(); el.type = "ELLIPSOID"; el.co = co; el.radius = r_; el.size_x, el.size_y, el.size_z = sx_, sy_, sz_
bota = bpy.data.objects.new("bota", mb); S.collection.objects.link(bota); poe(bota, COURO)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, .02, .02)); sola = poe(bpy.context.object, COURO); sola.scale = (.13, .36, .03)
bv = sola.modifiers.new("bv", "BEVEL"); bv.width = .01; bv.segments = 3
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, .02, .006)); chapa = poe(bpy.context.object, FERRO); chapa.scale = (.145, .37, .014)
bv = chapa.modifiers.new("bv", "BEVEL"); bv.width = .004; bv.segments = 2
for y in (-.13, -.04, .05, .14):
    for x in (-.062, .062):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=.006, location=(x * 1.13, y + .02, .016)); poe(bpy.context.object, LATÃO)
bpy.ops.mesh.primitive_cylinder_add(radius=.07, depth=.32, vertices=48, location=(0, -.06, .3)); cano = poe(bpy.context.object, COURO)
for pol in cano.data.polygons: pol.use_smooth = True
bpy.ops.mesh.primitive_torus_add(major_radius=.072, minor_radius=.008, location=(0, -.06, .24)); poe(bpy.context.object, FERRO)
bpy.ops.mesh.primitive_cylinder_add(radius=.085, depth=.9, vertices=48, location=(0, -.06, .9)); perna = poe(bpy.context.object, LÃ)
for pol in perna.data.polygons: pol.use_smooth = True

CENTRO = bpy.data.objects.new("centro_trinca", None); S.collection.objects.link(CENTRO); CENTRO.location = (0, .02, 0)
R_T, F_T = trincas_no_gelo(GELO, CENTRO)
chave(R_T, "default_value", [(1, 0), (136, 0), (140, .55), (148, 1.5), (160, 2.6), (192, 2.8)])
chave(F_T, "default_value", [(1, 0), (135, 0), (137, 6), (150, 2.2), (192, 1.4)])

bpy.ops.mesh.primitive_circle_add(radius=.25, fill_type="NGON", location=(0, 0, .02)); jato = bpy.context.object; jato.name = "jato_neve"
M_NEVE = mat("neve", (.85, .88, .92), 0, .6)
bpy.ops.mesh.primitive_ico_sphere_add(radius=1, subdivisions=1, location=(0, -60, -60)); floco = poe(bpy.context.object, M_NEVE); floco.name = "floco"
ps = jato.modifiers.new("ps", "PARTICLE_SYSTEM").particle_system.settings
ps.count = 1400; ps.frame_start = 136; ps.frame_end = 142; ps.lifetime = 40; ps.emit_from = "FACE"
ps.normal_factor = 1.2; ps.factor_random = 2.8; ps.object_align_factor = (0, 0, 1.2)
ps.render_type = "OBJECT"; ps.instance_object = floco; ps.particle_size = .006; ps.size_random = .8
ps.effector_weights.gravity = .35; ps.damping = .06
jato.show_instancer_for_render = False

bpy.ops.object.light_add(type="POINT", location=(.05, .35, 1.25)); luz_cel = bpy.context.object
luz_cel.data.color = (1, .78, .55); luz_cel.data.shadow_soft_size = .05
chave(luz_cel.data, "energy", [(1, 0), (132, 60), (136, 400), (140, 160), (192, 120)])

# neve caindo (o tempo todo, nos dois lugares)
for nome, centro in (("neve_braco", (5, 0, 2.6)), ("neve_bota", (0, 0, 2.2))):
    bpy.ops.mesh.primitive_plane_add(size=5, location=centro); em = bpy.context.object; em.name = nome
    ps = em.modifiers.new("ps", "PARTICLE_SYSTEM").particle_system.settings
    ps.count = 5000; ps.frame_start = -160; ps.frame_end = 192; ps.lifetime = 260; ps.emit_from = "FACE"
    ps.normal_factor = 0; ps.object_align_factor = (.12, .04, -.32); ps.brownian_factor = .05
    ps.render_type = "OBJECT"; ps.instance_object = floco; ps.particle_size = .0032; ps.size_random = .7; ps.effector_weights.gravity = .02
    em.show_instancer_for_render = False

# ------------------------------------------------------------------ câmeras e montagem
def camera(nome, lente, pos, alvo, foco, fstop):
    cd = bpy.data.cameras.new(nome); cd.lens = lente; cd.dof.use_dof = True; cd.dof.focus_distance = foco; cd.dof.aperture_fstop = fstop
    cd.sensor_width = 36; ob = bpy.data.objects.new(nome, cd); S.collection.objects.link(ob); ob.location = pos
    ob.rotation_euler = (Vector(alvo) - Vector(pos)).to_track_quat("-Z", "Y").to_euler(); return ob


ALVO1 = CEL_W + Vector((0, 0, -.02))
c1 = camera("plano1", 70, ALVO1 + Vector((.05, .62, .05)), ALVO1, .6, 2.4)
chave(c1, "location", [(1, ALVO1 + Vector((.06, .7, .07))), (60, ALVO1 + Vector((.03, .56, .03)))])
c2 = camera("plano2", 35, CEL_W + Vector((-.55, 1.35, .25)), CEL_W + Vector((.25, 0, .25)), 1.42, 2.8)
base2 = c2.location.copy()
for f in range(61, 133):
    k = .012 if 70 <= f <= 90 else .003
    c2.location = base2 + Vector((rnd.gauss(0, k), rnd.gauss(0, k), rnd.gauss(0, k))); c2.keyframe_insert("location", frame=f)
c3 = camera("plano3", 24, (.36, -.46, .045), (-.02, .1, .08), .58, 4.0)
base3 = c3.location.copy()
for f in range(133, 193):
    k = .018 * max(0, 1 - (f - 136) / 16) if f >= 136 else .002
    c3.location = base3 + Vector((rnd.gauss(0, k), rnd.gauss(0, k), rnd.gauss(0, k * .5))); c3.keyframe_insert("location", frame=f)
for f, cam in ((1, c1), (61, c2), (133, c3)):
    mk = S.timeline_markers.new(cam.name, frame=f); mk.camera = cam
S.camera = c1

for ob in S.objects:                                                     # interpolação constante nos cortes e no pisca
    ad = ob.animation_data
    if ad and ad.action:
        for fc in getattr(ad.action, "fcurves", []):
            if fc.data_path == "hide_render":
                for kp in fc.keyframe_points: kp.interpolation = "CONSTANT"

if TESTE:
    for f in TESTE:
        S.frame_set(f)
        for mk in sorted(S.timeline_markers, key=lambda m: m.frame):
            if mk.frame <= f: S.camera = mk.camera
        S.render.filepath = f"{OUT}/teste_{f:04d}.png"; bpy.ops.render.render(write_still=True)
else:
    S.render.filepath = f"{OUT}/q_"; S.render.use_overwrite = False; bpy.ops.render.render(animation=True)   # retoma: pula quadros prontos
