#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ejecutar_pruebas.py  -  Actividad 3, Fundamentos de IA (E-FIA-3)

Ejecuta los tres programas con las entradas de la Tabla 6 y las pruebas
adicionales del inciso e). Cada prueba define ANTES de ejecutar:
  entrada, resultado esperado y un criterio de comprobación.
Después ejecuta el programa real (subprocess), guarda lo obtenido y marca
CUMPLE o NO CUMPLE. Un fallo se conserva en el registro; no se oculta.

USO
    python ejecutar_pruebas.py
SALIDA
    ../exportacion/registro_pruebas.txt   (entrada, esperado, obtenido, resultado)
    ../exportacion/traza_<prueba>.csv     (trazas del mini modelo)
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

AQUI = Path(__file__).resolve().parent
BASE = AQUI.parent
DATOS = BASE / "datos"
EXPORT = BASE / "exportacion"
EXPORT.mkdir(parents=True, exist_ok=True)


def ejecutar(script, *args):
    """Corre un programa como proceso aparte y devuelve (código, salida)."""
    r = subprocess.run([sys.executable, str(AQUI / script), *args],
                       capture_output=True, text=True, encoding="utf-8")
    return r.returncode, (r.stdout + r.stderr).strip()


def texto_generado(salida):
    for linea in salida.splitlines():
        if linea.startswith("Texto generado:"):
            return linea.split(":", 1)[1].strip()
    return ""


def traza(nombre):
    return str(EXPORT / f"traza_{nombre}.csv")


