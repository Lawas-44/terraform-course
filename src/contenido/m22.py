# -*- coding: utf-8 -*-
# Módulo 22 · Proyecto final y siguientes pasos

LECCION = [
 ("h", "Lo que has construido"),
 ("p", "Si has seguido los pasos del proyecto, tienes un repositorio que crea y configura una web real en AWS con un solo comando. Repasemos todas las piezas:"),
 ("table", ["Pieza", "Herramienta", "Dónde está"], [
  ["Red propia (VPC, subred, internet gateway)", "Terraform", "`terraform/modules/red`"],
  ["Firewall: SSH solo desde tu IP, HTTP abierto", "Terraform", "`terraform/modules/servidores`"],
  ["Dos servidores Ubuntu con disco cifrado", "Terraform", "`terraform/modules/servidores`"],
  ["Clave SSH en AWS", "Terraform", "`terraform/main.tf`"],
  ["Estado guardado en S3 con bloqueo", "Terraform", "`terraform/versions.tf`"],
  ["Inventario de Ansible generado", "Terraform", "`terraform/templates/inventario.ini.tftpl`"],
  ["Paquetes básicos y mensaje de bienvenida", "Ansible", "`ansible/roles/comun`"],
  ["nginx configurado con handler", "Ansible", "`ansible/roles/nginx`"],
  ["Tu web, página de estado y zona privada", "Ansible", "`ansible/roles/web`"],
  ["Contraseña cifrada", "Ansible Vault", "`ansible/inventario/group_vars/all/vault.yml`"],
  ["Tests y revisiones automáticas", "Terraform test, ansible-lint, GitHub Actions", "`terraform/tests`, `.github/workflows`"],
  ["Despliegue con un comando", "Bash", "`scripts/`"],
 ]),

 ("h", "La prueba final: desde cero"),
 ("p", "Un proyecto de infraestructura está bien hecho cuando **otra persona** puede desplegarlo solo leyendo el README. Haz la prueba: clona tu repositorio en otra carpeta y sigue tus propias instrucciones."),
 ("term", """$ git clone https://github.com/tu-usuario/mi-web-en-la-nube.git prueba
$ cd prueba
$ cp terraform/terraform.tfvars.example terraform/terraform.tfvars
$ terraform -chdir=terraform init -backend-config=backend.hcl
$ ./scripts/desplegar.sh"""),
 ("p", "Comprueba el resultado en los dos servidores:"),
 ("term", """$ curl -s http://34.245.71.12 | grep h1
  <h1>Ana García</h1>
$ curl -s http://52.48.199.30/estado.html | grep "Nombre en"
    <tr><th>Nombre en el inventario</th><td>web2</td></tr>
$ curl -s -o /dev/null -w "%{http_code}\n" http://34.245.71.12/privado/
401"""),

 ("h", "Escribe el README"),
 ("p", "El README es lo primero que ve alguien en tu repositorio. Debe explicar qué es, qué necesita y cómo se usa. Una plantilla:"),
 ("code", "text", "README.md", """# Mi web en la nube

Web personal desplegada en AWS con Terraform y Ansible.

## Qué crea
- Una VPC con una subred pública.
- Dos servidores Ubuntu con nginx.
- Mi web, una página de estado y una zona privada.

## Requisitos
- Terraform 1.10 o superior y Ansible.
- Una cuenta de AWS configurada (`aws sts get-caller-identity`).
- Una clave SSH en ~/.ssh/id_ed25519.pub.

## Uso
1. Copia `terraform/terraform.tfvars.example` como `terraform.tfvars` y pon tu IP.
2. `./scripts/desplegar.sh`
3. Abre las URLs que aparecen al final.
4. Al terminar: `./scripts/destruir.sh`

## Coste
Dentro de la capa gratuita de AWS. Fuera de ella, unos céntimos por hora."""),

 ("h", "No olvides destruir"),
 ("term", """$ ./scripts/destruir.sh
...
Destroy complete! Resources: 13 destroyed."""),
 ("p", "Al día siguiente, entra en la web de AWS (sección EC2) y comprueba que no quedan servidores encendidos. El bucket del estado (del paso del módulo 10) cuesta prácticamente cero y puedes dejarlo."),

 ("h", "Cómo mejorar el proyecto"),
 ("p", "Si quieres seguir practicando, estas mejoras usan lo que ya sabes y añaden algo nuevo:"),
 ("table", ["Mejora", "Qué aprenderás"], [
  ["Un balanceador de carga delante de los dos servidores", "Recursos `aws_lb` en Terraform"],
  ["HTTPS con un dominio y certificado gratuito (Let's Encrypt)", "Route 53 y un rol de Ansible para certbot"],
  ["Un entorno `prod` además de `dev`", "Workspaces o carpetas por entorno"],
  ["Una base de datos para un formulario de contacto", "RDS y contraseñas gestionadas por AWS"],
  ["Imagen de servidor ya configurada", "Packer con Ansible"],
  ["Monitorización y alertas", "CloudWatch con Terraform"],
 ]),

 ("h", "Certificaciones"),
 ("ul", [
  "**HashiCorp Certified: Terraform Associate**: examen online de unos 60 minutos con preguntas tipo test. Este curso cubre su temario.",
  "**Red Hat Certified Engineer (RHCE)**: la certificación más conocida de Ansible. Es práctica (resuelves tareas en servidores reales) y más exigente: requiere conocer bien Linux.",
 ]),
 ("p", "Consulta siempre los detalles actualizados en las webs oficiales. Para prepararte, repite los tests de todos los módulos y el simulacro de abajo."),

 ("h", "Qué aprender después"),
 ("ul", [
  "**Linux**: cuanto mejor lo conozcas, más fácil te será Ansible.",
  "**Docker y Kubernetes**: Terraform crea los clústeres y hay providers y módulos de Ansible para gestionarlos.",
  "**Otra nube** (Azure o Google Cloud): el flujo de Terraform y Ansible es el mismo; solo cambian los recursos.",
  "**Terragrunt**, **OpenTofu** y **Packer**: herramientas del mismo ecosistema.",
 ]),
]

