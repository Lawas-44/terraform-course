# -*- coding: utf-8 -*-
# Módulo 01 · Preparación del entorno

LECCION = [
 ("h", "La terminal sin miedo"),
 ("p", "Terraform se usa desde la **terminal** (también llamada consola, shell o línea de comandos). Si nunca la has usado, estos son los conceptos mínimos:"),
 ("ul", [
  "**Linux y macOS** usan Bash o Zsh. Abre la app «Terminal».",
  "**Windows**: usa **PowerShell** (viene instalado) o, mejor aún, instala **WSL** (Windows Subsystem for Linux) para tener una terminal Linux real: `wsl --install`.",
  "Siempre estás «dentro» de una carpeta (el *directorio de trabajo*). Terraform trabaja sobre la carpeta en la que estás.",
 ]),
 ("code", "bash", "Bash / Zsh", """pwd                      # ¿en qué carpeta estoy?
ls -la                   # ¿qué hay aquí? (-a muestra ocultos)
mkdir -p terraform-labs  # crear carpeta
cd terraform-labs        # entrar en ella
cd ..                    # subir un nivel
code .                   # abrir la carpeta actual en VS Code"""),
 ("code", "bash", "PowerShell (equivalentes)", """Get-Location             # o simplemente: pwd
Get-ChildItem -Force     # o: ls
mkdir terraform-labs
cd terraform-labs
cd ..
code ."""),
 ("tip", "Pulsa <kbd>Tab</kbd> para autocompletar nombres de archivos y comandos, y las flechas <kbd>↑</kbd> <kbd>↓</kbd> para recuperar comandos anteriores. Te ahorrarán miles de pulsaciones."),

 ("h", "Instalar Terraform"),
 ("p", "Elige el método de tu sistema operativo. Todos instalan el mismo binario `terraform`."),
 ("code", "bash", "macOS (Homebrew)", """brew tap hashicorp/tap
brew install hashicorp/tap/terraform"""),
 ("code", "bash", "Ubuntu / Debian / WSL", """sudo apt-get update && sudo apt-get install -y gnupg software-properties-common curl
curl -fsSL https://apt.releases.hashicorp.com/gpg | \\
  sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] \\
https://apt.releases.hashicorp.com $(lsb_release -cs) main" | \\
  sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt-get update && sudo apt-get install -y terraform"""),
 ("code", "bash", "Windows (PowerShell)", """winget install HashiCorp.Terraform
# o con Chocolatey:
choco install terraform"""),
 ("p", "Cierra y vuelve a abrir la terminal y comprueba la instalación:"),
 ("term", """$ terraform version
Terraform v1.x.x
on linux_amd64"""),
 ("p", "Activa el autocompletado (Bash/Zsh) para que <kbd>Tab</kbd> complete subcomandos de Terraform:"),
 ("code", "bash", "terminal", "terraform -install-autocomplete"),

 ("h", "Gestionar varias versiones con tfenv"),
 ("p", "En proyectos reales cada repositorio puede exigir una versión distinta de Terraform. Herramientas como **tfenv** (o **tenv**, que también soporta OpenTofu) permiten tener varias instaladas y cambiar entre ellas."),
 ("code", "bash", "tfenv", """brew install tfenv                # macOS (en Linux: git clone de tfenv)
tfenv list-remote | head          # versiones disponibles
tfenv install 1.10.5              # instala una versión
tfenv use 1.10.5                  # la activa
echo "1.10.5" > .terraform-version   # fija la versión para este proyecto"""),
 ("info", "Para este curso basta con cualquier versión **1.10 o superior**. Si ya instalaste Terraform con el gestor de paquetes, no necesitas tfenv todavía."),

 ("h", "El editor: VS Code"),
 ("p", "Puedes usar cualquier editor, pero **Visual Studio Code** con la extensión oficial **HashiCorp Terraform** te da resaltado de sintaxis, autocompletado de recursos y argumentos, documentación al pasar el ratón y formateo automático."),
 ("ol", [
  "Instala VS Code desde code.visualstudio.com.",
  "Abre la pestaña de extensiones (<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>X</kbd>) y busca «HashiCorp Terraform».",
  "Activa el formateo al guardar con este ajuste en `settings.json`:",
 ]),
 ("code", "json", ".vscode/settings.json", """{
  "[terraform]": {
    "editor.defaultFormatter": "hashicorp.terraform",
    "editor.formatOnSave": true
  },
  "[terraform-vars]": {
    "editor.defaultFormatter": "hashicorp.terraform",
    "editor.formatOnSave": true
  }
}"""),

 ("h", "Git y un .gitignore correcto"),
 ("p", "Todo el código del curso irá a un repositorio Git. Configura tu identidad una sola vez:"),
 ("code", "bash", "terminal", """git config --global user.name "Tu Nombre"
git config --global user.email "tu@email.com"
git config --global init.defaultBranch main"""),
 ("p", "Y crea el repositorio de prácticas con un `.gitignore` **antes del primer commit**. Algunos archivos que genera Terraform contienen secretos o son enormes y nunca deben subirse:"),
 ("code", "text", ".gitignore", """.terraform/
*.tfstate
*.tfstate.*
*.tfplan
crash.log
*.tfvars
!example.tfvars
override.tf
*_override.tf"""),
 ("table", ["Archivo", "¿A Git?", "Por qué"], [
  ["`*.tf`", "✅ Sí", "Es tu código"],
  ["`.terraform.lock.hcl`", "✅ Sí", "Fija las versiones de providers para todo el equipo"],
  ["`.terraform/`", "❌ No", "Plugins descargados (cientos de MB), se regeneran con `init`"],
  ["`*.tfstate`", "❌ No", "Contiene IDs, IPs y a veces contraseñas en texto plano"],
  ["`*.tfvars`", "⚠️ Depende", "Si contiene secretos, nunca. Si son valores públicos, puede subirse"],
 ]),
 ("warn", "Antes de cada `git add`, ejecuta `git status` y revisa qué vas a subir. Un secreto en GitHub hay que considerarlo comprometido aunque lo borres después."),

 ("h", "Cuenta de AWS segura (necesaria desde el módulo 5)"),
 ("p", "Los módulos 0 a 4 no necesitan nube. Para el resto usaremos AWS. Prepárala bien desde el principio:"),
 ("ol", [
  "Crea la cuenta en aws.amazon.com. El email y contraseña con los que te registras son el usuario **root**: el más poderoso.",
  "Activa **MFA** en el usuario root (IAM → Security credentials) y guárdalo. No vuelvas a usar root para el día a día.",
  "Crea un usuario de trabajo. Lo recomendable es **IAM Identity Center** (inicio de sesión con SSO y credenciales temporales). Alternativa sencilla para aprender: un usuario IAM con la política `AdministratorAccess`, MFA y access keys.",
  "Crea un **presupuesto** en *Billing → Budgets*: «Monthly cost budget» de 5 USD con alerta por email al 80 %.",
 ]),
 ("p", "Instala la **AWS CLI v2** y configura las credenciales en un perfil con nombre:"),
 ("code", "bash", "Opción A: IAM Identity Center (recomendado)", """aws configure sso
# SSO session name: curso
# SSO start URL:    https://xxxxxxxx.awsapps.com/start
# SSO region:       eu-west-1
# ...elige cuenta y rol...
# CLI profile name: curso-terraform

aws sso login --profile curso-terraform   # cuando caduque la sesión"""),
 ("code", "bash", "Opción B: usuario IAM con access keys", """aws configure --profile curso-terraform
# AWS Access Key ID:     AKIA...
# AWS Secret Access Key: ****
# Default region name:   eu-west-1
# Default output format: json"""),
 ("p", "Comprueba que funciona. Este comando es tu mejor amigo cuando algo falle con credenciales:"),
 ("term", """$ aws sts get-caller-identity --profile curso-terraform
{
    "UserId": "AIDA...",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/alumno"
}"""),
 ("warn", "Nunca escribas access keys dentro de archivos `.tf`. Terraform las leerá del perfil o de variables de entorno, como veremos en el módulo 5."),
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
