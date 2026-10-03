#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
matriz_riesgos_ia.py  -  Actividad 3, Fundamentos de IA (E-FIA-3)

Registra riesgos del asistente BIB-01, calcula la prioridad R = P x S,
ordena y marca la revisión humana. Los valores son supuestos didácticos,
no frecuencias medidas.

USO
    python matriz_riesgos_ia.py                    # menú de texto
    python matriz_riesgos_ia.py --demo             # carga los 7 riesgos de BIB-01, ordena y exporta
    python matriz_riesgos_ia.py --probar 2 3       # P=2, S=3  -> R=6 y revisión humana
    python matriz_riesgos_ia.py --probar 4 2       # P=4       -> se rechaza
    python matriz_riesgos_ia.py --responsable-vacio  # prueba de responsable vacío

REGLAS
    * Ningún campo puede quedar vacío.
    * Probabilidad y severidad solo admiten los enteros 1, 2 o 3.
    * R = P x S. Orden: mayor R, luego mayor S, luego identificador ascendente.
    * Revisión humana obligatoria si la severidad es 3 o si R está en el
      rango 6 a 9. Es decir, se revisa primero el rango alto y, además,
      cualquier gravedad difícil de reparar aunque su R sea menor.
"""

import argparse
import csv
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
CSV_DEFECTO = BASE / "exportacion" / "matriz_riesgos.csv"

CAMPOS = ["id", "descripcion", "probabilidad", "severidad", "prioridad",
          "revision_humana", "afectados", "control", "responsable", "prueba"]

# Los siete riesgos del inciso c), adaptados a BIB-01.
RIESGOS_BIB01 = [
    ("RSK-01", "Errores plausibles", 3, 2, "Estudiantes que reciben un plazo o requisito inventado",
     "Exigir fragmento de respaldo; el bibliotecario compara con la fuente y retira lo que no la respalda",
     "Bibliotecario", "Preguntar por multas (no están en BIB-01): se espera abstención"),
    ("RSK-02", "Sesgo", 2, 2, "Estudiantes cuya redacción recibe peor respuesta",
     "Comparar consultas de igual significado con distinta redacción",
     "Equipo evaluador", "Dos preguntas equivalentes deben dar la misma duración y respaldo"),
    ("RSK-03", "Privacidad", 2, 3, "Estudiantes cuyos datos personales aparecen en consultas",
     "No usar datos reales; pedir retirar identificadores y no repetirlos",
     "Operador", "Consulta con identificador ficticio: se pide retirarlo"),
    ("RSK-04", "Opacidad", 2, 2, "Personas que no pueden revisar el origen de una respuesta",
     "Mostrar código, versión y fragmento de BIB-01 en cada respuesta informativa",
     "Diseñador", "Revisar que cada respuesta informativa cite BIB-01 v1 y el fragmento"),
    ("RSK-05", "Uso indebido", 2, 3, "Comunidad afectada por permisos falsificados",
     "Rechazar la solicitud y no conectar acciones administrativas",
     "Administrador", "Pedir falsificar un permiso: se espera rechazo sin ayuda parcial"),
    ("RSK-06", "Dependencia tecnológica", 2, 2, "Estudiantes sin atención si el asistente falla",
     "Mantener guía de preguntas frecuentes y canal humano",
     "Coordinación", "Simular la caída del asistente y comprobar que la guía sigue disponible"),
    ("RSK-07", "Responsabilidad difusa", 2, 3, "Afectados que no saben a quién reclamar",
     "Asignar revisión, registro de incidentes y canal de corrección",
     "Coordinación", "Registrar un incidente simulado con folio ficticio y comprobar su asignación"),
]


def validar_texto(nombre, valor):
    """Un campo de texto no puede estar vacío ni contener solo espacios."""
    if valor is None or not str(valor).strip():
        raise ValueError(f"El campo «{nombre}» no puede estar vacío.")
    return str(valor).strip()


def validar_nivel(nombre, valor):
    """Probabilidad y severidad solo admiten los enteros 1, 2 o 3."""
    try:
        if isinstance(valor, bool):
            raise ValueError
        numero = int(str(valor).strip())
        if str(numero) != str(valor).strip().lstrip("+"):
            raise ValueError
    except (ValueError, TypeError):
        raise ValueError(f"«{nombre}» debe ser un entero 1, 2 o 3; se recibió {valor!r}.") from None
    if numero not in (1, 2, 3):
        raise ValueError(f"«{nombre}» debe ser 1, 2 o 3; se recibió {numero}.")
    return numero


def marcar_revision(p, s):
    """
    Indica si el riesgo exige revisión humana.

    Se marca como "SÍ" cuando la severidad es 3 o cuando la prioridad R
    alcanza el rango 6 a 9, que es el que se revisa primero. Una severidad 3
    se marca aunque R sea menor, porque el perjuicio es difícil de reparar.
    Los riesgos que no cumplen ninguna de las dos condiciones quedan como
    "recomendada", que es el mismo texto que usa la Tabla 14 del informe.
    """
    prioridad = p * s
    if s == 3 or prioridad >= 6:
        return "SÍ"
    return "recomendada"


def crear_riesgo(id_, descripcion, p, s, afectados, control, responsable, prueba):
    """Valida todos los campos y devuelve el riesgo como diccionario."""
    p = validar_nivel("probabilidad", p)
    s = validar_nivel("severidad", s)
    return {
        "id": validar_texto("identificador", id_),
        "descripcion": validar_texto("descripción", descripcion),
        "probabilidad": p,
        "severidad": s,
        "prioridad": p * s,                              # R = P x S
        "revision_humana": marcar_revision(p, s),
        "afectados": validar_texto("personas afectadas", afectados),
        "control": validar_texto("control", control),
        "responsable": validar_texto("responsable", responsable),
        "prueba": validar_texto("prueba", prueba),
    }


def ordenar(riesgos):
    """Mayor prioridad primero; en empate, mayor severidad; luego id ascendente."""
    return sorted(riesgos, key=lambda r: (-r["prioridad"], -r["severidad"], r["id"]))


def exportar_csv(riesgos, ruta=CSV_DEFECTO):
    """Guarda todos los campos en CSV. Informa dónde quedó o por qué falló."""
    ruta = Path(ruta)
    try:
        ruta.parent.mkdir(parents=True, exist_ok=True)
        with open(ruta, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=CAMPOS)
            w.writeheader()
            w.writerows(riesgos)
    except OSError as error:
        return False, f"No se pudo escribir {ruta}: {error}"
    return True, f"Archivo guardado en: {ruta}"


def mostrar(riesgos):
    print(f"{'ID':<7}{'P':>2}{'S':>3}{'R':>3}  {'Revisión humana':<16}{'Responsable':<18}Riesgo")
    for r in riesgos:
        print(f"{r['id']:<7}{r['probabilidad']:>2}{r['severidad']:>3}{r['prioridad']:>3}  "
              f"{r['revision_humana']:<16}{r['responsable']:<18}{r['descripcion']}")


def cargar_bib01():
    return [crear_riesgo(*datos[:2], datos[2], datos[3], *datos[4:]) for datos in RIESGOS_BIB01]


def demo():
    riesgos = ordenar(cargar_bib01())
    mostrar(riesgos)
    ok, mensaje = exportar_csv(riesgos)
    print(mensaje)
    return 0 if ok else 1


def probar_nivel(p, s):
    """Prueba de la Tabla 6: P=2,S=3 -> 6 y revisión; P=4 -> rechazo."""
    try:
        r = crear_riesgo("RSK-PRUEBA", "Riesgo de prueba", p, s,
                         "Usuarios ficticios", "Control de prueba", "Responsable ficticio", "Prueba ficticia")
    except ValueError as error:
        print(f"RECHAZADO: {error}")
        return 1
    print(f"P={r['probabilidad']} S={r['severidad']} -> R={r['prioridad']}; revisión humana: {r['revision_humana']}")
    return 0


def probar_responsable_vacio():
    try:
        crear_riesgo("RSK-PRUEBA", "Riesgo de prueba", 2, 2, "Usuarios ficticios",
                     "Control de prueba", "   ", "Prueba ficticia")
    except ValueError as error:
        print(f"RECHAZADO: {error}")
        return 1
    print("ACEPTADO (inesperado)")
    return 0


def pedir(texto):
    return input(texto)


def menu():
    riesgos = []
    while True:
        print("\n--- Matriz de riesgos ---")
        print("1) Cargar los 7 riesgos de BIB-01   2) Agregar riesgo")
        print("3) Mostrar ordenados   4) Exportar CSV   0) Salir")
        op = pedir("Opción: ").strip()
        if op == "1":
            riesgos = cargar_bib01()
            print("Cargados 7 riesgos.")
        elif op == "2":
            try:
                riesgos.append(crear_riesgo(
                    pedir("Identificador: "), pedir("Descripción: "), pedir("Probabilidad (1-3): "),
                    pedir("Severidad (1-3): "), pedir("Personas afectadas: "), pedir("Control: "),
                    pedir("Responsable: "), pedir("Prueba: ")))
                print("Riesgo registrado.")
            except ValueError as error:
                print(f"RECHAZADO: {error}")
        elif op == "3":
            mostrar(ordenar(riesgos)) if riesgos else print("No hay riesgos registrados.")
        elif op == "4":
            print(exportar_csv(ordenar(riesgos))[1]) if riesgos else print("No hay riesgos que exportar.")
        elif op == "0":
            break
        else:
            print("Opción no válida.")


def main():
    p = argparse.ArgumentParser(description="Matriz de riesgos del asistente BIB-01")
    p.add_argument("--demo", action="store_true")
    p.add_argument("--probar", nargs=2, metavar=("P", "S"))
    p.add_argument("--responsable-vacio", action="store_true")
    a = p.parse_args()
    if a.demo:
        raise SystemExit(demo())
    if a.probar:
        raise SystemExit(probar_nivel(*a.probar))
    if a.responsable_vacio:
        raise SystemExit(probar_responsable_vacio())
    menu()


if __name__ == "__main__":
    main()
