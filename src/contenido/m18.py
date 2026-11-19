# -*- coding: utf-8 -*-
# Módulo 18 · Ansible Vault y buenas prácticas

LECCION = [
 ("h", "El problema de las contraseñas"),
 ("p", "Tarde o temprano necesitarás una contraseña en tu código: la de una base de datos, la de una zona privada... Si la escribes tal cual en un archivo YAML y lo subes a Git, cualquiera con acceso al repositorio la verá."),
 ("p", "**Ansible Vault** cifra archivos con una contraseña. El archivo cifrado sí se puede subir a Git: sin la contraseña del vault no se puede leer."),

 ("h", "Cifrar un archivo"),
 ("p", "Crea un archivo de variables normal y luego cífralo:"),
 ("code", "yaml", "secretos.yml (antes de cifrar)", """---
db_password: "MiContraseñaSecreta123\""""),
 ("term", """$ ansible-vault encrypt secretos.yml
New Vault password:
Confirm New Vault password:
Encryption successful
$ cat secretos.yml
$ANSIBLE_VAULT;1.1;AES256
62313365396662343061393464336163383764373764613633653634306231386433626436623361
6230653332656362336431643739643739653330643738310a3632626565313236363461366366..."""),
 ("p", "Ahora el archivo es ilegible. Comandos útiles:"),
 ("table", ["Comando", "Qué hace"], [
  ["`ansible-vault create archivo.yml`", "Crea un archivo nuevo ya cifrado"],
  ["`ansible-vault encrypt archivo.yml`", "Cifra un archivo existente"],
  ["`ansible-vault view archivo.yml`", "Muestra el contenido sin descifrar el archivo"],
  ["`ansible-vault edit archivo.yml`", "Abre el editor para cambiarlo"],
  ["`ansible-vault decrypt archivo.yml`", "Lo deja sin cifrar (con cuidado)"],
 ]),

 ("h", "Usar variables cifradas"),
 ("p", "Las variables cifradas se usan igual que las demás. Si el archivo está en `group_vars`, Ansible lo carga solo. Al ejecutar, hay que darle la contraseña del vault:"),
 ("term", """$ ansible-playbook site.yml --ask-vault-pass
Vault password:"""),
 ("p", "Si no la das, Ansible avisa:"),
 ("term", """ERROR! Attempting to decrypt but no vault secrets found"""),
 ("p", "También puedes guardar la contraseña en un archivo (fuera del repositorio) y usar `--vault-password-file`:"),
 ("term", """$ echo "mi-contraseña-del-vault" > ~/.vault_pass
$ chmod 600 ~/.vault_pass
$ ansible-playbook site.yml --vault-password-file ~/.vault_pass"""),
 ("warn", "La contraseña del vault **nunca** se sube a Git. Guárdala en un gestor de contraseñas."),

 ("h", "Que no se vean en pantalla: no_log"),
 ("p", "Aunque la variable esté cifrada, si una tarea la usa, Ansible podría mostrarla en la salida. Para evitarlo, añade `no_log: true` a esa tarea:"),
 ("code", "yaml", "no_log", """- name: Guardar la contraseña de la base de datos
  ansible.builtin.copy:
    content: "{{ db_password }}"
    dest: /etc/miapp/db_pass
    mode: "0600"
  no_log: true"""),

 ("h", "Configurar Ansible: ansible.cfg"),
 ("p", "Ya usas `ansible.cfg`. Estas son las opciones más útiles:"),
 ("code", "text", "ansible.cfg", """[defaults]
inventory = inventario/hosts.ini      # inventario por defecto
roles_path = roles                    # dónde están los roles
host_key_checking = False             # no preguntar por servidores nuevos
interpreter_python = auto_silent      # elegir Python sin avisos

[ssh_connection]
pipelining = True                     # conexiones más rápidas"""),

 ("h", "Revisar el código: ansible-lint"),
 ("p", "**ansible-lint** revisa tus playbooks y roles y avisa de errores y malas prácticas: nombres de módulos incompletos, permisos de archivo sin indicar, comandos que deberían ser módulos..."),
 ("term", """$ pipx install ansible-lint
$ ansible-lint
WARNING  Listing 2 violation(s) that are fatal
fqcn[action-core]: Use FQCN for builtin module actions (copy).
roles/web/tasks/main.yml:3
risky-file-permissions: File permissions unset or incorrect.
roles/web/tasks/main.yml:3

Failed: 2 failure(s), 0 warning(s) in 9 files processed."""),
 ("p", "En este ejemplo pide escribir `ansible.builtin.copy` en lugar de `copy`, e indicar los permisos con `mode`. Tras corregirlo:"),
 ("term", """$ ansible-lint
Passed: 0 failure(s), 0 warning(s) in 9 files processed."""),

 ("h", "Buenas prácticas"),
 ("ul", [
  "Pon un `name` claro a cada tarea.",
  "Usa el nombre completo de los módulos (`ansible.builtin.apt`).",
  "Indica siempre `mode` al crear archivos y carpetas.",
  "Usa módulos en lugar de `command` o `shell`. Si usas `command`, añade `changed_when`.",
  "Ejecuta los playbooks dos veces: la segunda debe salir `changed=0`.",
  "Prueba primero con `--check --diff`.",
  "Cifra los secretos con Vault y marca sus tareas con `no_log: true`.",
 ]),
]

