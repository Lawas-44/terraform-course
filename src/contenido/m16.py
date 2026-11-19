# -*- coding: utf-8 -*-
# Módulo 16 · Handlers, condiciones y bucles

LECCION = [
 ("h", "Handlers: reiniciar solo cuando hace falta"),
 ("p", "Cuando cambias el archivo de configuración de un programa (por ejemplo, nginx), hay que recargarlo para que lea los cambios. Pero si la configuración no ha cambiado, recargarlo es innecesario."),
 ("p", "Para eso están los **handlers**: tareas especiales que solo se ejecutan si otra tarea **les avisa** con `notify` y además esa tarea **ha cambiado algo**."),
 ("code", "yaml", "site.yml", """---
- name: Configurar nginx
  hosts: web
  become: true

  tasks:
    - name: Configurar el sitio
      ansible.builtin.template:
        src: templates/sitio.conf.j2
        dest: /etc/nginx/sites-available/miweb
        mode: "0644"
      notify: Recargar nginx

  handlers:
    - name: Recargar nginx
      ansible.builtin.service:
        name: nginx
        state: reloaded"""),
 ("ul", [
  "Si la plantilla cambia el archivo, la tarea sale `changed` y avisa al handler.",
  "Si el archivo ya estaba igual, la tarea sale `ok` y el handler **no** se ejecuta.",
  "Los handlers se ejecutan al **final** del playbook, y una sola vez aunque varias tareas les avisen.",
 ]),
 ("term", """$ ansible-playbook site.yml
TASK [Configurar el sitio] ****************************************
changed: [web1]

RUNNING HANDLER [Recargar nginx] **********************************
changed: [web1]"""),
 ("warn", "El texto de `notify` debe ser **exactamente igual** al `name` del handler, incluidas mayúsculas."),

 ("h", "Bucles: repetir una tarea"),
 ("p", "Con `loop` una tarea se repite para cada elemento de una lista. El elemento actual se llama `item`:"),
 ("code", "yaml", "loop", """    - name: Crear carpetas
      ansible.builtin.file:
        path: "/var/www/miweb/{{ item }}"
        state: directory
        mode: "0755"
      loop:
        - imagenes
        - css
        - privado"""),
 ("tip", "Algunos módulos aceptan una lista directamente y son más rápidos así. Por ejemplo, `apt` puede instalar varios paquetes de una vez: `name: [curl, htop, unzip]`."),
 ("p", "Con una lista de objetos, se accede a cada campo con un punto:"),
 ("code", "yaml", "loop con objetos", """    - name: Crear usuarios
      ansible.builtin.user:
        name: "{{ item.nombre }}"
        shell: "{{ item.shell }}"
      loop:
        - { nombre: ana, shell: /bin/bash }
        - { nombre: luis, shell: /bin/sh }"""),

 ("h", "Condiciones: when"),
 ("p", "`when` hace que una tarea solo se ejecute si se cumple una condición. No se ponen las llaves `{{ }}`:"),
 ("code", "yaml", "when", """    - name: Instalar nginx en Ubuntu
      ansible.builtin.apt:
        name: nginx
        state: present
      when: ansible_facts['distribution'] == "Ubuntu"

    - name: Activar la zona privada
      ansible.builtin.template:
        src: templates/privado.html.j2
        dest: /var/www/miweb/privado/index.html
        mode: "0644"
      when: web_privado_activo | default(false)"""),
 ("p", "Si la condición no se cumple, la tarea aparece como `skipping` en la salida."),

 ("h", "Guardar resultados: register"),
 ("p", "`register` guarda el resultado de una tarea en una variable para usarlo después:"),
 ("code", "yaml", "register", """    - name: Ver la versión de nginx
      ansible.builtin.command: nginx -v
      register: version_nginx
      changed_when: false

    - name: Mostrar la versión
      ansible.builtin.debug:
        msg: "{{ version_nginx.stderr }}\""""),
 ("ul", [
  "`changed_when: false` le dice a Ansible que esa tarea nunca cambia nada (solo consulta). Así no aparece como `changed`.",
  "El módulo `debug` muestra un mensaje en pantalla. Muy útil para aprender y para buscar errores.",
 ]),
 ("term", """TASK [Mostrar la versión] *****************************************
ok: [web1] => {
    "msg": "nginx version: nginx/1.24.0 (Ubuntu)"
}"""),
]

TEST = [
 ("¿Cuándo se ejecuta un handler?",
  ["Siempre al final", "Solo si una tarea le avisa con notify y esa tarea ha cambiado algo", "Al principio del playbook", "Cada vez que hay un error"], 1,
  "Si la tarea sale ok (sin cambios), el handler no se ejecuta."),
 ("Tres tareas avisan al mismo handler y las tres cambian algo. ¿Cuántas veces se ejecuta?",
  ["Tres", "Una, al final", "Ninguna", "Dos"], 1, "Los handlers se ejecutan una sola vez, al final."),
 ("¿Cómo se llama el elemento actual dentro de un `loop`?",
  ["element", "item", "each.value", "i"], 1, "Ansible usa `item`."),
 ("¿Qué hace `when: ansible_facts['distribution'] == \"Ubuntu\"`?",
  ["Instala Ubuntu", "Ejecuta la tarea solo en servidores Ubuntu", "Falla si no es Ubuntu", "Muestra el sistema"], 1,
  "En los demás servidores la tarea aparece como skipping."),
 ("¿Para qué sirve `register`?",
  ["Para registrar un servidor", "Para guardar el resultado de una tarea en una variable", "Para crear un usuario", "Para cifrar"], 1,
  "Después puedes usar esa variable en otras tareas."),
 ("¿Qué consigue `changed_when: false` en una tarea que solo consulta algo?",
  ["Que no se ejecute", "Que nunca aparezca como changed", "Que falle", "Que se repita"], 1,
  "Así el resultado del playbook refleja solo los cambios reales."),
]

