# -*- coding: utf-8 -*-
# Módulo 19 · Terraform y Ansible juntos

LECCION = [
 ("h", "Quién hace qué"),
 ("p", "Ya conoces las dos herramientas. Cada una tiene su trabajo:"),
 ("table", ["Tarea", "Herramienta"], [
  ["Crear la red, el firewall y los servidores", "Terraform"],
  ["Crear la clave SSH en AWS", "Terraform"],
  ["Instalar programas en los servidores", "Ansible"],
  ["Copiar la web y los archivos de configuración", "Ansible"],
  ["Arrancar y recargar servicios", "Ansible"],
 ]),
 ("p", "La pregunta es cómo pasar la información de una a otra. Ansible necesita saber **las IPs de los servidores**, y esas IPs las conoce Terraform."),
 ("code", "text", "flujo", """terraform apply  -->  servidores creados  -->  IPs
                                                 |
                                                 v
                                         inventario de Ansible
                                                 |
                                                 v
                              ansible-playbook  -->  servidores configurados"""),

 ("h", "Opción 1: Terraform escribe el inventario"),
 ("p", "La forma más sencilla: Terraform genera el archivo de inventario con una plantilla, usando `templatefile` y `local_file` (módulo 8)."),
 ("code", "text", "templates/inventario.ini.tftpl", """[web]
%{ for nombre, ip in servidores ~}
${nombre} ansible_host=${ip}
%{ endfor ~}

[web:vars]
ansible_user=ubuntu"""),
 ("code", "hcl", "main.tf", """resource "local_file" "inventario" {
  filename = "${path.module}/../ansible/inventario/hosts.ini"
  content = templatefile("${path.module}/templates/inventario.ini.tftpl", {
    servidores = { for nombre, s in aws_instance.web : nombre => s.public_ip }
  })
}"""),
 ("p", "Cada vez que hagas `terraform apply`, el inventario se actualiza solo con las IPs nuevas."),
 ("tip", "No subas el inventario generado a Git (añádelo a `.gitignore`): se regenera siempre y las IPs cambian."),

 ("h", "Opción 2: inventario dinámico de AWS"),
 ("p", "Ansible también puede **preguntar directamente a AWS** qué servidores hay, buscándolos por sus etiquetas. Necesita la colección `amazon.aws`:"),
 ("term", """$ ansible-galaxy collection install amazon.aws
$ pip install boto3 botocore"""),
 ("code", "yaml", "inventario/aws_ec2.yml", """---
plugin: amazon.aws.aws_ec2
regions:
  - eu-west-1
filters:
  tag:Rol: web
  instance-state-name: running
keyed_groups:
  - key: tags.Rol
    prefix: ""
    separator: ""
hostnames:
  - tag:Name
compose:
  ansible_host: public_ip_address"""),
 ("term", """$ ansible-inventory -i inventario/aws_ec2.yml --graph
@all:
  |--@web:
  |  |--miweb-dev-web1
  |  |--miweb-dev-web2"""),
 ("ul", [
  "Busca los servidores con la etiqueta `Rol = web` (la ponemos en Terraform).",
  "Los agrupa por esa etiqueta: aparece el grupo `web`.",
  "Usa la IP pública para conectarse.",
 ]),
 ("table", ["", "Inventario generado por Terraform", "Inventario dinámico"], [
  ["Dificultad", "Muy sencillo", "Necesita instalar la colección y boto3"],
  ["Si alguien crea servidores a mano", "No los ve", "Los ve si tienen la etiqueta"],
  ["Ideal para", "Proyectos pequeños y aprender", "Muchos servidores o entornos que cambian"],
 ]),
 ("p", "En el proyecto usamos la opción 1."),

 ("h", "Esperar a que los servidores estén listos"),
 ("p", "Justo después de `terraform apply`, los servidores están arrancando y aún no aceptan SSH. Si lanzas Ansible en ese momento, falla. El módulo `wait_for_connection` espera hasta que se puede entrar:"),
 ("term", """$ ansible web -m ansible.builtin.wait_for_connection -a "timeout=300"
web1 | SUCCESS => { "changed": false, "elapsed": 24 }
web2 | SUCCESS => { "changed": false, "elapsed": 26 }"""),

 ("h", "Todo con un comando"),
 ("p", "Ahora junta los pasos en un **script**: un archivo con comandos que se ejecutan en orden."),
 ("code", "bash", "scripts/desplegar.sh", """#!/usr/bin/env bash
set -euo pipefail          # parar si algún comando falla
cd "$(dirname "$0")/.."    # ir a la carpeta del proyecto

echo "==> 1/3 Creando la infraestructura con Terraform"
terraform -chdir=terraform apply -auto-approve

echo "==> 2/3 Esperando a que los servidores acepten SSH"
cd ansible
ansible web -m ansible.builtin.wait_for_connection -a "timeout=300"

echo "==> 3/3 Configurando los servidores con Ansible"
ansible-playbook site.yml --ask-vault-pass

echo "Listo. Tu web está en:"
terraform -chdir=../terraform output urls"""),
 ("term", """$ chmod +x scripts/desplegar.sh
$ ./scripts/desplegar.sh"""),
 ("info", "Aquí sí usamos `-auto-approve` porque el script lo ejecutas tú a propósito. Si prefieres revisar el plan antes, quítalo y Terraform te pedirá confirmación."),

 ("h", "Otras formas de unirlos"),
 ("ul", [
  "**Provisioner `local-exec`**: Terraform ejecuta `ansible-playbook` al crear cada servidor. Funciona, pero solo se ejecuta al crear, no cuando cambias la configuración.",
  "**Provider `ansible/ansible`**: Terraform registra los servidores en un inventario de Ansible.",
  "**Packer**: crea una imagen de servidor ya configurada (puede usar Ansible para ello) y Terraform lanza servidores desde esa imagen. Es la opción más robusta en empresas grandes.",
  "**user_data / cloud-init**: un script al arrancar (módulo 6). Bueno para cosas sencillas.",
 ]),
]

