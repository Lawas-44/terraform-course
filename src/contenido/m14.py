# -*- coding: utf-8 -*-
# Módulo 14 · Trabajo en equipo y CI/CD

LECCION = [
 ("h", "Organizar un repositorio de infraestructura"),
 ("p", "Cuando el código crece y hay varios entornos, una estructura clara es fundamental. La más extendida separa **módulos reutilizables** de **configuraciones por entorno**:"),
 ("code", "text", "estructura recomendada", """infra/
├── bootstrap/               # bucket del estado (se aplica una vez)
├── modules/                 # piezas reutilizables, sin backend ni provider
│   ├── network/
│   ├── web/
│   └── database/
├── envs/
│   ├── dev/
│   │   ├── backend.tf       # key = "dev/terraform.tfstate"
│   │   ├── main.tf          # llama a ../../modules/*
│   │   ├── providers.tf
│   │   └── terraform.tfvars # valores de dev
│   └── prod/
│       ├── backend.tf       # key = "prod/terraform.tfstate"
│       ├── main.tf
│       ├── providers.tf
│       └── terraform.tfvars
├── .github/workflows/terraform.yml
├── .pre-commit-config.yaml
├── .tflint.hcl
└── README.md"""),
 ("code", "hcl", "envs/prod/main.tf", """module "network" {
  source   = "../../modules/network"
  nombre   = "tienda-prod"
  vpc_cidr = "10.10.0.0/16"
}

module "web" {
  source         = "../../modules/web"
  nombre         = "tienda-prod"
  subnet_ids     = module.network.public_subnet_ids
  tipo_instancia = var.tipo_instancia   # t3.medium en prod, t3.micro en dev
  replicas       = var.replicas
}"""),
 ("ul", [
  "Cada entorno tiene **su propio estado**: un error en dev nunca toca prod.",
  "Las diferencias entre entornos están **a la vista** en sus `tfvars`.",
  "Para promocionar un cambio: se prueba en `envs/dev` y después se aplica igual en `envs/prod`.",
 ]),
 ("info", "Herramientas como **Terragrunt** reducen la repetición entre carpetas de entorno. Merece la pena mirarla cuando tengas muchos entornos o cuentas."),

 ("h", "El flujo de trabajo en equipo (GitOps)"),
 ("p", "En un equipo nadie ejecuta `apply` desde su portátil contra producción. El flujo habitual es:"),
 ("code", "text", "flujo con Pull Requests", """ 1. rama nueva      git switch -c feat/aumentar-replicas
 2. cambio          editar envs/prod/terraform.tfvars
 3. Pull Request    ──►  CI: fmt, validate, tflint, trivy, PLAN
                         └─ el plan se publica como comentario en el PR
 4. revisión        un compañero lee el código Y el plan
 5. merge a main    ──►  CI: APPLY (con aprobación manual para prod)"""),
 ("p", "Ventajas: todo cambio queda revisado y registrado, nadie necesita credenciales de producción en su máquina y el plan que se revisa es el que se aplica."),

 ("h", "Planes guardados y códigos de salida"),
 ("p", "En automatización se usan algunas opciones especiales:"),
 ("code", "bash", "terraform en CI", """export TF_IN_AUTOMATION=1        # salida adaptada a CI
terraform init -input=false
terraform plan -input=false -out=tfplan   # guarda el plan
terraform show -no-color tfplan > plan.txt   # versión legible para el PR
terraform apply -input=false tfplan       # aplica EXACTAMENTE ese plan"""),
 ("p", "Aplicar un plan guardado garantiza que se ejecuta lo que se revisó, aunque alguien haya cambiado algo entre medias (si el estado cambió, Terraform rechaza el plan obsoleto)."),
 ("p", "Con `-detailed-exitcode`, `plan` devuelve un código de salida útil para scripts:"),
 ("table", ["Código", "Significado"], [
  ["0", "Sin cambios"],
  ["1", "Error"],
  ["2", "Hay cambios pendientes"],
 ]),
 ("code", "bash", "detectar drift cada noche", """terraform plan -detailed-exitcode -input=false > /dev/null
if [ $? -eq 2 ]; then
  echo "¡Hay drift en producción!"   # enviar alerta
fi"""),

 ("h", "Autenticación sin claves: OIDC"),
 ("p", "Para que GitHub Actions despliegue en AWS lo peor que puedes hacer es guardar access keys como secretos del repositorio (duran para siempre y se filtran). Lo correcto es **OIDC**: GitHub emite un token temporal en cada ejecución, AWS confía en GitHub y entrega credenciales que caducan en una hora."),
 ("p", "Se configura una vez en AWS (¡con Terraform, claro!):"),
 ("code", "hcl", "bootstrap/github-oidc.tf", """variable "repo_github" {
  description = "Repositorio autorizado, formato propietario/nombre"
  type        = string
  default     = "mi-usuario/terraform-labs"
}

resource "aws_iam_openid_connect_provider" "github" {
  url            = "https://token.actions.githubusercontent.com"
  client_id_list = ["sts.amazonaws.com"]
}

resource "aws_iam_role" "github_terraform" {
  name = "github-terraform"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Federated = aws_iam_openid_connect_provider.github.arn }
      Action    = "sts:AssumeRoleWithWebIdentity"
      Condition = {
        StringEquals = {
          "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
        }
        StringLike = {
          # solo este repositorio puede asumir el rol
          "token.actions.githubusercontent.com:sub" = "repo:${var.repo_github}:*"
        }
      }
    }]
  })
}

# Para el curso damos permisos amplios; en real, limita al mínimo necesario
resource "aws_iam_role_policy_attachment" "admin" {
  role       = aws_iam_role.github_terraform.name
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}

output "role_arn" {
  value = aws_iam_role.github_terraform.arn
}"""),
 ("warn", "La condición `sub` es crítica: sin ella, **cualquier repositorio de GitHub** podría asumir tu rol. Puedes restringirla aún más, por ejemplo a la rama main (`repo:usuario/repo:ref:refs/heads/main`) para el job de apply."),

 ("h", "Pipeline con GitHub Actions"),
 ("p", "Este workflow hace plan en cada Pull Request (y lo comenta en el PR) y apply al hacer merge en `main`:"),
 ("code", "yaml", ".github/workflows/terraform.yml", """name: terraform

on:
  pull_request:
    paths: ["envs/dev/**", "modules/**"]
  push:
    branches: [main]
    paths: ["envs/dev/**", "modules/**"]

permissions:
  id-token: write       # necesario para OIDC
  contents: read
  pull-requests: write  # para comentar el plan

env:
  TF_IN_AUTOMATION: "1"
  AWS_REGION: eu-west-1

jobs:
  terraform:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: envs/dev

    steps:
      - uses: actions/checkout@v4

      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: "1.10.5"

      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Formato
        run: terraform fmt -check -recursive

      - name: Init
        run: terraform init -input=false

      - name: Validate
        run: terraform validate

      - name: Plan
        id: plan
        run: |
          terraform plan -input=false -no-color -out=tfplan
          terraform show -no-color tfplan > plan.txt

      - name: Comentar plan en el PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const plan = fs.readFileSync('envs/dev/plan.txt', 'utf8');
            const body = '### Terraform plan (dev)\\n```\\n' + plan.slice(0, 60000) + '\\n```';
            await github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body
            });

      - name: Apply
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'
        run: terraform apply -input=false tfplan"""),
 ("ol", [
  "Guarda el ARN del rol (output `role_arn`) como secreto `AWS_ROLE_ARN` en *Settings → Secrets and variables → Actions*. No es un secreto en sentido estricto, pero así no lo repites.",
  "Abre un PR que cambie algo en `envs/dev`: verás el plan como comentario.",
  "Haz merge: el job aplica el cambio.",
 ]),
 ("tip", "Para producción, crea un **GitHub Environment** llamado `prod` con *required reviewers*. Añade `environment: prod` al job de apply y GitHub pedirá aprobación manual antes de ejecutarlo."),

 ("h", "Reglas de convivencia"),
 ("ul", [
  "**Una sola vía de despliegue**: si se aplica desde CI, nadie aplica desde su portátil (permisos de solo lectura para las personas).",
  "**Cambios pequeños**: un PR con un plan de 3 recursos se revisa bien; uno de 300, no.",
  "**Lee el plan en el PR**, no solo el código. Busca especialmente `destroy` y `-/+`.",
  "**Protege la rama `main`**: PR obligatorio, revisiones y checks en verde.",
  "**Fija versiones**: Terraform (`required_version`, `.terraform-version`), providers (lock file) y módulos.",
  "**Documenta**: README por entorno y por módulo (terraform-docs).",
 ]),

 ("h", "Políticas como código"),
 ("p", "En organizaciones grandes se añaden **políticas automáticas** que revisan cada plan: «no se permiten instancias mayores de xlarge», «todos los buckets deben estar cifrados», «el coste no puede subir más de 500 €». Las herramientas más usadas son **Sentinel** (HCP Terraform) y **OPA/Conftest** (open source), que evalúan el plan en JSON:"),
 ("code", "bash", "evaluar un plan con conftest", """terraform plan -out=tfplan
terraform show -json tfplan > plan.json
conftest test plan.json --policy politicas/"""),
]

