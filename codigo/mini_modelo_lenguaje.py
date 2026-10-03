#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mini_modelo_lenguaje.py  -  Actividad 3, Fundamentos de IA (E-FIA-3)

Modelo de bigramas: para elegir la palabra siguiente solo observa la
palabra anterior. NO es un LLM y su salida no demuestra que un texto sea
verdadero ni seguro. Es un generador por conteos que se puede revisar a mano.

USO
    python mini_modelo_lenguaje.py                         # pide los datos
    python mini_modelo_lenguaje.py --inicio la --semilla 1 --limite 10
    python mini_modelo_lenguaje.py --corpus ../datos/corpus_sin_cuarta_frase.txt \
           --inicio biblioteca --semilla 7 --limite 10
    python mini_modelo_lenguaje.py --inicio museo --semilla 1 --limite 10   # sin continuación

ENTRADA : corpus (una frase por línea), palabra inicial, semilla entera,
          límite entero de 1 a 50 palabras (incluye la inicial).
SALIDA  : proporciones antes del sorteo, texto generado, motivo de parada
          y un archivo de traza (CSV) en la carpeta exportacion/.

Ecuación (7) del material:  P(v|u) = C(u,v) / N(u),  con N(u) > 0.
"""

import argparse
import csv
import random
import re
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
CORPUS_DEFECTO = BASE / "datos" / "corpus_biblioteca.txt"
DIR_TRAZAS = BASE / "exportacion"
FIN = "<FIN>"
LIMITE_MIN, LIMITE_MAX = 1, 50


def tokenizar(frase):
    """Minúsculas y palabras completas (se ignoran signos de puntuación)."""
    return re.findall(r"[a-záéíóúüñ0-9]+", frase.lower())


def leer_frases(texto):
    """Una frase por línea. Un corpus sin frases se rechaza antes de empezar."""
    frases = [tokenizar(linea) for linea in texto.splitlines()]
    frases = [f for f in frases if f]
    if not frases:
        raise ValueError("Corpus vacío: no hay frases con palabras. No se puede construir el modelo.")
    return frases


def construir_conteos(frases):
    """
    Cuenta parejas consecutivas dentro de cada frase (sin unir frases) y añade
    <FIN> al terminar cada una. Devuelve {palabra_anterior: Counter(siguientes)}.
    """
    conteos = {}
    for palabras in frases:
        secuencia = palabras + [FIN]
        for u, v in zip(secuencia, secuencia[1:]):
            conteos.setdefault(u, Counter())[v] += 1
    return conteos


def opciones(conteos, u):
    """
    Lista de (v, C(u,v), N(u), proporción) en orden estable: más repetidas
    primero y, en empate, alfabético. Devuelve [] si u no tiene continuaciones.
    """
    if u not in conteos:
        return []
    total = sum(conteos[u].values())            # N(u)
    orden = sorted(conteos[u].items(), key=lambda par: (-par[1], par[0]))
    return [(v, c, total, c / total) for v, c in orden]   # ecuación (7)


def validar_parametros(semilla, limite):
    """La semilla y el límite deben ser enteros; el límite, de 1 a 50."""
    try:
        semilla = int(str(semilla).strip())
    except (ValueError, TypeError):
        raise ValueError(f"La semilla debe ser un entero; se recibió {semilla!r}.") from None
    try:
        limite = int(str(limite).strip())
    except (ValueError, TypeError):
        raise ValueError(f"El límite debe ser un entero; se recibió {limite!r}.") from None
    if not LIMITE_MIN <= limite <= LIMITE_MAX:
        raise ValueError(f"El límite debe estar entre {LIMITE_MIN} y {LIMITE_MAX}; se recibió {limite}.")
    return semilla, limite


def generar(conteos, inicio, semilla, limite):
    """
    Genera texto desde la palabra inicial. Se detiene por:
      - 'FIN'                : se eligió <FIN>.
      - 'limite'             : el texto llegó al límite de palabras.
      - 'sin_continuacion'   : la palabra actual no tiene continuaciones observadas.
    Devuelve (palabras, motivo, traza). La traza guarda opciones y elecciones.
    """
    inicio = inicio.strip().lower()
    if not inicio:
        raise ValueError("La palabra inicial no puede estar vacía.")
    rng = random.Random(semilla)                # misma semilla -> mismo sorteo
    texto = [inicio]
    traza = []
    actual = inicio
    while True:
        if len(texto) >= limite:
            return texto, "limite", traza
        opc = opciones(conteos, actual)
        if not opc:
            traza.append({"paso": len(traza) + 1, "palabra_actual": actual,
                          "opciones": "(sin continuación observada)", "elegido": ""})
            return texto, "sin_continuacion", traza
        # Más oportunidad a las palabras más repetidas: pesos = conteos.
        elegido = rng.choices([v for v, _, _, _ in opc], weights=[c for _, c, _, _ in opc], k=1)[0]
        traza.append({
            "paso": len(traza) + 1,
            "palabra_actual": actual,
            "opciones": "; ".join(f"{v}:{c}/{n}={p:.4f}" for v, c, n, p in opc),
            "elegido": elegido,
        })
        if elegido == FIN:
            return texto, "FIN", traza
        texto.append(elegido)
        actual = elegido


MENSAJES_PARADA = {
    "FIN": "Se llegó a <FIN>.",
    "limite": "Se alcanzó el límite de palabras.",
    "sin_continuacion": "Contexto no observado: la palabra no tiene continuaciones en el corpus.",
}


def guardar_traza(traza, semilla, ruta=None):
    """Guarda la traza en CSV. Devuelve (éxito, mensaje)."""
    ruta = Path(ruta) if ruta else DIR_TRAZAS / f"traza_semilla_{semilla}.csv"
    try:
        ruta.parent.mkdir(parents=True, exist_ok=True)
        with open(ruta, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=["paso", "palabra_actual", "opciones", "elegido"])
            w.writeheader()
            w.writerows(traza)
    except OSError as error:
        return False, f"No se pudo escribir la traza en {ruta}: {error}"
    return True, f"Traza guardada en: {ruta}"


def ejecutar(ruta_corpus, inicio, semilla, limite, ruta_traza=None):
    """Flujo completo. Devuelve 0 si todo salió bien y 1 si se rechazó una entrada."""
    try:
        texto_corpus = Path(ruta_corpus).read_text(encoding="utf-8")
    except OSError as error:
        print(f"RECHAZADO: no se pudo leer el corpus ({error}).")
        return 1
    try:
        frases = leer_frases(texto_corpus)
        semilla, limite = validar_parametros(semilla, limite)
        conteos = construir_conteos(frases)
        ini = inicio.strip().lower()
        opc = opciones(conteos, ini)
        print(f"Frases del corpus: {len(frases)}")
        if opc:
            print(f"Antes del sorteo, continuaciones de «{ini}» (N = {opc[0][2]}):")
            for v, c, n, p in opc:
                print(f"  {v}: {c}/{n} = {p:.2f}")
        texto, motivo, traza = generar(conteos, inicio, semilla, limite)
    except ValueError as error:
        print(f"RECHAZADO: {error}")
        return 1
    print(f"Semilla: {semilla} | Límite: {limite}")
    print("Texto generado:", " ".join(texto))
    print(f"Motivo de parada: {motivo} - {MENSAJES_PARADA[motivo]}")
    print(f"Palabras: {len(texto)} (máximo {limite})")
    print(guardar_traza(traza, semilla, ruta_traza)[1])
    print("Nota: es un generador por conteos, no un LLM; no comprueba que el texto sea verdadero.")
    return 0


def main():
    p = argparse.ArgumentParser(description="Mini modelo de bigramas")
    p.add_argument("--corpus", default=str(CORPUS_DEFECTO))
    p.add_argument("--inicio")
    p.add_argument("--semilla")
    p.add_argument("--limite")
    p.add_argument("--traza", help="ruta del CSV de traza (opcional)")
    a = p.parse_args()
    inicio = a.inicio if a.inicio is not None else input("Palabra inicial: ")
    semilla = a.semilla if a.semilla is not None else input("Semilla (entero): ")
    limite = a.limite if a.limite is not None else input("Límite de palabras (1-50): ")
    raise SystemExit(ejecutar(a.corpus, inicio, semilla, limite, a.traza))


if __name__ == "__main__":
    main()