TEST = [
 ("¿Para qué sirve Ansible Vault?",
  ["Para guardar copias de seguridad", "Para cifrar archivos con datos secretos", "Para instalar roles", "Para conectar por SSH"], 1,
  "El archivo cifrado puede subirse a Git sin riesgo."),
 ("¿Qué comando cifra un archivo existente?",
  ["ansible-vault create", "ansible-vault encrypt", "ansible-vault lock", "ansible-playbook --encrypt"], 1, ""),
 ("Ejecutas un playbook que usa un archivo cifrado y sale \"no vault secrets found\". ¿Qué falta?",
  ["Instalar Vault", "Añadir --ask-vault-pass", "Descifrar el archivo", "Reiniciar"], 1, "Ansible necesita la contraseña del vault."),
 ("¿Qué hace `no_log: true` en una tarea?",
  ["Que no se ejecute", "Que no muestre sus datos en la salida", "Que no se guarde en Git", "Que no cambie nada"], 1,
  "Evita que un secreto aparezca en pantalla o en los registros."),
 ("¿Qué se puede subir a Git?",
  ["La contraseña del vault", "El archivo cifrado con Vault", "El archivo de contraseñas sin cifrar", "Nada"], 1,
  "El archivo cifrado sí; su contraseña nunca."),
 ("¿Para qué sirve ansible-lint?",
  ["Para ejecutar playbooks más rápido", "Para revisar el código y avisar de errores y malas prácticas", "Para cifrar", "Para crear roles"], 1, ""),
]

RETOS = [
 {"titulo": "Tu primer secreto",
  "enunciado": "Crea con `ansible-vault create` un archivo `secretos.yml` con la variable `api_token`. Escribe un playbook para `local` que guarde el token en `/tmp/token.txt` con permisos 0600 sin mostrarlo en pantalla.",
  "pista": "Carga el archivo con `vars_files` y usa `no_log: true`.",
  "solucion": ("yaml", """---
- name: Guardar un secreto
  hosts: local
  vars_files:
    - secretos.yml
  tasks:
    - name: Guardar el token
      ansible.builtin.copy:
        content: "{{ api_token }}"
        dest: /tmp/token.txt
        mode: "0600"
      no_log: true
# ansible-playbook secreto.yml --ask-vault-pass""")},
 {"titulo": "Limpia un playbook con ansible-lint",
  "enunciado": "Pasa `ansible-lint` sobre este playbook y corrige todos los avisos.",
  "codigo": ("yaml", """- hosts: local
  tasks:
    - copy:
        content: hola
        dest: /tmp/hola.txt
    - shell: mkdir -p /tmp/datos"""),
  "pista": "Faltan nombres, el nombre completo de los módulos y permisos. Y `mkdir` tiene un módulo.",
  "solucion": ("yaml", """---
- name: Ejemplo limpio
  hosts: local
  tasks:
    - name: Crear hola.txt
      ansible.builtin.copy:
        content: hola
        dest: /tmp/hola.txt
        mode: "0644"

    - name: Crear la carpeta de datos
      ansible.builtin.file:
        path: /tmp/datos
        state: directory
        mode: "0755\"""")},
]

