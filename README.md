# Actividad 3 — Un asistente que se deja revisar

**Fundamentos de Inteligencia Artificial (E-FIA-3)**
Universidad Politécnica de Pachuca · Licenciatura en Ingeniería en Tecnologías de la Información e Innovación Digital

## Qué hay en este repositorio

Los tres programas del inciso e) del informe, los datos ficticios que usan y las salidas que generan al ejecutarse.

```
codigo/       mapa_ramas_ia.py · matriz_riesgos_ia.py · mini_modelo_lenguaje.py
              ejecutar_pruebas.py · generar_figuras.py
datos/        BIB-01-v1.txt · corpus_biblioteca.txt ·
              corpus_sin_cuarta_frase.txt · corpus_vacio.txt
exportacion/  registro_pruebas.txt · matriz_riesgos.csv · traza_*.csv
diagramas/    figura-2-mapa-ramas.svg · figura-3-recorrido-pregunta.svg
```

## Requisitos

Python 3. No hace falta instalar nada: los cuatro programas usan solo la biblioteca estándar.

Probado con Python 3.14.4.

## Cómo ejecutarlos

Abrir una terminal en la carpeta `codigo/`.

### Mapa de ramas de la IA

```bash
python mapa_ramas_ia.py --consulta "PLN"
python mapa_ramas_ia.py --consulta "Quantum"          # término no registrado
python mapa_ramas_ia.py --consulta ""                 # consulta vacía
python mapa_ramas_ia.py --recomendar "texto" "responder preguntas" ""
python mapa_ramas_ia.py --recomendar "" "" ""         # información insuficiente
python mapa_ramas_ia.py --recomendar "imagenes" "clasificar fotos" "sin imagenes"
python mapa_ramas_ia.py --mermaid                     # diagrama en formato Mermaid
python mapa_ramas_ia.py                                # menú de texto
```

### Matriz de riesgos de BIB-01

```bash
python matriz_riesgos_ia.py --demo                    # carga los 7 riesgos, ordena y exporta
python matriz_riesgos_ia.py --probar 2 3              # R = 6 y revisión humana
python matriz_riesgos_ia.py --probar 4 2              # rechaza P = 4
python matriz_riesgos_ia.py --responsable-vacio       # rechaza campo vacío
python matriz_riesgos_ia.py                           # menú de texto
```

### Mini modelo de lenguaje (bigramas)

```bash
python mini_modelo_lenguaje.py --inicio biblioteca --semilla 1 --limite 10
python mini_modelo_lenguaje.py --inicio museo --semilla 1 --limite 10
python mini_modelo_lenguaje.py --inicio la --semilla 2 --limite 10
python mini_modelo_lenguaje.py --inicio biblioteca --semilla 1 --limite 99
python mini_modelo_lenguaje.py --corpus ../datos/corpus_vacio.txt \
       --inicio biblioteca --semilla 1 --limite 10
python mini_modelo_lenguaje.py --corpus ../datos/corpus_sin_cuarta_frase.txt \
       --inicio biblioteca --semilla 7 --limite 10
```

El mini modelo **no es un LLM**: es un generador por conteos que elige la palabra siguiente mirando solo la anterior. Sus salidas no demuestran que un texto sea verdadero ni seguro.

## Reproducir las pruebas

`ejecutar_pruebas.py` ejecuta las 21 pruebas del inciso e) y compara cada resultado obtenido con el esperado, que está escrito en el propio script antes de ejecutar.

```bash
python ejecutar_pruebas.py
```

Deja `exportacion/registro_pruebas.txt` con la entrada, el esperado, el obtenido y el veredicto de cada prueba. Resultado de la última ejecución: **21 de 21 cumplen lo esperado**.

## Regenerar los diagramas

```bash
python generar_figuras.py ambas
```

Escribe `figura2.svg` y `figura3.svg`, que corresponden a la Figura 2 y la Figura 3 del informe.

## Datos

Todos los datos son ficticios y están señalados como tales.

- `BIB-01-v1.txt` — fuente del asistente: el préstamo dura siete días y la renovación se solicita en el mostrador antes del vencimiento. No menciona multas ni horarios.
- `corpus_biblioteca.txt` — cuatro frases para el modelo de bigramas, con una repetida a propósito.
- `corpus_sin_cuarta_frase.txt` — las mismas tres frases, para comprobar cómo cambia la proporción al quitar la repetida.
- `corpus_vacio.txt` — vacío, para probar que el programa rechaza un corpus sin frases.

Los identificadores personales que aparecen en las pruebas son inventados y están marcados como ficticios.

## Nota sobre la configuración

Las rutas son relativas a la carpeta del repositorio: los programas usan `../datos/`, así que deben ejecutarse desde `codigo/`.