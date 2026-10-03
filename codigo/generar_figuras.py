#!/usr/bin/env python3
# Genera el SVG de las Figuras 2 y 3 sin depender de navegador ni graphviz.
# Layout por niveles (BFS) con posiciones fijas, salida SVG legible.
import html
import sys

# ---------------------------------------------------------------- Figura 2
# Nodos y enlaces tomados de la salida real de mapa_ramas_ia.py --mermaid
F2_NODES = {
    "N0": "Algoritmos evolutivos",
    "N1": "Redes neuronales",
    "N2": "Lógica difusa",
    "N3": "Aprendizaje automático",
    "N4": "Visión por computadora",
    "N5": "Procesamiento de lenguaje natural (PLN)",
    "N6": "Aprendizaje por reforzamiento",
    "N7": "Sistemas difusos",
    "N8": "LLM",
    "N9": "Asistente BIB-01",
}
F2_EDGES = [
    ("N2", "N7", "los sistemas difusos aplican la lógica difusa"),
    ("N6", "N3", "es un paradigma del aprendizaje automático"),
    ("N1", "N3", "se estudian dentro del aprendizaje automático"),
    ("N8", "N1", "se construye con redes neuronales"),
    ("N8", "N5", "se usa para tareas de PLN"),
    ("N4", "N1", "suele apoyarse en redes neuronales"),
    ("N9", "N8", "el asistente propuesto usaría un LLM"),
]
# coloration suave por familia
F2_FILL = {
    "N0": "#f5f5f5", "N1": "#e8eaf6", "N2": "#e0f2f1", "N3": "#e3f2fd",
    "N4": "#fff3e0", "N5": "#e8f5e9", "N6": "#fce4ec", "N7": "#e0f2f1",
    "N8": "#ede7f6", "N9": "#fff59d",
}
F2_POS = {
    "N9": (70, 60),
    "N8": (70, 215),
    "N5": (410, 60),
    "N1": (70, 390),
    "N6": (70, 560),
    "N3": (410, 460),
    "N4": (410, 660),
    "N2": (70, 720),
    "N7": (410, 840),
    "N0": (70, 980),
}

# ---------------------------------------------------------------- Figura 3
F3_ROWS = [
    ("start", ["Recibir la pregunta"]),
    ("dec", ["Revisar datos y alcance"]),
    ("act", ["Pedir retirar el dato", "Rechazar la solicitud", "Consultar BIB-01 v1"]),
    ("dec", ["¿Hay fragmento que respalde?"]),
    ("act", ["Preparar abstención y remitir al bibliotecario",
             "Preparar borrador con fragmento y fuente"]),
    ("pers", ["Persona: el bibliotecario revisa"]),
    ("dec", ["¿Aprueba y no hay datos personales?"]),
    ("act", ["Publicar respuesta", "No publicar; corregir o abstenerse"]),
    ("end", ["Guardar registro mínimo"]),
]
F3_FILL = {"start": "#e3f2fd", "dec": "#fff3e0", "act": "#f5f5f5",
           "pers": "#fff59d", "end": "#e8f5e9"}


def esc(s):
    return html.escape(s, quote=True)


def wrap(text, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        cand = (cur + " " + w).strip()
        if len(cand) > width and cur:
            lines.append(cur)
            cur = w
        else:
            cur = cand
    if cur:
        lines.append(cur)
    return lines


def rounded_box(x, y, w, h, label, fill, stroke="#455a64", fs=13, rx=8):
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" ry="{rx}" '
           f'fill="{fill}" stroke="{stroke}" stroke-width="1.4"/>']
    lines = wrap(label, int(w / 6.4))
    total = len(lines) * (fs + 3)
    ty = y + h / 2 - total / 2 + fs
    for i, ln in enumerate(lines):
        out.append(f'<text x="{x + w / 2}" y="{ty + i * (fs + 3)}" font-family="DejaVu Sans, sans-serif" '
                   f'font-size="{fs}" fill="#212121" text-anchor="middle">{esc(ln)}</text>')
    return "\n".join(out), (x + w / 2, y + h / 2), len(lines)


def edge(d, lx, ly, x2, y2, label=None, dashed=False):
    mx, my = (lx or 0), (ly or 0)
    out = [f'<path d="{d}" fill="none" stroke="#546e7a" stroke-width="1.3"'
           + (' stroke-dasharray="5,4"' if dashed else "") + '/>']
    if label:
        wpx = max(7.0, len(label) * 5.0 + 12)
        out.append(f'<rect x="{mx - wpx / 2}" y="{my - 9}" width="{wpx}" height="16" rx="4" '
                   f'fill="#ffffff" stroke="#cfd8dc" stroke-width="0.8"/>')
        out.append(f'<text x="{mx}" y="{my + 2.5}" font-family="DejaVu Sans, sans-serif" font-size="10" '
                   f'fill="#37474f" text-anchor="middle">{esc(label)}</text>')
    return "\n".join(out)


def arrow_head(x, y, direction="down", size=5.5):
    if direction == "down":
        pts = f"{x},{y} {x - size},{y - size * 1.6} {x + size},{y - size * 1.6}"
    else:
        pts = f"{x},{y} {x - size * 1.6},{y - size} {x - size * 1.6},{y + size}"
    return (f'<polygon points="{pts}" fill="#546e7a"/>')


