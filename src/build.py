# -*- coding: utf-8 -*-
import html, re, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import importlib
from temario import MODULOS
from extra import COMANDOS, ERRORES_COMUNES, GLOSARIO

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = "https://github.com/lawas-44/terraform-course"

def fmt(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*([A-Za-zÁÉÍÓÚáéíóúñ«][^*<>]*?)\*(?![\w*])", r"<em>\1</em>", s)
    s = s.replace("&lt;kbd&gt;", "<kbd>").replace("&lt;/kbd&gt;", "</kbd>")
    return s

def slug(s):
    import unicodedata
    s = unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")

def esc(s): return html.escape(s, quote=True)

FASES = [
  ("Fase 1 · Fundamentos", "Del cero absoluto a tu primer recurso en la nube.", ["00","01","02","03","04","05"]),
  ("Fase 2 · Construir infraestructura", "Recursos reales, repetición y lógica.", ["06","07","08"]),
  ("Fase 3 · Escalar y mantener", "Estado, entornos, reutilización y código heredado.", ["09","10","11","12"]),
  ("Fase 4 · Nivel profesional", "Calidad, automatización y proyecto final.", ["13","14","15"]),
]

def page(title, body, root, active, desc):
    nav = [("index.html","Inicio","inicio"),("index.html#temario","Temario","temario"),
           ("comandos.html","Comandos","comandos"),("glosario.html","Glosario","glosario")]
    links = "".join(
        f'<a href="{root}{h}"{" aria-current=\"page\"" if k==active else ""}>{t}</a>' for h,t,k in nav)
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
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{root}assets/css/styles.css">
<script>try{{var t=localStorage.getItem('tema');if(t)document.documentElement.dataset.theme=t;}}catch(e){{}}</script>
</head>
<body>
<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="{root}index.html"><span class="logo" aria-hidden="true">tf</span> Terraform desde cero</a>
    <nav class="main-nav" aria-label="Principal">{links}<a href="{REPO}" rel="noopener">GitHub</a></nav>
    <button class="theme-toggle" type="button" aria-label="Cambiar tema claro/oscuro" title="Cambiar tema"><svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="2"/><path d="M12 3a9 9 0 0 1 0 18z" fill="currentColor"/></svg></button>
  </div>
</header>
<main id="contenido">
{body}
</main>
<footer class="site-footer">
  <div class="wrap">
    <p>Curso abierto de Terraform para principiantes · Código en <a href="{REPO}">GitHub</a>. Terraform es una marca de HashiCorp; este curso no está afiliado.</p>
  </div>
</footer>
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

LANGS = {"hcl":"language-hcl","yaml":"language-yaml","text":"language-none","bash":"language-bash","json":"language-json"}

def code_block(lang, name, code, term=False):
    cls = LANGS.get(lang, "language-none")
    extra = " term" if term else ""
    return (f'<figure class="code{extra}"><figcaption><span>{esc(name)}</span>'
            f'<button class="copy" type="button" aria-label="Copiar código">Copiar</button></figcaption>'
            f'<pre><code class="{cls}">{html.escape(code, quote=False)}</code></pre></figure>')

def render_blocks(blocks):
    out, toc = [], []
    for b in blocks:
        k = b[0]
        if k == "h":
            sid = slug(b[1]); toc.append((sid, b[1]))
            out.append(f'<h3 id="{sid}">{fmt(b[1])}</h3>')
        elif k == "p": out.append(f"<p>{fmt(b[1])}</p>")
        elif k == "ul": out.append("<ul>" + "".join(f"<li>{fmt(x)}</li>" for x in b[1]) + "</ul>")
        elif k == "ol": out.append("<ol>" + "".join(f"<li>{fmt(x)}</li>" for x in b[1]) + "</ol>")
        elif k == "code": out.append(code_block(b[1], b[2], b[3]))
        elif k == "term": out.append(code_block("text", "terminal", b[1], term=True))
        elif k in ("tip", "warn", "info"):
            icon = {"tip": "💡 Consejo", "warn": "⚠️ Cuidado", "info": "ℹ️ Nota"}[k]
            cls = {"tip": "tip", "warn": "aviso", "info": ""}[k]
            out.append(f'<div class="callout {cls}"><strong>{icon}.</strong> {fmt(b[1])}</div>')
        elif k == "table":
            head = "".join(f"<th>{fmt(h)}</th>" for h in b[1])
            rows = "".join("<tr>" + "".join(f"<td>{fmt(c)}</td>" for c in r) + "</tr>" for r in b[2])
            out.append(f'<div class="table-wrap"><table class="data"><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>')
        elif k == "html": out.append(b[1])
        else: raise ValueError(k)
    return "\n".join(out), toc

def render_test(num, test):
    import random
    letras = "ABCD"
    qs = []
    for n, (q, opts, ok, exp) in enumerate(test, 1):
        # Barajado determinista: la respuesta correcta no cae siempre en la misma letra
        orden = list(range(len(opts)))
        random.Random(f"{num}-{n}").shuffle(orden)
        opts = [opts[j] for j in orden]
        ok = orden.index(ok)
        bts = "".join(f'<button type="button" class="opt" data-i="{i}"><span class="letra">{letras[i]}</span><span class="txt">{fmt(o)}</span></button>' for i, o in enumerate(opts))
        qs.append(f'<fieldset class="q" data-ok="{ok}"><legend><span class="qn">{n}</span><span class="txt">{fmt(q)}</span></legend>'
                  f'<div class="opts">{bts}</div><p class="exp" hidden><strong class="verdict"></strong> {fmt(exp)}</p></fieldset>')
    return (f'<div class="quiz" data-mod="{num}" data-total="{len(test)}">' + "".join(qs) +
            '<div class="quiz-foot"><p class="quiz-result" aria-live="polite">Responde todas las preguntas para ver tu nota.</p>'
            '<button type="button" class="btn small quiz-reset">Reintentar</button></div></div>')

def render_retos(retos):
    out = []
    for n, r in enumerate(retos, 1):
        h = f'<article class="reto"><h3>Reto {n}: {fmt(r["titulo"])}</h3><p>{fmt(r["enunciado"])}</p>'
        if r.get("codigo"):
            h += code_block(r["codigo"][0], "código del reto", r["codigo"][1])
        if r.get("pista"):
            h += f'<details><summary>💡 Ver pista</summary><p>{fmt(r["pista"])}</p></details>'
        lang, code = r["solucion"]
        h += f'<details><summary>✅ Ver solución</summary>{code_block(lang, "solución", code)}</details></article>'
        out.append(h)
    return "\n".join(out)

def modulo_page(i, m):
    root = "../"
    prev_m = MODULOS[i-1] if i > 0 else None
    next_m = MODULOS[i+1] if i < len(MODULOS)-1 else None
    cont = importlib.import_module(f"contenido.m{m['num']}")
    leccion_html, toc = render_blocks(cont.LECCION)
    parts = []
    nav = [("objetivos", "Objetivos"), ("leccion", "Lección"), ("practica", "Práctica")]
    if m["comandos"]: nav.append(("comandos", "Comandos"))
    nav += [("errores", "Errores frecuentes"), ("test", "Test"), ("retos", "Retos")]
    parts.append(f"""<div class="wrap narrow">
<nav class="breadcrumb" aria-label="Ruta"><a href="../index.html#temario">Temario</a> / Módulo {m['num']}</nav>
<header class="mod-head">
  <p class="eyebrow">Módulo {m['num']}</p>
  <h1>{fmt(m['titulo'])}</h1>
  <p class="lead">{fmt(m['resumen'])}</p>
  <div class="chips"><span class="chip nivel-{m['nivel'].lower()}">{m['nivel']}</span><span class="chip">⏱ {m['duracion']}</span><span class="chip">📝 {len(cont.TEST)} preguntas</span><span class="chip">🏋️ {len(cont.RETOS)} retos</span></div>
</header>
<nav class="toc" aria-label="En esta página"><strong>En esta página</strong>{''.join(f'<a href="#{a}">{t}</a>' for a, t in nav)}</nav>
""")
    parts.append('<section id="objetivos"><h2>🎯 Objetivos de aprendizaje</h2><p>Al terminar este módulo serás capaz de:</p><ul class="check">'
                 + "".join(f"<li>{fmt(o)}</li>" for o in m["objetivos"]) + "</ul></section>")
    indice = '<nav class="indice" aria-label="Índice de la lección"><strong>Índice de la lección</strong><ol>' + "".join(f'<li><a href="#{a}">{fmt(t)}</a></li>' for a, t in toc) + "</ol></nav>"
    parts.append(f'<section id="leccion" class="leccion"><h2>📚 Lección</h2>{indice}{leccion_html}</section>')
    lab = m["lab"]
    parts.append(f'<section id="practica"><h2>🛠 Práctica guiada: {fmt(lab["titulo"])}</h2><ol class="pasos">'
                 + "".join(f"<li>{fmt(p)}</li>" for p in lab["pasos"]) + "</ol>"
                 + ('<div class="callout aviso"><strong>💸 Recuerda:</strong> si has creado recursos en la nube, ejecuta <code>terraform destroy</code> al terminar.</div>' if int(m["num"]) >= 5 else "")
                 + "</section>")
    if m["comandos"]:
        parts.append('<section id="comandos"><h2>⌨️ Comandos clave</h2><div class="table-wrap"><table class="cmds"><thead><tr><th>Comando</th><th>Qué hace</th><th><span class="sr-only">Copiar</span></th></tr></thead><tbody>'
                     + "".join(cmd_row(c,d) for c,d in m["comandos"]) + "</tbody></table></div></section>")
    parts.append('<section id="errores"><h2>⚠️ Errores frecuentes</h2><dl class="errores">'
                 + "".join(f"<div><dt>{fmt(e)}</dt><dd>{fmt(s)}</dd></div>" for e,s in m["errores"]) + "</dl></section>")
    parts.append('<section id="test"><h2>✅ Test de autoevaluación</h2><p class="muted">Elige una respuesta en cada pregunta. Verás la explicación al momento. Con un 80 % o más, el módulo está superado.</p>'
                 + render_test(m["num"], cont.TEST) + "</section>")
    parts.append('<section id="retos"><h2>🏋️ Retos</h2><p class="muted">Ejercicios para practicar por tu cuenta. Intenta resolverlos antes de mirar la solución.</p>'
                 + render_retos(cont.RETOS) + "</section>")
    parts.append(f'<div class="complete-box"><label><input type="checkbox" class="mark-done" data-mod="{m["num"]}"> He completado este módulo</label></div>')
    pn = '<nav class="pager" aria-label="Módulos">'
    pn += (f'<a class="prev" href="{prev_m["num"]}-{prev_m["slug"]}.html"><small>← Anterior</small>{fmt(prev_m["titulo"])}</a>' if prev_m else "<span></span>")
    pn += (f'<a class="next" href="{next_m["num"]}-{next_m["slug"]}.html"><small>Siguiente →</small>{fmt(next_m["titulo"])}</a>' if next_m else "<span></span>")
    pn += "</nav></div>"
    parts.append(pn)
    return page(f"{m['num']} · {re.sub('`','',m['titulo'])} | Terraform desde cero", "\n".join(parts), root, "temario", m["resumen"])

def index_page():
    by = {m["num"]: m for m in MODULOS}
    fases = []
    for t, d, nums in FASES:
        cards = ""
        for n in nums:
            m = by[n]
            cards += (f'<a class="mod-card" href="modulos/{n}-{m["slug"]}.html" data-mod="{n}">'
                      f'<span class="mod-num">{n}</span><span class="mod-body"><strong>{fmt(m["titulo"])}</strong>'
                      f'<span>{fmt(m["resumen"])}</span><span class="meta">{m["nivel"]} · {m["duracion"]}<span class="done-badge">✓ Completado</span><span class="score-badge"></span></span></span></a>')
        fases.append(f'<div class="fase"><h3>{t}</h3><p class="muted">{d}</p><div class="mod-grid">{cards}</div></div>')
    body = f"""
<section class="hero">
  <div class="wrap">
    <p class="eyebrow">Curso gratuito · En español · Desde cero</p>
    <h1>Aprende Terraform<br>sin dar nada por sabido</h1>
    <p class="lead">Infraestructura como Código paso a paso: de tu primer <code>terraform init</code> a un pipeline de CI/CD desplegando en AWS. Teoría corta, mucha práctica y comandos listos para copiar.</p>
    <div class="cta"><a class="btn primary" href="modulos/00-introduccion.html">Empezar el curso</a><a class="btn" href="comandos.html">Ver chuleta de comandos</a></div>
    <ul class="stats">
      <li><strong>16</strong><span>módulos</span></li>
      <li><strong>~35 h</strong><span>de contenido y prácticas</span></li>
      <li><strong>0 €</strong><span>para empezar (módulos 0–4 sin nube)</span></li>
    </ul>
  </div>
</section>

<section class="wrap" id="enfoque">
  <h2>Cómo está pensado el curso</h2>
  <div class="grid-3">
    <article class="card"><h3>👤 Para quién</h3><p>Personas sin experiencia en Terraform ni en la nube: estudiantes, desarrolladores, sysadmins o perfiles de soporte que quieren dar el salto a DevOps/Cloud.</p></article>
    <article class="card"><h3>🧰 Qué necesitas</h3><p>Un ordenador (Windows, macOS o Linux), ganas de usar la terminal y, a partir del módulo 5, una cuenta de AWS con alertas de presupuesto. No hace falta saber programar.</p></article>
    <article class="card"><h3>🔁 Cómo se aprende</h3><p>Cada módulo sigue el mismo patrón: <em>objetivos → teoría breve → ejemplo → práctica guiada → comandos → errores frecuentes → autoevaluación</em>.</p></article>
    <article class="card"><h3>💸 Sin sustos en la factura</h3><p>Empezamos con providers locales (<code>local</code>, <code>random</code>), luego usamos recursos de la capa gratuita y cada práctica termina con <code>terraform destroy</code>.</p></article>
    <article class="card"><h3>🔀 Terraform u OpenTofu</h3><p>Usamos Terraform (1.10 o superior). Casi todo lo aprendido funciona igual en OpenTofu cambiando <code>terraform</code> por <code>tofu</code>.</p></article>
    <article class="card"><h3>🎓 Hacia la certificación</h3><p>El temario cubre los dominios del examen <em>HashiCorp Certified: Terraform Associate</em> y termina con un proyecto para tu portfolio.</p></article>
  </div>
</section>

<section class="wrap" id="temario">
  <div class="temario-head">
    <h2>Temario</h2>
    <div class="progress" aria-live="polite"><div class="bar"><span id="progress-fill"></span></div><span id="progress-text">0 de {len(MODULOS)} módulos completados</span></div>
  </div>
  {''.join(fases)}
</section>

<section class="wrap" id="antes">
  <h2>Checklist antes de empezar</h2>
  <ul class="check two-col">
    <li>Sé abrir una terminal y moverme entre carpetas (<a href="comandos.html#terminal">repaso aquí</a>).</li>
    <li>Tengo Git instalado y una cuenta de GitHub.</li>
    <li>Tengo un editor (recomendado: VS Code + extensión HashiCorp Terraform).</li>
    <li>Sé que <strong>nunca</strong> se suben claves ni archivos <code>.tfstate</code> a GitHub.</li>
    <li>(Módulo 5+) Cuenta de AWS con MFA, usuario no-root y presupuesto con alertas.</li>
    <li>Reservo 2–4 horas por semana: el curso completo cabe en 2–3 meses.</li>
  </ul>
</section>

<section class="wrap" id="recursos">
  <h2>Recursos complementarios</h2>
  <div class="grid-3">
    <a class="card link" href="comandos.html"><h3>⌨️ Chuleta de comandos</h3><p>Terraform, terminal, Git, AWS CLI y herramientas, con buscador y botón de copiar.</p></a>
    <a class="card link" href="glosario.html"><h3>📖 Glosario</h3><p>Todos los términos del curso explicados en una línea.</p></a>
    <a class="card link" href="{REPO}/tree/main/labs"><h3>🧪 Laboratorios</h3><p>El código de cada práctica en la carpeta <code>labs/</code> del repositorio.</p></a>
  </div>
</section>
"""
    return page("Terraform desde cero · Curso para principiantes", body, "", "inicio",
                "Curso gratuito de Terraform en español para principiantes: temario completo, prácticas y chuleta de comandos.")

def comandos_page():
    toc = "".join(f'<a href="#{k}">{t}</a>' for k,t,_,_ in COMANDOS)
    secs = ""
    for k, t, d, rows in COMANDOS:
        secs += (f'<section id="{k}" class="cmd-section"><h2>{t}</h2><p class="muted">{fmt(d)}</p><div class="table-wrap"><table class="cmds"><thead><tr><th>Comando</th><th>Qué hace</th><th><span class="sr-only">Copiar</span></th></tr></thead><tbody>'
                 + "".join(cmd_row(c,dd) for c,dd in rows) + "</tbody></table></div></section>")
    errs = "".join(f"<tr><td><code>{esc(e)}</code></td><td>{fmt(s)}</td></tr>" for e,s in ERRORES_COMUNES)
    body = f"""<div class="wrap">
<header class="mod-head"><p class="eyebrow">Referencia</p><h1>Chuleta de comandos</h1>
<p class="lead">Todo lo que vas a teclear durante el curso. Usa el buscador o salta a una sección. En la sección de terminal, <code>|</code> separa la versión Bash/Zsh de la de PowerShell.</p></header>
<div class="search-box"><label for="buscar" class="sr-only">Buscar comando</label><input id="buscar" type="search" placeholder="Buscar: state, workspace, aws, git…" autocomplete="off"><span id="sin-resultados" hidden>Sin resultados.</span></div>
<nav class="toc pills" aria-label="Secciones">{toc}<a href="#errores-comunes">Errores comunes</a></nav>
{secs}
<section id="errores-comunes" class="cmd-section"><h2>Errores comunes y cómo salir de ellos</h2><div class="table-wrap"><table class="cmds"><thead><tr><th>Mensaje</th><th>Solución</th></tr></thead><tbody>{errs}</tbody></table></div></section>
<section class="cmd-section"><h2>Ciclo de vida recomendado</h2>
{code_block("bash", "flujo diario", '''terraform fmt -recursive      # 1. formatear
terraform validate            # 2. validar
terraform plan -out=tfplan    # 3. planificar y guardar
terraform show tfplan         # 4. revisar con calma
terraform apply tfplan        # 5. aplicar exactamente ese plan
terraform destroy             # 6. (prácticas) limpiar al terminar''')}
</section>
</div>"""
    return page("Chuleta de comandos | Terraform desde cero", body, "", "comandos",
                "Comandos de Terraform, terminal, Git y AWS CLI para el curso.")

def glosario_page():
    items = "".join(f'<div><dt>{esc(t)}</dt><dd>{fmt(d)}</dd></div>' for t,d in sorted(GLOSARIO, key=lambda x: x[0].lower()))
    body = f"""<div class="wrap narrow">
<header class="mod-head"><p class="eyebrow">Referencia</p><h1>Glosario</h1><p class="lead">Los términos que aparecen en el curso, explicados en una línea.</p></header>
<dl class="glosario">{items}</dl></div>"""
    return page("Glosario | Terraform desde cero", body, "", "glosario", "Glosario de términos de Terraform.")

os.makedirs(f"{OUT}/modulos", exist_ok=True)
for i, m in enumerate(MODULOS):
    with open(f"{OUT}/modulos/{m['num']}-{m['slug']}.html", "w", encoding="utf-8") as f:
        f.write(modulo_page(i, m))
for name, fn in [("index.html", index_page), ("comandos.html", comandos_page), ("glosario.html", glosario_page)]:
    with open(f"{OUT}/{name}", "w", encoding="utf-8") as f:
        f.write(fn())
print("ok", len(MODULOS), "módulos")