TEST = [
 ("¿Por qué separar `envs/dev` y `envs/prod` en carpetas con estados distintos?",
  ["Por estética", "Para que un error en un entorno no afecte al otro y las diferencias sean explícitas", "Porque Terraform lo exige", "Para que sea más barato"], 1,
  "Cada entorno tiene su estado y su configuración visibles por separado."),
 ("¿Qué ventaja tiene `terraform apply tfplan` frente a `terraform apply`?",
  ["Es más rápido", "Aplica exactamente el plan revisado", "No necesita credenciales", "No modifica el estado"], 1,
  "Lo que se aprobó en el PR es lo que se ejecuta."),
 ("Con `-detailed-exitcode`, ¿qué código devuelve `plan` si hay cambios pendientes?",
  ["0", "1", "2", "3"], 2, "0 = sin cambios, 1 = error, 2 = cambios."),
 ("¿Qué aporta OIDC frente a guardar access keys de AWS en GitHub?",
  ["Nada", "Credenciales temporales sin secretos de larga duración", "Es más rápido", "Permite usar Azure"], 1,
  "No hay claves que puedan filtrarse; cada ejecución obtiene credenciales que caducan."),
 ("En la política de confianza del rol OIDC, ¿qué limita la condición sobre `sub`?",
  ["La región", "Qué repositorio (y rama) puede asumir el rol", "El tamaño de las instancias", "La versión de Terraform"], 1,
  "Sin ella, cualquier repositorio de GitHub podría asumir el rol."),
 ("¿Qué permiso necesita el workflow de GitHub Actions para usar OIDC?",
  ["contents: write", "id-token: write", "actions: write", "packages: read"], 1, "Permite solicitar el token OIDC a GitHub."),
]

