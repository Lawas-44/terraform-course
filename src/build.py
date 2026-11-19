# -*- coding: utf-8 -*-
"""Genera las páginas HTML del curso a partir de src/temario.py, src/extra.py y src/contenido/."""
import html, importlib, os, random, re, sys, unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from temario import MODULOS
from extra import COMANDOS, ERRORES_COMUNES, GLOSARIO

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = "https://github.com/lawas-44/terraform-course"

FASES = [
    ("Fase 1 · Fundamentos", "Del cero absoluto a tu primer recurso en la nube.", ["00", "01", "02", "03", "04", "05"]),
    ("Fase 2 · Construir infraestructura", "Recursos reales, repetición y lógica.", ["06", "07", "08"]),
    ("Fase 3 · Escalar y mantener", "Estado, entornos, reutilización y código heredado.", ["09", "10", "11", "12"]),
    ("Fase 4 · Nivel profesional", "Calidad, automatización y proyecto final.", ["13", "14", "15"]),
]

# ---------------------------------------------------------------- utilidades

def esc(s):
    return html.escape(s, quote=True)


def fmt(s):
    """Texto con `código`, **negrita**, *cursiva* y <kbd>."""
    s = html.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*([A-Za-zÁÉÍÓÚáéíóúñ«][^*<>]*?)\*(?![\w*])", r"<em>\1</em>", s)
    return s.replace("&lt;kbd&gt;", "<kbd>").replace("&lt;/kbd&gt;", "</kbd>")


def slug(s):
    s = unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def mod_url(m, root):
    return f"{root}modulos/{m['num']}-{m['slug']}.html"


ICON_MENU = '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round"/></svg>'
ICON_TEMA = '<svg viewBox="0 0 24 24" width="17" height="17" aria-hidden="true"><circle cx="12" cy="12" r="8.5" fill="none" stroke="currentColor" stroke-width="2"/><path d="M12 3.5a8.5 8.5 0 0 1 0 17z" fill="currentColor"/></svg>'

# ---------------------------------------------------------------- bloques de código

LANGS = {"hcl": "language-hcl", "yaml": "language-yaml", "bash": "language-bash", "json": "language-json"}


def term_window(title, inner, copy_text=None):
    data = f' data-copy="{esc(copy_text)}"' if copy_text else ""
    return (f'<figure class="term-win"><div class="term-bar"><span class="dots" aria-hidden="true"><i></i><i></i><i></i></span>'
            f'<span class="term-title">{esc(title)}</span>'
            f'<button class="copy" type="button"{data}>Copiar</button></div>'
            f'<pre>{inner}</pre></figure>')


def code_block(lang, name, code):
    cls = LANGS.get(lang)
    attr = f' class="{cls}"' if cls else ' class="plain"'
    return term_window(name, f"<code{attr}>{html.escape(code, quote=False)}</code>")


def terminal_output(text):
    """Salida de terminal: las líneas que empiezan por '$ ' son comandos (solo esas se copian)."""
    lines, cmds = [], []
    for line in text.split("\n"):
        if line.startswith("$ "):
            cmds.append(line[2:])
            lines.append(f'<span class="prompt">$ </span><span class="cmdline">{html.escape(line[2:], quote=False)}</span>')
        else:
            lines.append(f'<span class="out">{html.escape(line, quote=False)}</span>')
    return term_window("terminal", '<code class="plain">' + "\n".join(lines) + "</code>", copy_text="\n".join(cmds))

# ---------------------------------------------------------------- plantilla común


def sidebar(root, actual=None, toc=None):
    """Menú lateral: progreso del curso + módulos por fase + referencia."""
    by = {m["num"]: m for m in MODULOS}
    h = [f'''<div class="progress-box" aria-live="polite">
  <div class="label"><span>Progreso del curso</span><span class="js-pct">0 %</span></div>
  <div class="bar"><span class="fill js-fill"></span></div>
  <small class="js-count">0 de {len(MODULOS)} módulos completados</small>
</div>
<nav aria-label="Contenido del curso">
<ul class="sb-list"><li><a class="sb-link" href="{root}index.html"{' aria-current="page"' if actual == "inicio" else ''}><span class="num"></span><span class="t">Inicio</span></a></li></ul>''']
    for titulo, _, nums in FASES:
        h.append(f'<p class="sb-group">{esc(titulo)}</p><ul class="sb-list">')
        for n in nums:
            m = by[n]
            cur = ' aria-current="page"' if actual == n else ""
            h.append(f'<li><a class="sb-link" data-mod="{n}" href="{mod_url(m, root)}"{cur}>'
                     f'<span class="num">{n}</span><span class="t">{fmt(m["titulo"])}</span><span class="st" aria-hidden="true"></span></a>')
            if actual == n and toc:
                h.append(render_toc(toc))
            h.append("</li>")
        h.append("</ul>")
    ref = [("comandos", f"{root}comandos.html", "Chuleta de comandos"), ("glosario", f"{root}glosario.html", "Glosario"),
           ("labs", f"{REPO}/tree/main/labs", "Código de las prácticas"), ("github", REPO, "Repositorio en GitHub")]
    h.append('<p class="sb-group">Referencia</p><ul class="sb-list">')
    for k, href, t in ref:
        cur = ' aria-current="page"' if actual == k else ""
        h.append(f'<li><a class="sb-link" href="{href}"{cur}><span class="num"></span><span class="t">{t}</span></a>')
        if actual == k and toc:
            h.append(render_toc(toc))
        h.append("</li>")
    h.append("</ul></nav>")
    return "\n".join(h)