# ---------------------------------------------------------------------------
# DEFINICIÓN DE PRUEBAS: lo esperado se escribe aquí, antes de ejecutar nada.
# Cada prueba: id, programa, descripción de la entrada, esperado (texto),
# función que ejecuta, función que comprueba (recibe código y salida).
# ---------------------------------------------------------------------------
PRUEBAS = [
    # ---- Mapa de ramas -----------------------------------------------------
    dict(id="M-01", prog="mapa_ramas_ia.py", entrada='consulta "PLN"',
         esperado="Muestra la ficha de PLN y su conexión con LLM.",
         correr=lambda: ejecutar("mapa_ramas_ia.py", "--consulta", "PLN"),
         ok=lambda c, s: c == 0 and "LLM" in s and "Procesamiento de lenguaje natural" in s),
    dict(id="M-02", prog="mapa_ramas_ia.py", entrada='consulta "Quantum" (rama inexistente)',
         esperado="Indica «Término no registrado».",
         correr=lambda: ejecutar("mapa_ramas_ia.py", "--consulta", "Quantum"),
         ok=lambda c, s: "Término no registrado" in s),
    dict(id="M-03", prog="mapa_ramas_ia.py", entrada='consulta "lógica difusa"',
         esperado="Muestra la ficha y la conexión con Sistemas difusos.",
         correr=lambda: ejecutar("mapa_ramas_ia.py", "--consulta", "lógica difusa"),
         ok=lambda c, s: "Sistemas difusos" in s and "Lógica difusa" in s),
    dict(id="M-04", prog="mapa_ramas_ia.py", entrada='consulta "reforzamiento"',
         esperado="Muestra la ficha y la conexión con Aprendizaje automático.",
         correr=lambda: ejecutar("mapa_ramas_ia.py", "--consulta", "reforzamiento"),
         ok=lambda c, s: "Aprendizaje automático" in s and "Aprendizaje por reforzamiento" in s),
    dict(id="M-05", prog="mapa_ramas_ia.py", entrada='consulta "" (vacía)',
         esperado="Indica «Consulta vacía» sin error.",
         correr=lambda: ejecutar("mapa_ramas_ia.py", "--consulta", ""),
         ok=lambda c, s: "Consulta vacía" in s and c == 0),
    dict(id="M-06", prog="mapa_ramas_ia.py", entrada='recomendar "algo" "otra cosa" "" (sin pistas)',
         esperado="Responde «Información insuficiente»; no declara incompatibilidad.",
         correr=lambda: ejecutar("mapa_ramas_ia.py", "--recomendar", "algo", "otra cosa", ""),
         ok=lambda c, s: "Información insuficiente" in s and "incompatible" not in s),
    dict(id="M-07", prog="mapa_ramas_ia.py", entrada='recomendar "imagenes" "clasificar" "sin imagenes"',
         esperado="Visión por computadora aparece como incompatible por la restricción escrita.",
         correr=lambda: ejecutar("mapa_ramas_ia.py", "--recomendar", "imagenes", "clasificar", "sin imagenes"),
         ok=lambda c, s: "Visión por computadora: incompatible" in s),
    # ---- Matriz de riesgos -------------------------------------------------
    dict(id="X-01", prog="matriz_riesgos_ia.py", entrada="P = 2, S = 3",
         esperado="R = 6 y revisión humana SÍ.",
         correr=lambda: ejecutar("matriz_riesgos_ia.py", "--probar", "2", "3"),
         ok=lambda c, s: "R=6" in s and "SÍ" in s),
    dict(id="X-02", prog="matriz_riesgos_ia.py", entrada="P = 4, S = 2",
         esperado="Rechaza P = 4 (código de salida 1).",
         correr=lambda: ejecutar("matriz_riesgos_ia.py", "--probar", "4", "2"),
         ok=lambda c, s: c == 1 and "RECHAZADO" in s),
    dict(id="X-03", prog="matriz_riesgos_ia.py", entrada="responsable vacío",
         esperado="Rechaza el campo «responsable» vacío (código de salida 1).",
         correr=lambda: ejecutar("matriz_riesgos_ia.py", "--responsable-vacio"),
         ok=lambda c, s: c == 1 and "responsable" in s and "RECHAZADO" in s),
    dict(id="X-04", prog="matriz_riesgos_ia.py", entrada="--demo (7 riesgos de BIB-01)",
         esperado="Orden: RSK-03, RSK-05, RSK-07, RSK-01, RSK-02, RSK-04, RSK-06 y CSV guardado.",
         correr=lambda: ejecutar("matriz_riesgos_ia.py", "--demo"),
         ok=lambda c, s: c == 0 and [l.split()[0] for l in s.splitlines() if l.startswith("RSK-")]
         == ["RSK-03", "RSK-05", "RSK-07", "RSK-01", "RSK-02", "RSK-04", "RSK-06"]
         and "Archivo guardado" in s),
    # ---- Mini modelo de lenguaje ------------------------------------------
    dict(id="L-01", prog="mini_modelo_lenguaje.py", entrada="corpus de 4 frases, inicio «biblioteca», semilla 1, límite 10",
         esperado="Antes del sorteo: abre 3/4 = 0.75 y cierra 1/4 = 0.25.",
         correr=lambda: ejecutar("mini_modelo_lenguaje.py", "--inicio", "biblioteca", "--semilla", "1",
                                 "--limite", "10", "--traza", traza("L-01")),
         ok=lambda c, s: "abre: 3/4 = 0.75" in s and "cierra: 1/4 = 0.25" in s),
    dict(id="L-02", prog="mini_modelo_lenguaje.py", entrada="corpus sin la cuarta frase, inicio «biblioteca»",
         esperado="abre 2/3 = 0.67 y cierra 1/3 = 0.33.",
         correr=lambda: ejecutar("mini_modelo_lenguaje.py", "--corpus", str(DATOS / "corpus_sin_cuarta_frase.txt"),
                                 "--inicio", "biblioteca", "--semilla", "1", "--limite", "10", "--traza", traza("L-02")),
         ok=lambda c, s: "abre: 2/3 = 0.67" in s and "cierra: 1/3 = 0.33" in s),
    dict(id="L-03", prog="mini_modelo_lenguaje.py", entrada="corpus vacío",
         esperado="Rechaza el corpus vacío antes de generar (código de salida 1).",
         correr=lambda: ejecutar("mini_modelo_lenguaje.py", "--corpus", str(DATOS / "corpus_vacio.txt"),
                                 "--inicio", "la", "--semilla", "1", "--limite", "10", "--traza", traza("L-03")),
         ok=lambda c, s: c == 1 and "Corpus vacío" in s),
    dict(id="L-04", prog="mini_modelo_lenguaje.py", entrada="inicio «museo» con corpus válido",
         esperado="Se detiene: motivo sin_continuacion; texto de una sola palabra.",
         correr=lambda: ejecutar("mini_modelo_lenguaje.py", "--inicio", "museo", "--semilla", "1",
                                 "--limite", "10", "--traza", traza("L-04")),
         ok=lambda c, s: "sin_continuacion" in s and texto_generado(s) == "museo"),
    dict(id="L-05", prog="mini_modelo_lenguaje.py", entrada="inicio «la», límite 2",
         esperado="Parada por límite con exactamente 2 palabras.",
         correr=lambda: ejecutar("mini_modelo_lenguaje.py", "--inicio", "la", "--semilla", "1",
                                 "--limite", "2", "--traza", traza("L-05")),
         ok=lambda c, s: "Motivo de parada: limite" in s and len(texto_generado(s).split()) == 2),
    dict(id="L-06", prog="mini_modelo_lenguaje.py", entrada="límite 0 (fuera del rango 1 a 50)",
         esperado="Rechaza el límite (código de salida 1).",
         correr=lambda: ejecutar("mini_modelo_lenguaje.py", "--inicio", "la", "--semilla", "1",
                                 "--limite", "0", "--traza", traza("L-06")),
         ok=lambda c, s: c == 1 and "El límite debe estar entre 1 y 50" in s),
    dict(id="L-07", prog="mini_modelo_lenguaje.py", entrada="inicio «la», semilla 1, límite 10",
         esperado="Texto de 1 a 10 palabras, solo palabras del corpus, parada por FIN o límite.",
         correr=lambda: ejecutar("mini_modelo_lenguaje.py", "--inicio", "la", "--semilla", "1",
                                 "--limite", "10", "--traza", traza("semilla_1")),
         ok=lambda c, s: c == 0 and 1 <= len(texto_generado(s).split()) <= 10
         and set(texto_generado(s).split()) <= {"la", "biblioteca", "abre", "cierra", "temprano", "tarde"}),
    dict(id="L-08", prog="mini_modelo_lenguaje.py", entrada="inicio «la», semilla 2, límite 10",
         esperado="Mismas condiciones que la semilla 1; los textos pueden coincidir o diferir.",
         correr=lambda: ejecutar("mini_modelo_lenguaje.py", "--inicio", "la", "--semilla", "2",
                                 "--limite", "10", "--traza", traza("semilla_2")),
         ok=lambda c, s: c == 0 and 1 <= len(texto_generado(s).split()) <= 10
         and set(texto_generado(s).split()) <= {"la", "biblioteca", "abre", "cierra", "temprano", "tarde"}),
    dict(id="L-09", prog="mini_modelo_lenguaje.py", entrada="semilla 1 repetida",
         esperado="Repetir la semilla 1 produce exactamente el mismo texto que L-07.",
         correr=lambda: ejecutar("mini_modelo_lenguaje.py", "--inicio", "la", "--semilla", "1",
                                 "--limite", "10", "--traza", traza("semilla_1_repetida")),
         ok=None),   # se comprueba con el resultado de L-07 (ver más abajo)
    dict(id="L-10", prog="mini_modelo_lenguaje.py", entrada="inicio «la», semilla 5, límite 10",
         esperado="Mismas condiciones que las semillas 1 y 2; se espera ver si otra semilla cambia el sorteo.",
         correr=lambda: ejecutar("mini_modelo_lenguaje.py", "--inicio", "la", "--semilla", "5",
                                 "--limite", "10", "--traza", traza("semilla_5")),
         ok=lambda c, s: c == 0 and 1 <= len(texto_generado(s).split()) <= 10
         and set(texto_generado(s).split()) <= {"la", "biblioteca", "abre", "cierra", "temprano", "tarde"}),
]


