# -*- coding: utf-8 -*-
# Módulo 14 · Playbooks

LECCION = [
 ("h", "YAML en cinco minutos"),
 ("p", "Los playbooks se escriben en **YAML**, un formato de texto muy sencillo. Solo hay tres reglas importantes:"),
 ("ol", [
  "La **sangría** (los espacios al principio) indica qué va dentro de qué. Usa siempre espacios, nunca tabuladores.",
  "`clave: valor` define un dato.",
  "Un guion `- ` al principio indica un elemento de una lista.",
 ]),
 ("code", "yaml", "ejemplo.yml", """---
nombre: Ana            # texto
edad: 30               # número
activo: true           # verdadero o falso
lenguajes:             # lista
  - terraform
  - ansible
direccion:             # datos dentro de otro dato
  ciudad: Madrid
  cp: "28001\""""),
 ("tip", "Los archivos YAML suelen empezar con `---`. No es obligatorio, pero es la costumbre."),

 ("h", "Qué es un playbook"),
 ("p", "Un **playbook** es un archivo con una lista de **tareas** que Ansible ejecuta en orden en un grupo de servidores. Es como una receta: primero esto, luego esto otro."),
 ("code", "yaml", "site.yml", """---
- name: Configurar los servidores web
  hosts: web
  become: true

  tasks:
    - name: Instalar nginx
      ansible.builtin.apt:
        name: nginx
        state: present
        update_cache: true

    - name: Arrancar nginx
      ansible.builtin.service:
        name: nginx
        state: started
        enabled: true"""),
 ("ul", [
  "`name`: una descripción. Es lo que verás en pantalla.",
  "`hosts`: en qué grupo del inventario se ejecuta.",
  "`become: true`: ejecutar como administrador.",
  "`tasks`: la lista de tareas. Cada tarea usa un **módulo** (`apt`, `service`...) con sus opciones.",
 ]),
 ("info", "`ansible.builtin.apt` es el nombre completo del módulo `apt`. Se recomienda escribir el nombre completo para evitar confusiones."),

 ("h", "Ejecutar un playbook"),
 ("term", """$ ansible-playbook site.yml

PLAY [Configurar los servidores web] ******************************

TASK [Gathering Facts] ********************************************
ok: [web1]
ok: [web2]

TASK [Instalar nginx] *********************************************
changed: [web1]
changed: [web2]

TASK [Arrancar nginx] *********************************************
ok: [web1]
ok: [web2]

PLAY RECAP ********************************************************
web1 : ok=3  changed=1  unreachable=0  failed=0
web2 : ok=3  changed=1  unreachable=0  failed=0"""),
 ("table", ["Resultado", "Significado"], [
  ["`ok`", "Ya estaba bien; no ha hecho falta cambiar nada"],
  ["`changed`", "Ha hecho un cambio"],
  ["`failed`", "Ha fallado"],
  ["`unreachable`", "No ha podido conectarse al servidor"],
 ]),

 ("h", "Idempotencia: ejecutarlo varias veces"),
 ("p", "Ejecuta el mismo playbook otra vez:"),
 ("term", """$ ansible-playbook site.yml
...
PLAY RECAP ********************************************************
web1 : ok=3  changed=0  unreachable=0  failed=0
web2 : ok=3  changed=0  unreachable=0  failed=0"""),
 ("p", "`changed=0`: nginx ya estaba instalado y arrancado, así que no ha hecho nada. Como Terraform, Ansible describe **cómo debe quedar** el servidor y solo cambia lo necesario. Por eso puedes ejecutar un playbook tantas veces como quieras sin miedo."),

 ("h", "Probar antes de cambiar"),
 ("p", "Igual que `terraform plan`, Ansible puede enseñarte lo que haría sin cambiar nada:"),
 ("term", """$ ansible-playbook site.yml --check --diff"""),
 ("ul", [
  "`--check`: simula; no cambia nada.",
  "`--diff`: muestra las líneas que cambiarían en los archivos.",
 ]),
 ("p", "Y para comprobar que el YAML está bien escrito:"),
 ("term", """$ ansible-playbook site.yml --syntax-check
playbook: site.yml"""),

 ("h", "Los módulos más usados"),
 ("table", ["Módulo", "Para qué sirve", "Ejemplo"], [
  ["`apt`", "Instalar o quitar paquetes (Ubuntu/Debian)", "`name: nginx`, `state: present`"],
  ["`service`", "Arrancar, parar o reiniciar servicios", "`name: nginx`, `state: started`"],
  ["`copy`", "Copiar un archivo o escribir un texto", "`src: web.css`, `dest: /var/www/web.css`"],
  ["`file`", "Crear carpetas, enlaces o borrar archivos", "`path: /var/www`, `state: directory`"],
  ["`template`", "Copiar un archivo rellenando variables (módulo 15)", "`src: index.html.j2`"],
  ["`user`", "Crear usuarios", "`name: deploy`"],
  ["`command`", "Ejecutar un comando (último recurso)", "`cmd: uptime`"],
 ]),
 ("code", "yaml", "más tareas", """    - name: Crear la carpeta de la web
      ansible.builtin.file:
        path: /var/www/miweb
        state: directory
        mode: "0755"

    - name: Crear una página sencilla
      ansible.builtin.copy:
        content: "<h1>Hola desde Ansible</h1>"
        dest: /var/www/miweb/index.html
        mode: "0644"

    - name: Crear el usuario deploy
      ansible.builtin.user:
        name: deploy
        shell: /bin/bash"""),
 ("warn", "Evita `command` y `shell` siempre que exista un módulo para lo que quieres hacer. Los módulos saben si algo ya está hecho; un comando suelto se ejecuta siempre."),
]