def render_toc(toc):
    h = ['<ul class="sb-toc">']
    for anchor, label, sub in toc:
        h.append(f'<li><a href="#{anchor}">{fmt(label)}</a>')
        if sub:
            h.append('<ul class="sb-toc">' + "".join(f'<li><a href="#{a}">{fmt(t)}</a></li>' for a, t in sub) + "</ul>")
        h.append("</li>")
    h.append("</ul>")
    return "".join(h)


def page(title, body, root, actual, desc, toc=None, wide=False):
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="icon" href="{root}assets/img/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{root}assets/css/styles.css">
<script>try{{var t=localStorage.getItem('tema');if(t)document.documentElement.dataset.theme=t;}}catch(e){{}}</script>
</head>
<body>
<a class="skip" href="#contenido">Saltar al contenido</a>
<header class="topbar">
  <button class="icon-btn menu-toggle" type="button" aria-label="Abrir menú" aria-controls="sidebar" aria-expanded="false">{ICON_MENU}</button>
  <a class="brand" href="{root}index.html"><span class="logo" aria-hidden="true">tf</span><span class="brand-text">Terraform desde cero</span></a>
  <span class="spacer"></span>
  <div class="top-progress" title="Progreso del curso" aria-hidden="true"><span class="js-pct">0 %</span><div class="bar"><span class="fill js-fill"></span></div></div>
  <button class="icon-btn theme-toggle" type="button" aria-label="Cambiar tema claro u oscuro" title="Cambiar tema">{ICON_TEMA}</button>
