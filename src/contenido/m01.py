# -*- coding: utf-8 -*-
# Módulo 01 · Preparación del entorno

LECCION = [
 ("h", "La terminal"),
 ("p", "Terraform se usa escribiendo comandos en la **terminal** (también llamada consola). Es una ventana donde escribes órdenes en lugar de hacer clic."),
 ("ul", [
  "**macOS y Linux**: abre la aplicación «Terminal».",
  "**Windows**: abre **PowerShell**. Si quieres una terminal igual que la de Linux, instala WSL con `wsl --install`.",
 ]),
 ("p", "Siempre estás «dentro» de una carpeta. Terraform trabaja con los archivos de la carpeta en la que estás. Estos comandos te bastan para empezar:"),
 ("term", """$ pwd
/home/ana
$ mkdir terraform-labs
$ cd terraform-labs
$ ls
$ cd .."""),
 ("table", ["Comando", "Qué hace"], [
  ["`pwd`", "Muestra en qué carpeta estás"],
  ["`ls`", "Lista los archivos de la carpeta"],
  ["`mkdir nombre`", "Crea una carpeta"],
  ["`cd nombre`", "Entra en una carpeta"],
  ["`cd ..`", "Vuelve a la carpeta anterior"],
 ]),
 ("tip", "Pulsa <kbd>Tab</kbd> para autocompletar nombres y la flecha hacia arriba para repetir el último comando."),

 ("h", "Instalar Terraform"),
 ("p", "Elige tu sistema operativo:"),
 ("code", "bash", "macOS", """brew tap hashicorp/tap
brew install hashicorp/tap/terraform"""),
 ("code", "bash", "Windows (PowerShell)", """winget install HashiCorp.Terraform"""),
 ("code", "bash", "Ubuntu / Debian / WSL", """sudo apt-get update && sudo apt-get install -y gnupg curl lsb-release
curl -fsSL https://apt.releases.hashicorp.com/gpg | \\
  sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] \\
https://apt.releases.hashicorp.com $(lsb_release -cs) main" | \\
  sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt-get update && sudo apt-get install -y terraform"""),
 ("p", "Cierra la terminal, ábrela de nuevo y comprueba que funciona:"),
 ("term", """$ terraform version
Terraform v1.10.5
on linux_amd64"""),
 ("info", "Para este curso vale cualquier versión **1.10 o superior**. Si algún día necesitas tener varias versiones instaladas, existe la herramienta **tfenv**, que permite cambiar de una a otra."),

 ("h", "El editor de código"),
 ("p", "Te recomendamos **Visual Studio Code** (gratuito) con la extensión **HashiCorp Terraform**. La extensión colorea el código, te sugiere palabras mientras escribes y ordena el código al guardar."),
 ("ol", [
  "Descarga VS Code de code.visualstudio.com.",
  "Abre la sección de extensiones (<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>X</kbd>).",
  "Busca «HashiCorp Terraform» e instálala.",
 ]),

 ("h", "Git y qué archivos no subir nunca"),
 ("p", "Guardaremos el código en Git. Antes de nada, dile a Git quién eres:"),
 ("term", """$ git config --global user.name "Tu Nombre"
$ git config --global user.email "tu@email.com\""""),
 ("p", "Terraform crea algunos archivos que **no** deben subirse a GitHub porque pesan mucho o tienen datos secretos. Para evitarlo, crea un archivo `.gitignore` en tu carpeta con este contenido:"),
 ("code", "text", ".gitignore", """.terraform/
*.tfstate
*.tfstate.*
*.tfplan
*.tfvars"""),
 ("table", ["Archivo", "¿Se sube a Git?", "Motivo"], [
  ["`*.tf`", "Sí", "Es tu código"],
  ["`.terraform.lock.hcl`", "Sí", "Guarda las versiones exactas de los providers"],
  ["`.terraform/`", "No", "Son programas descargados; se pueden volver a descargar"],
  ["`*.tfstate`", "No", "Puede contener contraseñas"],
 ]),
 ("warn", "Antes de subir cambios, ejecuta `git status` y mira la lista de archivos. Si ves un `.tfstate`, no lo subas."),

 ("h", "Cuenta de AWS (a partir del módulo 5)"),
 ("p", "Los módulos 0 a 4 no necesitan nube. Para los siguientes usaremos AWS. Configúrala con cuidado:"),
 ("ol", [
  "Crea la cuenta en aws.amazon.com. El email con el que te registras es el usuario principal (llamado **root**).",
  "Activa la **verificación en dos pasos (MFA)** en ese usuario.",
  "Crea un usuario para trabajar a diario. No uses root para el día a día.",
  "Crea una **alerta de gasto** en *Billing → Budgets*, por ejemplo de 5 dólares. Así AWS te avisará si gastas dinero.",
 ]),
 ("p", "Instala la herramienta de AWS para la terminal (**AWS CLI**) y guarda tus credenciales:"),
 ("term", """$ aws configure --profile curso-terraform
AWS Access Key ID [None]: AKIA...
AWS Secret Access Key [None]: ****
Default region name [None]: eu-west-1
Default output format [None]: json"""),
 ("p", "Comprueba que funciona. Si ves tu número de cuenta, todo está bien:"),
 ("term", """$ aws sts get-caller-identity --profile curso-terraform
{
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/alumno"
}"""),
 ("warn", "Nunca escribas tus claves de AWS dentro de los archivos `.tf`. Terraform las lee solas de la configuración que acabas de crear."),
]