RETOS = [
 {"titulo": "Paquetes y carpetas",
  "enunciado": "Escribe un playbook para el grupo `local` que cree en `/tmp/miweb` las carpetas `css`, `js` e `img` con un `loop`, y muestre con `debug` cuántas carpetas ha creado.",
  "pista": "Usa `register` en la tarea con loop: el resultado tiene una lista `results`.",
  "solucion": ("yaml", """---
- name: Carpetas
  hosts: local
  tasks:
    - name: Crear carpetas
      ansible.builtin.file:
        path: "/tmp/miweb/{{ item }}"
        state: directory
        mode: "0755"
      loop: [css, js, img]
      register: carpetas

    - name: Resumen
      ansible.builtin.debug:
        msg: "Carpetas procesadas: {{ carpetas.results | length }}\"""")},
 {"titulo": "Handler que no se dispara",
  "enunciado": "¿Por qué este handler no se ejecuta nunca? Corrígelo.",
  "codigo": ("yaml", """  tasks:
    - name: Configurar nginx
      ansible.builtin.template:
        src: nginx.conf.j2
        dest: /etc/nginx/nginx.conf
        mode: "0644"
      notify: recargar nginx

  handlers:
    - name: Recargar nginx
      ansible.builtin.service:
        name: nginx
        state: reloaded"""),
  "pista": "Compara letra por letra el notify y el nombre del handler.",
  "solucion": ("yaml", """      notify: Recargar nginx   # debe coincidir exactamente, con la R mayúscula""")},
]

PROYECTO = {
 "titulo": "Configura nginx a tu medida",
 "bloques": [
  ("p", "Hasta ahora usabas la configuración por defecto de nginx. Vas a poner la tuya: tu web en su propia carpeta (`/var/www/miweb`), con un handler que recarga nginx solo si cambia la configuración."),
  ("p", "1. Crea la plantilla de configuración de nginx:"),
  ("code", "text", "ansible/templates/sitio.conf.j2", """# Archivo gestionado por Ansible
server {
    listen 80 default_server;
    server_name _;

    root {{ web_raiz }};
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }
}"""),
  ("p", "2. Actualiza `site.yml` completo. Fíjate en el `loop`, los `notify` y el handler:"),
  ("code", "yaml", "ansible/site.yml", """---
- name: Configurar los servidores web
  hosts: web
  become: true
  vars:
    web_raiz: /var/www/miweb

  tasks:
    - name: Actualizar la lista de paquetes
      ansible.builtin.apt:
        update_cache: true
        cache_valid_time: 3600

    - name: Instalar paquetes
      ansible.builtin.apt:
        name: "{{ item }}"
        state: present
      loop:
        - nginx
        - curl
        - htop

    - name: Crear la carpeta de la web
      ansible.builtin.file:
        path: "{{ web_raiz }}"
        state: directory
        mode: "0755"

    - name: Configurar el sitio
      ansible.builtin.template:
        src: templates/sitio.conf.j2
        dest: /etc/nginx/sites-available/miweb
        mode: "0644"
      notify: Recargar nginx

    - name: Activar el sitio
      ansible.builtin.file:
        src: /etc/nginx/sites-available/miweb
        dest: /etc/nginx/sites-enabled/miweb
        state: link
      notify: Recargar nginx

    - name: Desactivar el sitio por defecto
      ansible.builtin.file:
        path: /etc/nginx/sites-enabled/default
        state: absent
      notify: Recargar nginx

    - name: Generar las páginas
      ansible.builtin.template:
        src: "templates/{{ item }}.j2"
        dest: "{{ web_raiz }}/{{ item }}"
        mode: "0644"
      loop:
        - index.html
        - estado.html

    - name: Arrancar nginx
      ansible.builtin.service:
        name: nginx
        state: started
        enabled: true

  handlers:
    - name: Recargar nginx
      ansible.builtin.service:
        name: nginx
        state: reloaded"""),
  ("term", """$ ansible-playbook site.yml
...
RUNNING HANDLER [Recargar nginx] **********************************
changed: [web1]
changed: [web2]
$ ansible-playbook site.yml
...
web1 : ok=10  changed=0  unreachable=0  failed=0"""),
  ("p", "La segunda vez no hay cambios y el handler no se ejecuta: nginx no se recarga sin motivo."),
  ("p", "Resultado de este paso: nginx usa tu configuración y tu web vive en `/var/www/miweb`. El playbook ya es largo; en el próximo módulo lo ordenarás en roles."),
 ],
}