</header>
<div class="layout">
<aside class="sidebar" id="sidebar">
{sidebar(root, actual, toc)}
</aside>
<div class="overlay" aria-hidden="true"></div>
<main class="content" id="contenido">
<div class="content-inner{' wide' if wide else ''}">
{body}
<footer class="site-footer">Curso abierto de Terraform para principiantes. Código en <a href="{REPO}">GitHub</a>. Terraform es una marca de HashiCorp; este curso no está afiliado.</footer>
</div>
</main>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-hcl.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-yaml.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-bash.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-json.min.js"></script>
<script src="{root}assets/js/main.js"></script>
</body>
</html>
"""


def cmd_row(c, d):
    return (f'<tr><td><code class="cmd">{esc(c)}</code></td><td>{fmt(d)}</td>'
            f'<td class="copy-cell"><button class="copy" type="button" data-copy="{esc(c)}" aria-label="Copiar comando">Copiar</button></td></tr>')


def cmd_table(rows):
    return ('<div class="table-wrap"><table class="cmds"><thead><tr>'
            '<th>Comando</th><th>Qué hace</th><th><span class="sr-only">Copiar</span></th></tr></thead><tbody>'
            + "".join(cmd_row(c, d) for c, d in rows) + "</tbody></table></div>")

# ---------------------------------------------------------------- módulos


def render_blocks(blocks):
    out, toc = [], []
    for b in blocks:
        k = b[0]
        if k == "h":
            sid = slug(b[1])
            toc.append((sid, b[1]))
            out.append(f'<h3 id="{sid}">{fmt(b[1])}</h3>')
        elif k == "p":
            out.append(f"<p>{fmt(b[1])}</p>")
        elif k in ("ul", "ol"):
            out.append(f"<{k}>" + "".join(f"<li>{fmt(x)}</li>" for x in b[1]) + f"</{k}>")
        elif k == "code":
            out.append(code_block(b[1], b[2], b[3]))
        elif k == "term":
            out.append(terminal_output(b[1]))
        elif k in ("tip", "warn", "info"):
            label = {"tip": "Consejo", "warn": "Importante", "info": "Nota"}[k]
            cls = {"tip": "tip", "warn": "aviso", "info": ""}[k]
            out.append(f'<div class="callout {cls}"><span class="k">{label}</span>{fmt(b[1])}</div>')
        elif k == "table":
            head = "".join(f"<th>{fmt(x)}</th>" for x in b[1])
            rows = "".join("<tr>" + "".join(f"<td>{fmt(c)}</td>" for c in r) + "</tr>" for r in b[2])
            out.append(f'<div class="table-wrap"><table><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>')
        elif k == "html":
            out.append(b[1])
        else:
            raise ValueError(f"Bloque desconocido: {k}")
    return "\n".join(out), toc


def render_test(num, test):
    letras = "ABCD"
    qs = []
    for n, (q, opts, ok, exp) in enumerate(test, 1):
        # Barajado determinista: la respuesta correcta no cae siempre en la misma letra
        orden = list(range(len(opts)))
        random.Random(f"{num}-{n}").shuffle(orden)
        opts = [opts[j] for j in orden]
        ok = orden.index(ok)
        bts = "".join(f'<button type="button" class="opt" data-i="{i}"><span class="letra">{letras[i]}</span><span class="txt">{fmt(o)}</span></button>'
                      for i, o in enumerate(opts))
        qs.append(f'<fieldset class="q" data-ok="{ok}"><legend><span class="qn">{n:02d}</span><span class="txt">{fmt(q)}</span></legend>'
                  f'<div class="opts">{bts}</div><p class="exp" hidden><strong class="verdict"></strong> {fmt(exp)}</p></fieldset>')
    return (f'<div class="quiz" data-mod="{num}" data-total="{len(test)}">' + "".join(qs)
            + '<div class="quiz-foot"><p class="quiz-result" aria-live="polite">Responde todas las preguntas para ver tu nota.</p>'
              '<button type="button" class="btn small quiz-reset">Reintentar</button></div></div>')


def render_retos(retos):
    out = []
    for n, r in enumerate(retos, 1):
        h = f'<article class="reto"><h3>Reto {n}. {fmt(r["titulo"])}</h3><p>{fmt(r["enunciado"])}</p>'
        if r.get("codigo"):
            h += code_block(r["codigo"][0], "código del reto", r["codigo"][1])
        if r.get("pista"):
            h += f'<details><summary>Ver pista</summary><p>{fmt(r["pista"])}</p></details>'
        lang, code = r["solucion"]
        h += f'<details><summary>Ver solución</summary>{code_block(lang, "solución", code)}</details></article>'
        out.append(h)
    return "\n".join(out)


def modulo_page(i, m):
    root = "../"
    prev_m = MODULOS[i - 1] if i > 0 else None
    next_m = MODULOS[i + 1] if i < len(MODULOS) - 1 else None
    cont = importlib.import_module(f"contenido.m{m['num']}")
    leccion_html, lec_toc = render_blocks(cont.LECCION)

    toc = [("objetivos", "Objetivos", None), ("leccion", "Lección", lec_toc), ("practica", "Práctica guiada", None)]
    if m["comandos"]:
        toc.append(("comandos", "Comandos clave", None))
    toc += [("errores", "Errores frecuentes", None), ("test", "Test", None), ("retos", "Retos", None)]

    p = [f"""<nav class="breadcrumb" aria-label="Ruta"><a href="../index.html#temario">Temario</a> / Módulo {m['num']}</nav>
<header class="mod-head">
  <p class="eyebrow">Módulo {m['num']}</p>
  <h1>{fmt(m['titulo'])}</h1>
  <p class="lead">{fmt(m['resumen'])}</p>
  <div class="meta-row"><span>Nivel: {m['nivel']}</span><span>Duración: {m['duracion']}</span><span>Test: {len(cont.TEST)} preguntas</span><span>Retos: {len(cont.RETOS)}</span></div>