# ---------------------------------------------------------------- Figura 2
def figura2():
    W, H = 720, 1080
    NW, NH = 230, 44
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
             f'viewBox="0 0 {W} {H}" font-family="DejaVu Sans, sans-serif">',
             f'<rect width="{W}" height="{H}" fill="#ffffff"/>']
    # aristas primero (detrás)
    for a, b, lab in F2_EDGES:
        ax, ay = F2_POS[a]
        bx, by = F2_POS[b]
        acx, acy = ax + NW / 2, ay + NH / 2
        bcx, bcy = bx + NW / 2, by + NH / 2
        d = f"M {acx},{acy + NH / 2} C {acx},{bcy} {bcx},{acy} {bcx},{bcy - NH / 2}"
        # etiqueta en el punto medio real de la curva (t=0.5 de la cubica)
        t = 0.5
        mt = 1 - t
        px = (mt ** 3 * acx + 3 * mt ** 2 * t * acx
              + 3 * mt * t ** 2 * bcx + t ** 3 * bcx)
        py = (mt ** 3 * (acy + NH / 2) + 3 * mt ** 2 * t * bcy
              + 3 * mt * t ** 2 * acy + t ** 3 * (bcy - NH / 2))
        parts.append(edge(d, px, py, 0, 0, label=lab))
        parts.append(arrow_head(bcx, bcy - NH / 2, "down"))
    for n, lab in F2_NODES.items():
        x, y = F2_POS[n]
        svg, _, _ = rounded_box(x, y, NW, NH, lab, F2_FILL[n])
        parts.append(svg)
    parts.append("</svg>")
    return "\n".join(parts)


# ---------------------------------------------------------------- Figura 3
def figura3():
    W = 820
    BOX_W, BOX_H, GAP = 250, 44, 56
    x0 = 40
    # calcular alto total
    rows = F3_ROWS
    row_hs = [max(BOX_H, len(labels) * (BOX_H + 16) - 16) for _k, labels in rows]
    total_h = sum(row_hs) + GAP * (len(rows) - 1)
    H = total_h + 30
    centers = {}
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
             f'viewBox="0 0 {W} {H}" font-family="DejaVu Sans, sans-serif">',
             f'<rect width="{W}" height="{H}" fill="#ffffff"/>']
    y = 20
    placements = []
    for (kind, labels), row_h in zip(rows, row_hs):
        n = len(labels)
        total_w = n * BOX_W + (n - 1) * 26
        sx = (W - total_w) / 2
        box_h = BOX_H
        for i, lab in enumerate(labels):
            x = sx + i * (BOX_W + 26)
            centers[lab] = (x + BOX_W / 2, y + box_h / 2)
            placements.append((kind, lab, x, y, box_h))
        y += row_h + GAP

    for kind, lab, x, yy, box_h in placements:
        svg, (cx, cy), _ = rounded_box(x, yy, BOX_W, box_h, lab, F3_FILL[kind],
                                       stroke="#37474f" if kind == "dec" else "#455a64")
        parts.append(svg)

    def link(a, b, label=None, dashed=False):
        ax, ay = centers[a]
        bx, by = centers[b]
        parts.append(edge(f"M {ax},{ay + 22} L {bx},{by - 22}", (ax + bx) / 2, (ay + by) / 2,
                          0, 0, label=label, dashed=dashed))
        parts.append(arrow_head(bx, by - 22, "down"))

    # conexiones
    link("Recibir la pregunta", "Revisar datos y alcance")
    rev = ("Revisar datos y alcance",)
    link("Revisar datos y alcance", "Pedir retirar el dato")
    link("Revisar datos y alcance", "Rechazar la solicitud")
    link("Revisar datos y alcance", "Consultar BIB-01 v1")
    link("Consultar BIB-01 v1", "¿Hay fragmento que respalde?")
    link("¿Hay fragmento que respalde?",
         "Preparar abstención y remitir al bibliotecario")
    link("¿Hay fragmento que respalde?",
         "Preparar borrador con fragmento y fuente")
    link("Preparar abstención y remitir al bibliotecario",
         "Persona: el bibliotecario revisa")
    link("Preparar borrador con fragmento y fuente",
         "Persona: el bibliotecario revisa")
    link("Persona: el bibliotecario revisa",
         "¿Aprueba y no hay datos personales?")
    link("¿Aprueba y no hay datos personales?", "Publicar respuesta")
    link("¿Aprueba y no hay datos personales?",
         "No publicar; corregir o abstenerse")
    link("Publicar respuesta", "Guardar registro mínimo")
    link("No publicar; corregir o abstenerse", "Guardar registro mínimo")
    parts.append("</svg>")
    return "\n".join(parts)


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "ambas"
    if which in ("2", "ambas"):
        open("/tmp/opencode/figura2.svg", "w", encoding="utf-8").write(figura2())
        print("figura2.svg escrito")
    if which in ("3", "ambas"):
        open("/tmp/opencode/figura3.svg", "w", encoding="utf-8").write(figura3())
        print("figura3.svg escrito")