PROYECTO = {
 "titulo": "Zona privada con contraseña cifrada",
 "bloques": [
  ("p", "Vas a añadir a tu web una zona `/privado/` protegida con usuario y contraseña. La contraseña estará cifrada con Ansible Vault."),
  ("p", "1. Crea el archivo cifrado con la contraseña:"),
  ("term", """$ cd ansible
$ ansible-vault create inventario/group_vars/all/vault.yml
New Vault password:
Confirm New Vault password:"""),
  ("p", "Se abrirá el editor. Escribe esto y guarda:"),
  ("code", "yaml", "inventario/group_vars/all/vault.yml (descifrado)", """---
web_privado_password: "elige-una-contraseña\""""),
  ("p", "2. Añade el usuario (no es secreto) a `web.yml`:"),
  ("code", "yaml", "inventario/group_vars/all/web.yml (añadir al final)", """web_privado_usuario: "admin\""""),
  ("p", "3. Pide la contraseña en nginx. Añade esto dentro del bloque `server` de `roles/nginx/templates/sitio.conf.j2`:"),
  ("code", "text", "roles/nginx/templates/sitio.conf.j2 (añadir)", """    location /privado/ {
        auth_basic "Zona privada";
        auth_basic_user_file /etc/nginx/.htpasswd;
    }"""),
  ("p", "4. Añade estas tareas al final de `roles/web/tasks/main.yml`. nginx necesita la contraseña en un formato especial (cifrada); la calculamos con `openssl`:"),
  ("code", "yaml", "roles/web/tasks/main.yml (añadir)", """- name: Crear la carpeta privada
  ansible.builtin.file:
    path: "{{ web_raiz }}/privado"
    state: directory
    owner: root
    group: root
    mode: "0755"

- name: Generar la página privada
  ansible.builtin.template:
    src: privado.html.j2
    dest: "{{ web_raiz }}/privado/index.html"
    owner: root
    group: root
    mode: "0644"

- name: Calcular la contraseña cifrada de la zona privada
  ansible.builtin.command:
    cmd: "openssl passwd -6 -salt {{ (inventory_hostname | hash('sha1'))[:16] }} -stdin"
    stdin: "{{ web_privado_password }}"
  register: web_hash
  changed_when: false
  no_log: true

- name: Guardar usuario y contraseña de la zona privada
  ansible.builtin.copy:
    content: "{{ web_privado_usuario }}:{{ web_hash.stdout }}\\n"
    dest: /etc/nginx/.htpasswd
    owner: root
    group: www-data
    mode: "0640"
  no_log: true"""),
  ("info", "El `salt` es un valor que se mezcla con la contraseña al cifrarla. Lo calculamos a partir del nombre del servidor para que siempre salga igual y la tarea no cambie en cada ejecución."),
  ("p", "5. Crea la plantilla `roles/web/templates/privado.html.j2` (está en el repositorio del curso), ejecuta y comprueba:"),
  ("term", """$ ansible-playbook site.yml --ask-vault-pass
$ curl -s -o /dev/null -w "%{http_code}\\n" http://54.170.10.20/privado/
401
$ curl -s -u admin:elige-una-contraseña http://54.170.10.20/privado/ | grep h1
  <h1>Zona privada</h1>
$ ansible-lint
Passed: 0 failure(s), 0 warning(s)"""),
  ("p", "Resultado de este paso: tu web tiene una zona privada. La contraseña está cifrada en Git y nunca aparece en pantalla."),
 ],
}