</header>"""]
    p.append('<section id="objetivos"><h2>Objetivos</h2><p>Al terminar este módulo sabrás:</p><ul class="check">'
             + "".join(f"<li>{fmt(o)}</li>" for o in m["objetivos"]) + "</ul></section>")
    p.append(f'<section id="leccion"><h2>Lección</h2>{leccion_html}</section>')
    lab = m["lab"]
    aviso = ('<div class="callout aviso"><span class="k">Importante</span>Si has creado recursos en la nube, ejecuta '
             '<code>terraform destroy</code> al terminar para no pagar por ellos.</div>') if int(m["num"]) >= 5 else ""
    p.append(f'<section id="practica"><h2>Práctica guiada</h2><p><strong>{fmt(lab["titulo"])}</strong></p><ol class="pasos">'
             + "".join(f"<li>{fmt(x)}</li>" for x in lab["pasos"]) + f"</ol>{aviso}</section>")
    if m["comandos"]:
        p.append(f'<section id="comandos"><h2>Comandos clave</h2>{cmd_table(m["comandos"])}</section>')
    p.append('<section id="errores"><h2>Errores frecuentes</h2><dl class="errores">'
             + "".join(f"<div><dt>{fmt(e)}</dt><dd>{fmt(s)}</dd></div>" for e, s in m["errores"]) + "</dl></section>")
    p.append('<section id="test"><h2>Test</h2><p class="muted">Elige una respuesta en cada pregunta. Verás la explicación al momento. Con un 80 % o más, el módulo está superado.</p>'
             + render_test(m["num"], cont.TEST) + "</section>")
    p.append('<section id="retos"><h2>Retos</h2><p class="muted">Ejercicios para practicar por tu cuenta. Intenta resolverlos antes de mirar la solución.</p>'
             + render_retos(cont.RETOS) + "</section>")
    p.append(f'<div class="complete-box"><label><input type="checkbox" class="mark-done" data-mod="{m["num"]}"> He completado este módulo</label></div>')
    pn = '<nav class="pager" aria-label="Módulos">'
    pn += (f'<a class="prev" href="{prev_m["num"]}-{prev_m["slug"]}.html"><small>Anterior</small>{fmt(prev_m["titulo"])}</a>' if prev_m else "<span></span>")
    pn += (f'<a class="next" href="{next_m["num"]}-{next_m["slug"]}.html"><small>Siguiente</small>{fmt(next_m["titulo"])}</a>' if next_m else "<span></span>")
    p.append(pn + "</nav>")
    return page(f"{m['num']} · {m['titulo'].replace('`', '')} | Terraform desde cero", "\n".join(p), root, m["num"], m["resumen"], toc=toc)

# ---------------------------------------------------------------- portada


def index_page():
    by = {m["num"]: m for m in MODULOS}
    fases = []
    for titulo, desc, nums in FASES:
        rows = ""
        for n in nums:
            m = by[n]
            rows += (f'<li><a class="mod-row" href="{mod_url(m, "")}" data-mod="{n}"><span class="num">{n}</span>'
                     f'<span><strong>{fmt(m["titulo"])}</strong><span class="desc">{fmt(m["resumen"])}</span></span>'
                     f'<span class="info">{m["nivel"]} · {m["duracion"]}<span class="estado"></span></span></a></li>')
        fases.append(f'<div class="fase"><h3>{titulo}</h3><p class="muted">{desc}</p><ul class="mod-list">{rows}</ul></div>')
    body = f"""
<section class="hero">
  <p class="eyebrow">Curso gratuito · En español · Desde cero</p>
  <h1>Aprende Terraform desde cero</h1>
  <p class="lead">Aprende a crear infraestructura con código, paso a paso. Cada módulo tiene una explicación sencilla, ejemplos que puedes copiar, un test y ejercicios.</p>
  <div class="cta"><a class="btn primary js-continuar" href="modulos/00-introduccion.html">Empezar el curso</a><a class="btn" href="comandos.html">Chuleta de comandos</a></div>
  <ul class="stats">
    <li><strong>16</strong><span>módulos</span></li>
    <li><strong>~35 h</strong><span>de contenido y prácticas</span></li>
    <li><strong>0 €</strong><span>para empezar (módulos 0 a 4 sin nube)</span></li>
  </ul>
</section>

<section id="enfoque">
  <h2>Cómo funciona el curso</h2>
  <div class="grid-2">
    <div class="card"><h3>Para quién</h3><p>Para cualquier persona que empiece de cero. No hace falta saber programar ni haber usado la nube.</p></div>
    <div class="card"><h3>Qué necesitas</h3><p>Un ordenador con Windows, macOS o Linux. A partir del módulo 5, una cuenta de AWS.</p></div>
    <div class="card"><h3>Cómo se aprende</h3><p>Cada módulo tiene: objetivos, lección, práctica guiada, comandos, errores frecuentes, test y retos.</p></div>
    <div class="card"><h3>Sin gastar dinero</h3><p>Empezamos sin nube. Después usamos recursos gratuitos y cada práctica termina con <code>terraform destroy</code>.</p></div>
  </div>
</section>

<section id="temario">
  <h2>Temario</h2>
  {''.join(fases)}
</section>