TEST = [('Simulacro · ¿Qué comando debes ejecutar tras añadir un nuevo provider al código?',
  ['terraform plan', 'terraform init', 'terraform refresh', 'terraform providers'],
  1,
  'Cualquier provider o módulo nuevo requiere init.'),
 ('Simulacro · ¿Qué afirmación sobre el estado es FALSA?',
  ['Puede contener secretos',
   'Debe guardarse en un backend remoto en equipos',
   'Terraform lo necesita para funcionar',
   'Es seguro subirlo a un repositorio público si se marca sensitive'],
  3,
  '`sensitive` no cifra nada en el estado.'),
 ('Simulacro · ¿Qué hace `terraform apply -refresh-only`?',
  ['Recrea todos los recursos',
   'Actualiza el estado para que refleje la realidad sin modificar la infraestructura',
   'Destruye el drift',
   'Actualiza los providers'],
  1,
  'Sincroniza estado ← realidad, previa confirmación.'),
 ('Simulacro · Tienes `variable "x" { default = 1 }`, `TF_VAR_x=2` y `x = 3` en terraform.tfvars. ¿Valor de '
  'var.x?',
  ['1', '2', '3', 'Error'],
  2,
  'terraform.tfvars tiene prioridad sobre las variables de entorno.'),
 ('Simulacro · ¿Qué meta-argumento evita recrear recursos al quitar un elemento intermedio de una colección?',
  ['count', 'for_each', 'depends_on', 'provider'],
  1,
  'for_each identifica cada copia por clave, no por posición.'),
 ('Simulacro · ¿Dónde se guardan los providers descargados por init?',
  ['En ~/.aws', 'En la carpeta .terraform del proyecto', 'En el estado', 'En el lock file'],
  1,
  'El lock file solo guarda versiones y hashes; los binarios van a .terraform/.'),
 ('Simulacro · ¿Qué variable de entorno activa los logs detallados de Terraform?',
  ['TF_DEBUG', 'TF_LOG', 'TERRAFORM_VERBOSE', 'TF_VAR_log'],
  1,
  'TF_LOG=TRACE|DEBUG|INFO|WARN|ERROR; TF_LOG_PATH para guardarlos.'),
 ('Simulacro · ¿Cómo referencias el output `vpc_id` del módulo `network`?',
  ['network.vpc_id', 'module.network.vpc_id', 'output.network.vpc_id', 'data.network.vpc_id'],
  1,
  'module.NOMBRE.OUTPUT.'),
 ('Simulacro · ¿Qué bloque permite renombrar un recurso sin destruirlo y queda registrado en el código?',
  ['import', 'moved', 'removed', 'rename'],
  1,
  'Disponible desde Terraform 1.1.'),
 ('Simulacro · ¿Qué es cierto sobre los workspaces CLI?',
  ['Cada uno tiene su propio estado con el mismo código',
   'Cada uno tiene su propio código',
   'Sustituyen al backend',
   'Solo existen en HCP Terraform'],
  0,
  'Mismo código, estados separados; `terraform.workspace` da el nombre actual.'),
 ('Simulacro · ¿Cómo se conecta Ansible a servidores Linux?',
  ['Con un agente instalado', 'Por SSH', 'Por la API de la nube', 'Por HTTP'],
  1,
  'Ansible no necesita agentes: entra por SSH.'),
 ('Simulacro · ¿Cuándo se ejecuta un handler de Ansible?',
  ['Siempre', 'Cuando una tarea con notify ha cambiado algo', 'Al principio', 'Solo si hay errores'],
  1,
  'Y se ejecuta una sola vez, al final.'),
 ('Simulacro · ¿Qué carpeta de un rol tiene la prioridad de variables más baja?',
  ['vars/', 'defaults/', 'tasks/', 'handlers/'],
  1,
  'Por eso es la adecuada para valores que el usuario puede cambiar.'),
 ('Simulacro · En el proyecto, ¿quién escribe el inventario de Ansible?',
  ['La persona a mano', 'Terraform, con templatefile y local_file', 'AWS', 'GitHub Actions'],
  1,
  'Así las IPs siempre están al día.')]

