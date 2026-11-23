# Terraform y Ansible desde cero

Curso gratuito de **Terraform y Ansible para principiantes**, en español, publicado como web estática. A lo largo del curso se construye paso a paso un proyecto real: una web personal en AWS creada con Terraform y configurada con Ansible.

- 23 módulos (~50 h) en 4 partes: primeros pasos, Terraform, Ansible y todo junto.
- [Proyecto guiado](proyecto.html) de 22 pasos, con el código terminado en [`proyecto/`](proyecto/).
- Cada módulo: objetivos, lección con ejemplos de código y salidas de terminal, **paso del proyecto**, práctica guiada, comandos clave, errores frecuentes, **test autocorregido** y **retos con pista y solución**.
- Código de todas las prácticas en [`labs/`](labs/), validado automáticamente con GitHub Actions.
- [Chuleta de comandos](comandos.html) (Terraform, Ansible, SSH, terminal Bash/PowerShell, Git, AWS CLI, herramientas) con buscador y botón de copiar.
- [Glosario](glosario.html) y progreso del alumno guardado en el navegador.

El análisis completo del curso (público, decisiones, metodología, mapa del temario, costes, evaluación y hoja de ruta) está en [`docs/ANALISIS.md`](docs/ANALISIS.md).

## Ver la web en local

No necesita instalar nada: abre `index.html` en el navegador, o levanta un servidor:

```bash
python3 -m http.server 8000
```

y entra en http://localhost:8000.

## Publicar con GitHub Pages

1. En GitHub: **Settings → Pages**.
2. *Source*: **Deploy from a branch**, rama `main`, carpeta `/ (root)`.
3. La web quedará en `https://<tu-usuario>.github.io/terraform-course/`.

## Estructura

```
index.html        Portada, enfoque del curso y temario
comandos.html     Chuleta de comandos
glosario.html     Glosario
modulos/          Una página por módulo (00–22)
labs/             Código de las prácticas
proyecto/         Proyecto guiado terminado (Terraform + Ansible)
proyecto.html     Página del proyecto guiado
assets/           CSS, JS e imágenes
docs/             Análisis y diseño del curso
src/              Generador y contenido de las lecciones
```

## Cómo editar el contenido

Las páginas se generan a partir de `src/` (ver [`src/README.md`](src/README.md)):

1. Edita la lección, el test o los retos en `src/contenido/mNN.py` (o la ficha del módulo en `src/temario.py`).
2. Ejecuta `python3 src/build.py`.
3. Revisa la página en local y haz commit de los `.py` y de los `.html` generados.

## Laboratorios

El código de las prácticas está en [`labs/`](labs/). Un workflow de GitHub Actions comprueba en cada push el código de Terraform (`fmt`, `validate`, `test`) y el de Ansible (`ansible-lint`, idempotencia y una ejecución real del playbook del proyecto).