TEST = [
 ("¿Qué necesita Ansible que solo conoce Terraform?",
  ["La contraseña del vault", "Las IPs de los servidores", "Los roles", "El nombre del playbook"], 1,
  "Terraform crea los servidores y sabe qué IP tiene cada uno."),
 ("¿Cómo genera Terraform el inventario de Ansible en el proyecto?",
  ["Con un output", "Con templatefile y local_file", "Con un data source", "Con un provisioner remote-exec"], 1,
  "La plantilla se rellena con las IPs y se guarda como archivo."),
 ("¿Qué hace el inventario dinámico `amazon.aws.aws_ec2`?",
  ["Crea servidores", "Pregunta a AWS qué servidores hay y los agrupa", "Cifra el inventario", "Instala Ansible"], 1,
  "Busca los servidores por región, filtros y etiquetas."),
 ("Lanzas Ansible justo después de `terraform apply` y sale UNREACHABLE. ¿Qué haces?",
  ["Borrar el servidor", "Esperar con wait_for_connection antes del playbook", "Cambiar de región", "Desactivar SSH"], 1,
  "Los servidores tardan unos segundos en aceptar conexiones."),
 ("¿Por qué no se sube a Git el inventario generado?",
  ["Porque contiene contraseñas", "Porque se regenera en cada apply y las IPs cambian", "Porque Git no admite .ini", "Sí se sube"], 1, ""),
 ("¿Qué hace `set -euo pipefail` en el script?",
  ["Lo ejecuta más rápido", "Hace que el script se pare si un comando falla", "Lo cifra", "Muestra los comandos"], 1,
  "Así no se ejecuta Ansible si Terraform ha fallado."),
]

RETOS = [
 {"titulo": "Script para destruir",
  "enunciado": "Escribe `scripts/destruir.sh` que borre toda la infraestructura del proyecto pidiendo confirmación.",
  "pista": "Sin `-auto-approve`, Terraform pide escribir yes.",
  "solucion": ("bash", """#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
terraform -chdir=terraform destroy""")},
 {"titulo": "Grupo por entorno",
  "enunciado": "Cambia la plantilla del inventario para que, además del grupo `web`, cree un grupo con el nombre del entorno (`dev` o `prod`) que incluya a `web`.",
  "pista": "En INI, un grupo de grupos se escribe `[dev:children]` seguido de los nombres de los grupos. Pasa `entorno` a templatefile.",
  "solucion": ("text", """# templates/inventario.ini.tftpl
[web]
%{ for nombre, ip in servidores ~}
${nombre} ansible_host=${ip}
%{ endfor ~}

[${entorno}:children]
web

[web:vars]
ansible_user=ubuntu

# main.tf
#   content = templatefile(".../inventario.ini.tftpl", {
#     servidores = module.servidores.ips
#     entorno    = var.entorno
#   })""")},
]

PROYECTO = {
 "titulo": "Despliegue con un solo comando",
 "bloques": [
  ("p", "Ya tienes todas las piezas. Ahora vas a crear dos scripts para desplegar y borrar el proyecto completo con un comando, y lo probarás desde cero."),
  ("p", "1. Crea `scripts/desplegar.sh` con el contenido de la lección y `scripts/destruir.sh` con el del reto 1. Dales permiso de ejecución:"),
  ("term", """$ chmod +x scripts/desplegar.sh scripts/destruir.sh"""),
  ("p", "2. Añade al `.gitignore` del proyecto los archivos que no deben subirse. El `vault.yml` cifrado sí puede subirse a tu repositorio:"),
  ("code", "text", ".gitignore (añadir)", """ansible/inventario/hosts.ini
terraform/terraform.tfvars
terraform/backend.hcl"""),
  ("p", "3. La prueba de fuego: destruye todo y vuelve a crearlo con un solo comando."),
  ("term", """$ ./scripts/destruir.sh
...
Destroy complete! Resources: 13 destroyed.

$ ./scripts/desplegar.sh
==> 1/3 Creando la infraestructura con Terraform
...
Apply complete! Resources: 13 added, 0 changed, 0 destroyed.
==> 2/3 Esperando a que los servidores acepten SSH
web1 | SUCCESS => { "changed": false, "elapsed": 31 }
web2 | SUCCESS => { "changed": false, "elapsed": 33 }
==> 3/3 Configurando los servidores con Ansible
Vault password:
...
PLAY RECAP ********************************************************
web1 : ok=15  changed=11  unreachable=0  failed=0
web2 : ok=15  changed=11  unreachable=0  failed=0

Listo. Tu web está en:
{
  "web1" = "http://34.245.71.12"
  "web2" = "http://52.48.199.30"
}"""),
  ("p", "En unos tres minutos, desde cero, tienes dos servidores con tu web funcionando. Las IPs son nuevas, pero no has tenido que tocar el inventario: Terraform lo ha regenerado."),
  ("p", "Resultado de este paso: el proyecto completo se crea con `./scripts/desplegar.sh` y se borra con `./scripts/destruir.sh`."),
 ],
}
