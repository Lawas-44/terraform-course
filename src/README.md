# Generador del sitio

Las páginas HTML de `modulos/`, `index.html`, `comandos.html` y `glosario.html` **se generan** con:

```bash
python3 src/build.py
```

No edites esos HTML a mano: edita estos archivos y vuelve a generar.

| Archivo | Contenido |
|---|---|
| `temario.py` | Ficha de cada módulo: título, nivel, duración, objetivos, práctica guiada, comandos y errores frecuentes |
| `contenido/mNN.py` | Lección (`LECCION`), test (`TEST`) y retos (`RETOS`) del módulo NN |
| `extra.py` | Chuleta de comandos, errores comunes y glosario |
| `build.py` | Plantillas HTML |

## Bloques de una lección

`LECCION` es una lista de tuplas:

```python
("h", "Título de apartado")                 # crea un apartado y una entrada en el índice
("p", "Texto con `código`, **negrita** y *cursiva*")
("ul", ["elemento", "elemento"])           # lista; ("ol", [...]) para numerada
("code", "hcl", "main.tf", """código""")    # lenguajes: hcl, bash, yaml, json, text
("term", """$ terraform plan\n...""")       # salida de terminal
("tip", "consejo"), ("info", "nota"), ("warn", "advertencia")
("table", ["Cabecera", ...], [["fila", ...], ...])
("html", "<p>HTML a mano</p>")
```

## Test

```python
TEST = [
  ("Pregunta", ["opción A", "opción B", "opción C", "opción D"], 1, "Explicación"),
]  # el 1 es el índice (desde 0) de la respuesta correcta
```

## Retos

```python
RETOS = [{
  "titulo": "...", "enunciado": "...",
  "codigo": ("hcl", "..."),        # opcional
  "pista": "...",                  # opcional
  "solucion": ("hcl", "..."),
}]
```