RETOS = [
 {"titulo": "Tu primer pipeline",
  "enunciado": "En tu repositorio de prácticas, crea el rol OIDC, añade el workflow y abre un PR que cambie una etiqueta. Comprueba que aparece el plan como comentario y que al hacer merge se aplica.",
  "pista": "Si el job falla en `configure-aws-credentials`, revisa el permiso `id-token: write` y la condición `sub` (propietario/repositorio exactos, sensibles a mayúsculas).",
  "solucion": ("bash", """cd bootstrap
terraform apply -var="repo_github=TU_USUARIO/terraform-labs"
terraform output -raw role_arn     # cópialo al secreto AWS_ROLE_ARN

git switch -c prueba-pipeline
# cambia una etiqueta en envs/dev
git commit -am "chore: cambia etiqueta" && git push -u origin prueba-pipeline
# abre el PR en GitHub → ver comentario con el plan → merge""")},
 {"titulo": "Detector de drift programado",
  "enunciado": "Añade un segundo workflow que se ejecute todas las noches (`schedule`), haga `plan -detailed-exitcode` sobre `envs/dev` y falle (o abra un issue) si hay drift.",
  "pista": "`on: schedule: - cron: \"0 3 * * *\"`. Usa `continue-on-error` o captura el código de salida en bash.",
  "solucion": ("yaml", """name: drift
on:
  schedule:
    - cron: "0 3 * * *"
  workflow_dispatch: {}

permissions:
  id-token: write
  contents: read

jobs:
  drift:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: envs/dev
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
          aws-region: eu-west-1
      - run: terraform init -input=false
      - name: Plan
        run: |
          set +e
          terraform plan -input=false -detailed-exitcode
          code=$?
          if [ $code -eq 2 ]; then echo "::error::Drift detectado"; exit 1; fi
          exit $code""")},
]