TEST = [
 ("En YAML, ¿qué indica la sangría?",
  ["Nada, es decorativa", "Qué datos van dentro de otros", "Los comentarios", "El orden de ejecución"], 1,
  "Por eso hay que ser cuidadoso con los espacios."),
 ("¿Qué indica `hosts: web` en un playbook?",
  ["El nombre del playbook", "El grupo del inventario donde se ejecuta", "El usuario SSH", "El puerto"], 1,
  "Las tareas se ejecutarán en todos los servidores del grupo web."),
 ("Ejecutas un playbook dos veces seguidas sin cambiar nada. ¿Qué esperas ver la segunda vez?",
  ["changed en todas las tareas", "changed=0", "failed", "unreachable"], 1,
  "Ansible es idempotente: si todo está ya bien, no cambia nada."),
 ("¿Qué hace `--check`?",
  ["Comprueba la sintaxis", "Simula la ejecución sin cambiar nada", "Revisa la seguridad", "Comprueba la conexión"], 1,
  "Es el equivalente a terraform plan."),
 ("¿Qué módulo usarías para crear una carpeta?",
  ["copy", "file", "apt", "service"], 1, "`file` con `state: directory`."),
 ("¿Por qué evitar `command` cuando hay un módulo específico?",
  ["Porque es más lento", "Porque los módulos saben si algo ya está hecho y command se ejecuta siempre", "Porque command no existe", "Porque necesita internet"], 1,
  "Los módulos son idempotentes; un comando suelto no."),
]

RETOS = [
 {"titulo": "Arregla el YAML",
  "enunciado": "Este playbook tiene tres errores de YAML o de Ansible. Encuéntralos y compruébalo con `--syntax-check`.",
  "codigo": ("yaml", """- name: Mi playbook
  hosts: local
  tasks:
  - name: Crear carpeta
      ansible.builtin.file:
        path: /tmp/prueba
        state: directory
    - name Crear archivo
      ansible.builtin.copy:
        content: "hola"
        dest: /tmp/prueba/hola.txt"""),
  "pista": "Mira la sangría de las tareas y los dos puntos.",
  "solucion": ("yaml", """- name: Mi playbook
  hosts: local
  tasks:
    - name: Crear carpeta            # 1. todas las tareas al mismo nivel
      ansible.builtin.file:          # 2. el módulo, alineado con name
        path: /tmp/prueba
        state: directory
    - name: Crear archivo            # 3. faltaban los dos puntos
      ansible.builtin.copy:
        content: "hola"
        dest: /tmp/prueba/hola.txt""")},
 {"titulo": "Un playbook completo",
  "enunciado": "Escribe un playbook para el grupo `local` que cree la carpeta `/tmp/miweb`, escriba dentro un `index.html` con tu nombre y cree el archivo `/tmp/miweb/LEEME.txt`. Ejecútalo dos veces.",
  "pista": "Usa `file` y `copy` con `content`. No hace falta `become` porque es `/tmp`.",
  "solucion": ("yaml", """---
- name: Mi web local
  hosts: local
  tasks:
    - name: Crear la carpeta
      ansible.builtin.file:
        path: /tmp/miweb
        state: directory
        mode: "0755"

    - name: Crear la página
      ansible.builtin.copy:
        content: "<h1>Ana</h1>"
        dest: /tmp/miweb/index.html
        mode: "0644"

    - name: Crear el LEEME
      ansible.builtin.copy:
        content: "Creado con Ansible"
        dest: /tmp/miweb/LEEME.txt
        mode: "0644"
# Segunda ejecución: changed=0""")},
]

PROYECTO = {
 "titulo": "Instala nginx: tu primera web visible",
 "bloques": [
  ("p", "Vas a escribir el primer playbook del proyecto. Instalará el servidor web nginx en los dos servidores y publicará una página sencilla. Al terminar podrás abrir la web en el navegador."),
  ("code", "yaml", "ansible/site.yml", """---
- name: Configurar los servidores web
  hosts: web
  become: true

  tasks:
    - name: Actualizar la lista de paquetes
      ansible.builtin.apt:
        update_cache: true
        cache_valid_time: 3600

    - name: Instalar nginx
      ansible.builtin.apt:
        name: nginx
        state: present

    - name: Crear la carpeta de la web
      ansible.builtin.file:
        path: /var/www/html
        state: directory
        mode: "0755"

    - name: Publicar una página de prueba
      ansible.builtin.copy:
        content: "<h1>Mi web en la nube</h1><p>Servidor {{ inventory_hostname }}</p>"
        dest: /var/www/html/index.html
        mode: "0644"

    - name: Arrancar nginx
      ansible.builtin.service:
        name: nginx
        state: started
        enabled: true"""),
  ("p", "`{{ inventory_hostname }}` es el nombre del servidor en el inventario (web1 o web2). Lo verás en detalle en el próximo módulo."),
  ("term", """$ cd ansible
$ ansible-playbook site.yml --syntax-check
$ ansible-playbook site.yml
...
PLAY RECAP ********************************************************
web1 : ok=6  changed=3  unreachable=0  failed=0
web2 : ok=6  changed=3  unreachable=0  failed=0"""),
  ("p", "Abre las direcciones que te da Terraform:"),
  ("term", """$ terraform -chdir=../terraform output urls
{
  "web1" = "http://54.170.10.20"
  "web2" = "http://54.170.10.21"
}
$ curl http://54.170.10.20
<h1>Mi web en la nube</h1><p>Servidor web1</p>"""),
  ("tip", "Ejecuta el playbook una segunda vez: debe terminar con `changed=0`."),
  ("p", "Resultado de este paso: tus dos servidores sirven una web. Es tu primer resultado visible del proyecto."),
 ],
}
