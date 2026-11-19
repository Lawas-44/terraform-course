# -*- coding: utf-8 -*-
# Módulo 14 · Trabajo en equipo y CI/CD

LECCION = [
 ("h", "Organizar el repositorio"),
 ("p", "Cuando hay varios entornos (desarrollo, producción...), conviene separar los **módulos** (las piezas reutilizables) de los **entornos** (donde se usan):"),
 ("code", "text", "estructura recomendada", """infra/
├── modules/          # piezas reutilizables
│   ├── network/
│   └── web/
├── envs/
│   ├── dev/          # entorno de desarrollo (su propio estado)
│   │   ├── main.tf
│   │   └── terraform.tfvars
│   └── prod/         # entorno de producción (su propio estado)
│       ├── main.tf
│       └── terraform.tfvars
└── .github/workflows/terraform.yml"""),
 ("p", "Cada entorno tiene su propio estado. Así, un error en desarrollo nunca afecta a producción."),
 ("code", "hcl", "envs/prod/main.tf", """module "web" {
  source         = "../../modules/web"
  nombre         = "tienda-prod"
  tipo_instancia = "t3.medium"
}"""),

 ("h", "Trabajar en equipo"),
 ("p", "En un equipo nadie aplica cambios desde su ordenador. El proceso habitual es:"),
 ("ol", [
  "Creas una rama nueva en Git y haces tu cambio.",
  "Abres un **Pull Request** en GitHub.",
  "Un sistema automático ejecuta `terraform plan` y publica el resultado en el Pull Request.",
  "Un compañero revisa el código y el plan.",
  "Al aprobarlo y unirlo a `main`, el sistema automático ejecuta `terraform apply`.",
 ]),
 ("p", "Así todo cambio queda revisado y registrado, y nadie necesita las claves de producción en su ordenador."),

 ("h", "Guardar el plan y aplicar ese mismo plan"),
 ("p", "En los sistemas automáticos se guarda el plan en un archivo y luego se aplica exactamente ese plan:"),
 ("term", """$ terraform plan -out=tfplan
$ terraform show tfplan
$ terraform apply tfplan"""),
 ("p", "Así se aplica justo lo que se revisó, sin sorpresas."),
 ("p", "Otra opción útil es `-detailed-exitcode`. Hace que `plan` termine con un número que indica el resultado:"),
 ("table", ["Número", "Significado"], [
  ["0", "No hay cambios"],
  ["1", "Ha habido un error"],
  ["2", "Hay cambios pendientes"],
 ]),

 ("h", "Conectar GitHub con AWS sin guardar claves"),
 ("p", "GitHub Actions es el sistema automático de GitHub. Para que pueda crear cosas en AWS **no guardes tus claves de AWS en GitHub**. Usa **OIDC**: GitHub pide permiso a AWS en cada ejecución y recibe unas claves temporales que caducan en una hora."),
 ("p", "Se configura una vez en AWS:"),
 ("code", "hcl", "oidc.tf", """resource "aws_iam_openid_connect_provider" "github" {
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
          # Solo TU repositorio puede usar este permiso
          "token.actions.githubusercontent.com:sub" = "repo:mi-usuario/terraform-labs:*"
        }
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "admin" {
  role       = aws_iam_role.github_terraform.name
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}

output "role_arn" {
  value = aws_iam_role.github_terraform.arn
}"""),
 ("warn", "La línea con `sub` es muy importante: limita el permiso a tu repositorio. Sin ella, cualquier repositorio de GitHub podría usar tu cuenta de AWS."),

 ("h", "El flujo automático en GitHub Actions"),
 ("p", "Este archivo hace `plan` en cada Pull Request y `apply` al unir los cambios a `main`:"),
 ("code", "yaml", ".github/workflows/terraform.yml", """name: terraform

on:
  pull_request:
  push:
    branches: [main]

permissions:
  id-token: write    # necesario para OIDC
  contents: read

jobs:
  terraform:
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

      - run: terraform fmt -check -recursive
      - run: terraform init -input=false
      - run: terraform validate
      - run: terraform plan -input=false -out=tfplan

      - name: Apply
        if: github.ref == 'refs/heads/main' && github.event_name == 'push'
        run: terraform apply -input=false tfplan"""),
 ("ol", [
  "Copia el valor del output `role_arn`.",
  "En GitHub, ve a *Settings → Secrets and variables → Actions* y crea el secreto `AWS_ROLE_ARN` con ese valor.",
  "Abre un Pull Request: verás el plan en la pestaña *Actions*.",
 ]),

 ("h", "Normas para trabajar en equipo"),
 ("ul", [
  "**Un solo camino para aplicar cambios**: si se hace desde GitHub Actions, nadie lo hace desde su ordenador.",
  "**Cambios pequeños**: son más fáciles de revisar.",
  "**Lee el plan**, no solo el código. Fíjate sobre todo en lo que se va a borrar.",
  "**Protege la rama main**: que no se pueda cambiar sin Pull Request y revisión.",
 ]),
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