TEST = [
 ("¿Qué comando muestra la carpeta en la que estás trabajando en Bash?",
  ["ls", "pwd", "cd", "whoami"], 1, "`pwd` = *print working directory*."),
 ("¿Cuál de estos archivos SÍ debe subirse a Git?",
  [".terraform/", "terraform.tfstate", ".terraform.lock.hcl", "secretos.tfvars"], 2,
  "El lock file fija las versiones exactas de los providers para todo el equipo; el resto contiene binarios o datos sensibles."),
 ("¿Por qué no se sube el archivo terraform.tfstate a un repositorio?",
  ["Porque es muy pequeño", "Porque puede contener datos sensibles en texto plano", "Porque Git no admite JSON", "Porque se borra solo"], 1,
  "El estado guarda atributos de los recursos, incluidas contraseñas o claves generadas."),
 ("¿Qué comando te dice con qué cuenta y usuario de AWS estás autenticado?",
  ["aws whoami", "aws configure list-users", "aws sts get-caller-identity", "terraform login"], 2,
  "STS (*Security Token Service*) devuelve la cuenta, el usuario/rol y su ARN."),
 ("¿Qué deberías hacer con el usuario root de AWS?",
  ["Usarlo a diario con access keys", "Protegerlo con MFA y no usarlo para el trabajo diario", "Borrarlo", "Compartirlo con el equipo"], 1,
  "Root tiene poder ilimitado. Se protege con MFA y se trabaja con usuarios o roles con permisos acotados."),
 ("¿Para qué sirve tfenv?",
  ["Para cifrar el estado", "Para gestionar varias versiones de Terraform", "Para formatear el código", "Para crear cuentas de AWS"], 1,
  "Permite instalar varias versiones y elegir cuál usar en cada proyecto con `.terraform-version`."),
]

RETOS = [
 {"titulo": "Repositorio de prácticas listo",
  "enunciado": "Crea una carpeta `terraform-labs`, inicializa Git, añade el `.gitignore` de la lección y un `README.md`. Haz el primer commit y súbelo a un repositorio nuevo de GitHub.",
  "pista": "Crea primero el repositorio vacío en GitHub y copia la URL que te da.",
  "solucion": ("bash", """mkdir terraform-labs && cd terraform-labs
git init
# crea .gitignore y README.md con tu editor
git status                 # comprueba que no hay nada raro
git add .gitignore README.md
git commit -m "Primer commit"
git remote add origin https://github.com/TU_USUARIO/terraform-labs.git
git push -u origin main""")},
 {"titulo": "Perfil de AWS por defecto",
  "enunciado": "Haz que la terminal use tu perfil `curso-terraform` sin tener que escribir `--profile` en cada comando.",
  "pista": "Hay una variable de entorno que la AWS CLI y Terraform leen.",
  "solucion": ("bash", """# Bash/Zsh (añádelo a ~/.bashrc o ~/.zshrc para que sea permanente)
export AWS_PROFILE=curso-terraform

# PowerShell
$env:AWS_PROFILE = "curso-terraform"

aws sts get-caller-identity   # ya no hace falta --profile""")},
]