def main():
    inicio = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    registro = [f"REGISTRO DE PRUEBAS - ejecutado el {inicio}",
                f"Python {sys.version.split()[0]}", ""]
    resultados = {}
    cumple = 0
    for p in PRUEBAS:
        codigo, salida = p["correr"]()
        resultados[p["id"]] = (codigo, salida)
        if p["id"] == "L-09":
            ok = texto_generado(salida) == texto_generado(resultados["L-07"][1])
        else:
            ok = bool(p["ok"](codigo, salida))
        cumple += ok
        registro += [f"[{p['id']}] {p['prog']}",
                     f"  Entrada  : {p['entrada']}",
                     f"  Esperado : {p['esperado']}",
                     f"  Código de salida: {codigo}",
                     "  Obtenido :"] + ["    " + l for l in salida.splitlines()] + \
                    [f"  Resultado: {'CUMPLE' if ok else 'NO CUMPLE'}", ""]
    t7 = texto_generado(resultados["L-07"][1])
    t8 = texto_generado(resultados["L-08"][1])
    registro += ["COMPARACIÓN DE SEMILLAS",
                 f"  Semilla 1: {t7}", f"  Semilla 2: {t8}",
                 "  " + ("Semillas 1 y 2: los textos coinciden; eso no demuestra un error." if t7 == t8
                         else "Semillas 1 y 2: los textos difieren; la semilla cambió el sorteo."),
                 f"  Semilla 5: {texto_generado(resultados['L-10'][1])}",
                 "  " + ("Semillas 1 y 5: los textos coinciden." if t7 == texto_generado(resultados['L-10'][1])
                         else "Semillas 1 y 5: los textos difieren; otra semilla cambió el sorteo."), "",
                 f"RESUMEN: {cumple} de {len(PRUEBAS)} pruebas cumplen lo esperado."]
    ruta = EXPORT / "registro_pruebas.txt"
    ruta.write_text("\n".join(registro), encoding="utf-8")
    print("\n".join(registro))
    print(f"\nRegistro guardado en: {ruta}")
    raise SystemExit(0 if cumple == len(PRUEBAS) else 1)


if __name__ == "__main__":
    main()