RETOS = [
 {"titulo": "Un tercer servidor",
  "enunciado": "Añade un servidor `web3` al proyecto. ¿Qué archivos tienes que tocar? ¿Hay que cambiar algo en Ansible?",
  "pista": "Piensa en la variable `servidores` y en cómo se genera el inventario.",
  "solucion": ("hcl", """# Solo hay que cambiar terraform/terraform.tfvars:
servidores = {
  web1 = "t3.micro"
  web2 = "t3.micro"
  web3 = "t3.micro"
}
# ./scripts/desplegar.sh
# Terraform crea web3 y lo añade al inventario.
# Ansible no cambia: el playbook se aplica a todo el grupo web.""")},
 {"titulo": "Cambia tu web sin tocar los servidores a mano",
  "enunciado": "Añade un cuarto proyecto a tu web y publícalo. ¿Qué comando ejecutas? ¿Qué tareas aparecen como changed?",
  "pista": "Los datos de la web están en group_vars.",
  "solucion": ("yaml", """# ansible/inventario/group_vars/all/web.yml
web_proyectos:
  # ... los tres anteriores ...
  - nombre: "Mi cuarto proyecto"
    descripcion: "Añadido con Ansible."

# cd ansible && ansible-playbook site.yml --ask-vault-pass
# Solo cambia "Generar la página principal" en web1 y web2.""")},
]

PROYECTO = {
 "titulo": "Despliegue final y entrega",
 "bloques": [
  ("p", "Último paso: comprueba que todo funciona desde cero, documenta el proyecto y destrúyelo."),
  ("ol", [
   "Clona tu repositorio en una carpeta nueva y despliega siguiendo solo tu README.",
   "Abre la web en los dos servidores y comprueba que se ve tu nombre y tus proyectos.",
   "Abre `/estado.html` en cada uno: cada servidor muestra sus propios datos.",
   "Entra en `/privado/` con tu usuario y contraseña.",
   "Comprueba que GitHub Actions está en verde.",
   "Haz una captura de la web y añádela al README: es tu proyecto de portfolio.",
   "Destruye todo con `./scripts/destruir.sh`.",
  ]),
  ("p", "Lista de comprobación final:"),
  ("table", ["Comprobación", "Cómo verlo"], [
   ["Se despliega desde cero con un comando", "`./scripts/desplegar.sh` termina sin errores"],
   ["El playbook es idempotente", "La segunda ejecución da `changed=0`"],
   ["No hay secretos en Git", "`git log -p` no muestra contraseñas ni `.tfstate`"],
   ["Los tests pasan", "`terraform test` y `ansible-lint` sin errores"],
   ["Todo se borra", "`./scripts/destruir.sh` y la consola de EC2 vacía"],
  ]),
  ("p", "Enhorabuena: has construido infraestructura real con Terraform, la has configurado con Ansible y lo has automatizado todo. El código completo de referencia está en la carpeta `proyecto/` del repositorio del curso."),
 ],
}