<section id="antes">
  <h2>Antes de empezar</h2>
  <ul class="check two-col">
    <li>Sé abrir una terminal y moverme entre carpetas (<a href="comandos.html#terminal">repaso aquí</a>).</li>
    <li>Tengo Git instalado y una cuenta de GitHub.</li>
    <li>Tengo un editor de código (recomendado: VS Code).</li>
    <li>Sé que nunca se suben contraseñas ni archivos <code>.tfstate</code> a GitHub.</li>
    <li>A partir del módulo 5: cuenta de AWS con alertas de gasto.</li>
    <li>Reservo 2 a 4 horas por semana.</li>
  </ul>
</section>

<section id="recursos">
  <h2>Material de apoyo</h2>
  <div class="grid-2">
    <a class="card" href="comandos.html"><h3>Chuleta de comandos</h3><p>Terraform, terminal, Git y AWS, con buscador y botón de copiar.</p></a>
    <a class="card" href="glosario.html"><h3>Glosario</h3><p>Todas las palabras del curso explicadas en una línea.</p></a>
    <a class="card" href="{REPO}/tree/main/labs"><h3>Código de las prácticas</h3><p>Cada práctica lista para ejecutar, en la carpeta <code>labs/</code>.</p></a>
  </div>
</section>
"""
    return page("Terraform desde cero · Curso para principiantes", body, "", "inicio",
                "Curso gratuito de Terraform en español para principiantes: lecciones, prácticas, tests y chuleta de comandos.")

# ---------------------------------------------------------------- referencia


def comandos_page():
    secs = ""
    for k, t, d, rows in COMANDOS:
        secs += f'<section id="{k}" class="cmd-section"><h2>{t}</h2><p class="muted">{fmt(d)}</p>{cmd_table(rows)}</section>'
    errs = "".join(f"<tr><td><code>{esc(e)}</code></td><td>{fmt(s)}</td></tr>" for e, s in ERRORES_COMUNES)
    flujo = """$ terraform fmt -recursive
$ terraform validate
$ terraform plan -out=tfplan
$ terraform show tfplan
$ terraform apply tfplan
$ terraform destroy"""
    body = f"""<header class="mod-head"><p class="eyebrow">Referencia</p><h1>Chuleta de comandos</h1>
<p class="lead">Todos los comandos del curso. Usa el buscador o el menú lateral. En la sección de terminal, <code>|</code> separa la versión de Bash de la de PowerShell.</p></header>
<div class="search-box"><label for="buscar" class="sr-only">Buscar comando</label><input id="buscar" type="search" placeholder="Buscar: state, workspace, aws, git..." autocomplete="off"><span id="sin-resultados" hidden>Sin resultados.</span></div>
<section id="flujo-diario" class="cmd-section"><h2>El flujo de cada día</h2><p class="muted">Formatear, validar, planificar, revisar, aplicar y, en las prácticas, destruir.</p>{terminal_output(flujo)}</section>
{secs}
<section id="errores-comunes" class="cmd-section"><h2>Errores comunes</h2><div class="table-wrap"><table><thead><tr><th>Mensaje</th><th>Solución</th></tr></thead><tbody>{errs}</tbody></table></div></section>"""
    toc = [("flujo-diario", "El flujo de cada día", None)] + [(k, t, None) for k, t, _, _ in COMANDOS] + [("errores-comunes", "Errores comunes", None)]
    return page("Chuleta de comandos | Terraform desde cero", body, "", "comandos",
                "Comandos de Terraform, terminal, Git y AWS CLI para el curso.", toc=toc, wide=True)


def glosario_page():
    items = "".join(f'<div><dt>{esc(t)}</dt><dd>{fmt(d)}</dd></div>' for t, d in sorted(GLOSARIO, key=lambda x: x[0].lower()))
    body = f"""<header class="mod-head"><p class="eyebrow">Referencia</p><h1>Glosario</h1><p class="lead">Las palabras del curso, explicadas en una línea.</p></header>
<dl class="glosario">{items}</dl>"""
    return page("Glosario | Terraform desde cero", body, "", "glosario", "Glosario de términos de Terraform.")

# ---------------------------------------------------------------- main


if __name__ == "__main__":
    os.makedirs(f"{OUT}/modulos", exist_ok=True)
    for i, m in enumerate(MODULOS):
        with open(f"{OUT}/modulos/{m['num']}-{m['slug']}.html", "w", encoding="utf-8") as f:
            f.write(modulo_page(i, m))
    for name, fn in [("index.html", index_page), ("comandos.html", comandos_page), ("glosario.html", glosario_page)]:
        with open(f"{OUT}/{name}", "w", encoding="utf-8") as f:
            f.write(fn())
    print("ok", len(MODULOS), "módulos")
