# Terraform desde cero

Curso gratuito de **Terraform para principiantes**, en español, publicado como web estática.

- 16 módulos (~35 h) organizados en 4 fases: fundamentos → construir → escalar → profesional.
- Cada módulo: objetivos, contenido, ejemplo, práctica guiada, comandos clave, errores frecuentes y autoevaluación.
- [Chuleta de comandos](comandos.html) (Terraform, terminal Bash/PowerShell, Git, AWS CLI, herramientas) con buscador y botón de copiar.
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
modulos/          Una página por módulo (00–15)
labs/             Código de las prácticas
assets/           CSS, JS e imágenes
docs/             Análisis y diseño del curso
```

## Cómo añadir contenido a un módulo

Cada página de `modulos/` ya tiene el guion. Para desarrollar la lección, busca el comentario
`<!-- ESCRIBE AQUÍ LA LECCIÓN -->`, añade un `<h3>` por cada punto del contenido y elimina el aviso «Lección en desarrollo».

Para bloques de código usa:

```html
<figure class="code"><figcaption><span>main.tf</span><button class="copy" type="button">Copiar</button></figcaption>
<pre><code class="language-hcl">resource "random_pet" "x" {}</code></pre></figure>
```
