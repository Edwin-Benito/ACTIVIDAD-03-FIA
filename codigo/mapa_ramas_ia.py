#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mapa_ramas_ia.py  -  Actividad 3, Fundamentos de IA (E-FIA-3)

Mapa de relaciones entre las ramas de la IA y su pertinencia para el
asistente BIB-01 (biblioteca ficticia). Todos los datos son didácticos.

USO
    python mapa_ramas_ia.py                         # menú de texto
    python mapa_ramas_ia.py --consulta "PLN"        # consulta directa
    python mapa_ramas_ia.py --consulta ""           # consulta vacía (se rechaza)
    python mapa_ramas_ia.py --recomendar "texto" "responder preguntas" ""
    python mapa_ramas_ia.py --mermaid               # diagrama para el informe

ENTRADA : un término (rama, técnica o concepto) o los datos de una tarea.
SALIDA  : ficha, conexiones y pertinencia; o un mensaje claro de por qué
          no se pudo responder ("término no registrado", "información
          insuficiente", "incompatible por restricción explícita").
"""

import argparse
import unicodedata

# ---------------------------------------------------------------------------
# 1. Fichas: un diccionario relaciona el nombre de cada rama con su información.
#    El orden es el de la Tabla 2 del material.
# ---------------------------------------------------------------------------
FICHAS = {
    "algoritmos evolutivos": {
        "nombre": "Algoritmos evolutivos",
        "tecnica": "Búsqueda y optimización con poblaciones de soluciones",
        "datos": ["soluciones candidatas", "restricciones", "medida de calidad"],
        "aplicaciones": [
            "turnos del mostrador de la biblioteca",
            "distribución de salas de estudio",
            "calendario de mantenimiento",
        ],
        "bib01": "No necesaria: BIB-01 no plantea un problema de optimización.",
        "alias": ["evolutivos", "algoritmo evolutivo", "algoritmos geneticos"],
    },
    "redes neuronales": {
        "nombre": "Redes neuronales",
        "tecnica": "Capas de operaciones con pesos que se ajustan con ejemplos",
        "datos": ["ejemplos de entrada con salida esperada (numéricos)"],
        "aplicaciones": [
            "reconocer dígitos manuscritos de una matrícula",
            "clasificar imágenes",
            "base de los modelos de lenguaje",
        ],
        "bib01": "Indirecta: un LLM se construye con ellas; el equipo no las entrena.",
        "alias": ["red neuronal", "redes neuronales artificiales"],
    },
    "logica difusa": {
        "nombre": "Lógica difusa",
        "tecnica": "Pertenencia gradual a categorías y reglas combinadas",
        "datos": ["valores medidos", "funciones de pertenencia", "reglas"],
        "aplicaciones": [
            "ventilación según ocupación de una sala",
            "control de un ventilador por temperatura",
            "regulación de iluminación",
        ],
        "bib01": "No necesaria: no hay magnitudes graduales que controlar (solo práctica del inciso b).",
        "alias": ["difusa", "fuzzy", "logica borrosa"],
    },
    "aprendizaje automatico": {
        "nombre": "Aprendizaje automático",
        "tecnica": "Ajuste de modelos a partir de datos",
        "datos": ["ejemplos con o sin etiqueta"],
        "aplicaciones": [
            "clasificar preguntas frecuentes por tema",
            "agrupar préstamos por patrón de uso",
            "predecir demanda de libros",
        ],
        "bib01": "Indirecta: es la base de los modelos de lenguaje que se emplearían.",
        "alias": ["machine learning", "ml", "aprendizaje de maquina"],
    },
    "vision por computadora": {
        "nombre": "Visión por computadora",
        "tecnica": "Análisis de imágenes y video",
        "datos": ["imágenes", "fotogramas de video"],
        "aplicaciones": [
            "detectar libros con la cubierta dañada",
            "contar ejemplares en un estante",
            "leer códigos de barras",
        ],
        "bib01": "No necesaria: las entradas de BIB-01 son preguntas en texto.",
        "alias": ["vision artificial", "vision computacional"],
    },
    "pln": {
        "nombre": "Procesamiento de lenguaje natural (PLN)",
        "tecnica": "Análisis y generación de lenguaje humano",
        "datos": ["texto dividido en tokens"],
        "aplicaciones": [
            "entender que dos preguntas con distinta redacción significan lo mismo",
            "clasificar consultas",
            "redactar respuestas con respaldo",
        ],
        "bib01": "Sí: la tarea es entender preguntas y redactar respuestas a partir de BIB-01.",
        "alias": ["procesamiento de lenguaje natural", "lenguaje natural", "nlp"],
    },
    "aprendizaje por reforzamiento": {
        "nombre": "Aprendizaje por reforzamiento",
        "tecnica": "Un agente aprende acciones mediante recompensas (p. ej. Q-Learning)",
        "datos": ["estados", "acciones", "recompensas"],
        "aplicaciones": [
            "robot simulado que lleva un libro a su estante",
            "agente que aprende a recorrer una cuadrícula",
            "juegos de estrategia",
        ],
        "bib01": "No necesaria: el asistente no aprende por recompensas.",
        "alias": ["reforzamiento", "refuerzo", "q-learning", "q learning", "rl"],
    },
}

# Nodos que no son ramas de la Tabla 2 pero aparecen en el mapa.
NODOS_EXTRA = {
    "sistemas difusos": "Sistemas que aplican lógica difusa para tomar decisiones.",
    "llm": "Modelo de lenguaje de gran tamaño; se relaciona con PLN y redes neuronales.",
    "bib-01": "Asistente de orientación de una biblioteca ficticia (caso de uso).",
}
ALIAS_EXTRA = {
    "sistema difuso": "sistemas difusos",
    "modelo de lenguaje": "llm",
    "bib01": "bib-01",
    "asistente": "bib-01",
}

# ---------------------------------------------------------------------------
# 2. Grafo: puntos (nodos) unidos por enlaces que explican la relación.
#    Cada enlace es (origen, destino, explicación).
# ---------------------------------------------------------------------------
ENLACES = [
    ("logica difusa", "sistemas difusos", "los sistemas difusos aplican la lógica difusa"),
    ("aprendizaje por reforzamiento", "aprendizaje automatico", "es un paradigma del aprendizaje automático"),
    ("redes neuronales", "aprendizaje automatico", "se estudian dentro del aprendizaje automático"),
    ("llm", "redes neuronales", "se construye con redes neuronales"),
    ("llm", "pln", "se usa para tareas de PLN"),
    ("vision por computadora", "redes neuronales", "suele apoyarse en redes neuronales"),
    ("bib-01", "llm", "el asistente propuesto usaría un LLM"),
]

# ---------------------------------------------------------------------------
# 3. Restricciones explícitas que sí permiten declarar incompatibilidad.
#    Solo se declara incompatibilidad si la restricción aparece escrita.
# ---------------------------------------------------------------------------
INCOMPATIBLES = {
    "sin datos etiquetados": ["redes neuronales", "aprendizaje automatico"],
    "sin imagenes": ["vision por computadora"],
    "sin recompensa": ["aprendizaje por reforzamiento"],
}

# Palabras clave que orientan la recomendación (entrada/tarea -> rama).
PISTAS = {
    "pln": ["texto", "pregunta", "lenguaje", "idioma", "redactar", "token"],
    "vision por computadora": ["imagen", "imagenes", "foto", "video", "camara"],
    "algoritmos evolutivos": ["optimizar", "horario", "turnos", "poblacion", "calendario"],
    "aprendizaje por reforzamiento": ["recompensa", "agente", "accion", "acciones", "entorno"],
    "logica difusa": ["temperatura", "gradual", "regla", "ocupacion", "ventilador"],
    "aprendizaje automatico": ["etiquetado", "etiquetados", "clasificar", "predecir", "ejemplos"],
}


def normalizar(texto):
    """Minúsculas, sin acentos y sin espacios sobrantes."""
    texto = unicodedata.normalize("NFD", texto.lower().strip())
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


def buscar_nodo(consulta):
    """Devuelve la clave del nodo que coincide con la consulta, o None."""
    q = normalizar(consulta)
    if q in FICHAS or q in NODOS_EXTRA:
        return q
    if q in ALIAS_EXTRA:
        return ALIAS_EXTRA[q]
    for clave, ficha in FICHAS.items():
        if q == normalizar(ficha["nombre"]) or q in [normalizar(a) for a in ficha["alias"]]:
            return clave
    return None


def nombre_visible(clave):
    return FICHAS[clave]["nombre"] if clave in FICHAS else clave.upper() if clave in ("llm",) else clave.capitalize()


def vecinos(clave):
    """Lista de (otro nodo, explicación) conectados con el nodo dado."""
    salida = []
    for a, b, texto in ENLACES:
        if a == clave:
            salida.append((b, texto))
        elif b == clave:
            salida.append((a, texto))
    return salida


def consultar(consulta):
    """Devuelve el texto de respuesta a una consulta sobre el mapa."""
    if not consulta or not consulta.strip():
        return "Consulta vacía: escriba el nombre de una rama, técnica o concepto."
    clave = buscar_nodo(consulta)
    if clave is None:
        return f"Término no registrado: «{consulta.strip()}». Pruebe con una rama de la Tabla 2."
    lineas = []
    if clave in FICHAS:
        f = FICHAS[clave]
        lineas.append(f"== {f['nombre']} ==")
        lineas.append(f"Técnica       : {f['tecnica']}")
        lineas.append(f"Datos         : {', '.join(f['datos'])}")
        lineas.append("Aplicaciones  : " + "; ".join(f["aplicaciones"]))
        lineas.append(f"Para BIB-01   : {f['bib01']}")
    else:
        lineas.append(f"== {nombre_visible(clave)} ==")
        lineas.append(NODOS_EXTRA[clave])
    conex = vecinos(clave)
    if conex:
        lineas.append("Conexiones:")
        for otro, texto in conex:
            lineas.append(f"  - {nombre_visible(otro)}: {texto}")
    else:
        lineas.append("Conexiones: ninguna registrada (no implica incompatibilidad).")
    return "\n".join(lineas)


def recomendar(entrada, tarea, restricciones):
    """
    Explica qué rama sirve según entrada, tarea y restricciones.
    - Sin pistas suficientes -> 'información insuficiente'.
    - Solo se declara incompatibilidad por una restricción escrita.
    """
    if not (entrada.strip() or tarea.strip()):
        return "Información insuficiente: indique al menos la entrada o la tarea."
    texto = normalizar(entrada + " " + tarea)
    candidatas = [r for r, claves in PISTAS.items() if any(c in texto.split() or c in texto for c in claves)]
    if not candidatas:
        return "Información insuficiente: no hay datos para recomendar una rama."
    rest = normalizar(restricciones)
    respuestas = []
    for rama in candidatas:
        motivo = next((r for r, ramas in INCOMPATIBLES.items() if r in rest and rama in ramas), None)
        nombre = FICHAS[rama]["nombre"]
        if motivo:
            respuestas.append(f"{nombre}: incompatible por la restricción explícita «{motivo}».")
        else:
            respuestas.append(f"{nombre}: sirve para esta tarea ({FICHAS[rama]['tecnica']}).")
    return "\n".join(respuestas)


def mermaid():
    """Genera el diagrama del mapa en formato Mermaid para el informe."""
    ids = {}
    lineas = ["flowchart TD"]
    todos = list(FICHAS) + list(NODOS_EXTRA)
    for i, clave in enumerate(todos):
        ids[clave] = f"N{i}"
        lineas.append(f'    N{i}["{nombre_visible(clave)}"]')
    for a, b, texto in ENLACES:
        lineas.append(f'    {ids[a]} -->|"{texto}"| {ids[b]}')
    return "\n".join(lineas)


def menu():
    """Menú de texto para recorrer el mapa."""
    while True:
        print("\n--- Mapa de ramas de IA ---")
        print("1) Consultar un término   2) Recomendar rama   3) Listar ramas")
        print("4) Mostrar diagrama Mermaid   0) Salir")
        op = input("Opción: ").strip()
        if op == "1":
            print(consultar(input("Término: ")))
        elif op == "2":
            e = input("Entrada (datos): ")
            t = input("Tarea: ")
            r = input("Restricciones (vacío si no hay): ")
            print(recomendar(e, t, r))
        elif op == "3":
            for f in FICHAS.values():
                print("-", f["nombre"])
        elif op == "4":
            print(mermaid())
        elif op == "0":
            break
        else:
            print("Opción no válida.")


def main():
    p = argparse.ArgumentParser(description="Mapa de relaciones de ramas de IA (BIB-01)")
    p.add_argument("--consulta", help="término a consultar (puede ir vacío)")
    p.add_argument("--recomendar", nargs=3, metavar=("ENTRADA", "TAREA", "RESTRICCIONES"))
    p.add_argument("--mermaid", action="store_true", help="imprime el diagrama Mermaid")
    a = p.parse_args()
    if a.consulta is not None:
        print(consultar(a.consulta))
    elif a.recomendar:
        print(recomendar(*a.recomendar))
    elif a.mermaid:
        print(mermaid())
    else:
        menu()


if __name__ == "__main__":
    main()
