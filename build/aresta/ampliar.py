#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ampliação 4× com Real-ESRGAN x4plus, rodando na CPU via onnxruntime (sem PyTorch).
A rede RRDBNet é montada como grafo ONNX a partir dos pesos em safetensors
(huggingface.co/Comfy-Org/Real-ESRGAN_repackaged, licença BSD-3) e processada em blocos.
Uso: python3 ampliar.py [--mistura=0.6] <entrada.png> [<entrada2> ...]
--mistura mistura o resultado com a ampliação Lanczos do original (0.6 = 60% Real-ESRGAN). Usar em
retratos: o modelo puro deixa a pele lisa demais. Capas e cenários ficam melhores com o resultado puro.
Os pesos são baixados uma vez para build/_modelos/ (fora do git).
Saída: exportacoes/banco_de_arte_4x/<categoria>/<nome>_4x.jpg"""
import os, subprocess, sys, time
import numpy as np
import onnx, onnxruntime as ort
from onnx import helper, numpy_helper, TensorProto
from safetensors.numpy import load_file
from PIL import Image

ROOT = "/home/user/LTKG"
OUT = f"{ROOT}/exportacoes/banco_de_arte_4x"
PESOS = f"{ROOT}/build/_modelos/RealESRGAN_x4plus.safetensors"
URL = "https://huggingface.co/Comfy-Org/Real-ESRGAN_repackaged/resolve/main/RealESRGAN_x4plus.safetensors"
TILE, PAD = 256, 16


def rede(pesos):
    w = load_file(pesos)
    nodes, inits, n = [], [], [0]

    def nome(p):
        n[0] += 1
        return f"{p}{n[0]}"

    def conv(x, k):
        for s in ("weight", "bias"):
            inits.append(numpy_helper.from_array(w[f"{k}.{s}"].astype(np.float32), f"{k}.{s}"))
        y = nome("c")
        nodes.append(helper.make_node("Conv", [x, f"{k}.weight", f"{k}.bias"], [y], pads=[1, 1, 1, 1]))
        return y

    def op(t, xs, **kw):
        y = nome(t)
        nodes.append(helper.make_node(t, xs, [y], **kw))
        return y

    lrelu = lambda x: op("LeakyRelu", [x], alpha=0.2)
    inits.append(numpy_helper.from_array(np.array(0.2, np.float32), "s02"))
    inits.append(numpy_helper.from_array(np.array([1, 1, 2, 2], np.float32), "esc2"))
    soma_escalada = lambda a, x: op("Add", [op("Mul", [a, "s02"]), x])
    dobra = lambda x: op("Resize", [x, "", "esc2"], mode="nearest",
                         coordinate_transformation_mode="asymmetric", nearest_mode="floor")

    def rdb(x, k):
        xs = [x]
        for i in range(1, 5):
            xs.append(lrelu(conv(op("Concat", xs, axis=1) if len(xs) > 1 else x, f"{k}.conv{i}")))
        return soma_escalada(conv(op("Concat", xs, axis=1), f"{k}.conv5"), x)

    feat = conv("x", "conv_first")
    b = feat
    for i in range(23):
        r = b
        for j in (1, 2, 3):
            r = rdb(r, f"body.{i}.rdb{j}")
        b = soma_escalada(r, b)
    feat = op("Add", [feat, conv(b, "conv_body")])
    feat = lrelu(conv(dobra(feat), "conv_up1"))
    feat = lrelu(conv(dobra(feat), "conv_up2"))
    out = conv(lrelu(conv(feat, "conv_hr")), "conv_last")
    nodes.append(helper.make_node("Identity", [out], ["y"]))
    g = helper.make_graph(nodes, "rrdbnet_x4",
                          [helper.make_tensor_value_info("x", TensorProto.FLOAT, [1, 3, "h", "w"])],
                          [helper.make_tensor_value_info("y", TensorProto.FLOAT, [1, 3, "H", "W"])], inits)
    m = helper.make_model(g, opset_imports=[helper.make_opsetid("", 13)], ir_version=8)
    so = ort.SessionOptions()
    so.intra_op_num_threads = os.cpu_count()
    return ort.InferenceSession(m.SerializeToString(), so, providers=["CPUExecutionProvider"])


def ampliar(sess, im):
    a = np.asarray(im.convert("RGB"), np.float32).transpose(2, 0, 1) / 255.0
    _, h, wd = a.shape
    res = np.zeros((3, h * 4, wd * 4), np.float32)
    for y0 in range(0, h, TILE):
        for x0 in range(0, wd, TILE):
            y1, x1 = min(y0 + TILE, h), min(x0 + TILE, wd)
            py0, px0, py1, px1 = max(y0 - PAD, 0), max(x0 - PAD, 0), min(y1 + PAD, h), min(x1 + PAD, wd)
            t = sess.run(None, {"x": a[None, :, py0:py1, px0:px1]})[0][0]
            oy, ox = (y0 - py0) * 4, (x0 - px0) * 4
            res[:, y0 * 4:y1 * 4, x0 * 4:x1 * 4] = t[:, oy:oy + (y1 - y0) * 4, ox:ox + (x1 - x0) * 4]
    return Image.fromarray((np.clip(res, 0, 1).transpose(1, 2, 0) * 255 + 0.5).astype(np.uint8))


if __name__ == "__main__":
    if not os.path.exists(PESOS):
        os.makedirs(os.path.dirname(PESOS), exist_ok=True)
        subprocess.run(["curl", "-sSfL", "-o", PESOS, URL], check=True)
    mistura = 1.0
    args = [a for a in sys.argv[1:] if not a.startswith("--mistura=")]
    for a in sys.argv[1:]:
        if a.startswith("--mistura="): mistura = float(a.split("=", 1)[1])
    sess = rede(PESOS)
    for src in args:
        t0 = time.time()
        cat = os.path.basename(os.path.dirname(src))
        os.makedirs(f"{OUT}/{cat}", exist_ok=True)
        dst = f"{OUT}/{cat}/{os.path.splitext(os.path.basename(src))[0]}_4x.jpg"
        im = ampliar(sess, Image.open(src))
        if mistura < 1:
            im = Image.blend(Image.open(src).convert("RGB").resize(im.size, Image.LANCZOS), im, mistura)
        im.save(dst, quality=93, subsampling=0, optimize=True)
        print(dst, im.size, f"{time.time() - t0:.0f}s", flush=True)
