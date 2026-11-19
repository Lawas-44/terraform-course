# Laboratorios

Código de las prácticas del curso. Cada carpeta se ejecuta por separado:

```bash
cd labs/02-primer-proyecto
terraform init
terraform apply
terraform destroy
```

| Lab | Módulo | Nube | Coste |
|---|---|---|---|
| `02-primer-proyecto` | Primer proyecto | No | 0 € |
| `03-hcl` | Lenguaje HCL | No | 0 € |
| `04-variables` | Variables, outputs, locals (`terraform apply -var-file=prod.tfvars`) | No | 0 € |
| `05-s3-bucket` | Providers: bucket S3 | AWS | ~0 € |
| `06-servidor-web` | Recursos y dependencias: EC2 + nginx | AWS | capa gratuita |
| `07-meta-argumentos` | count, for_each, lifecycle | No | 0 € |
| `08-expresiones` | Expresiones y funciones (`terraform console`) | No | 0 € |
| `09-estado` | El estado, drift, moved | No | 0 € |
| `10-backend-s3` | `bootstrap/` (bucket del estado) + `proyecto/` (backend parcial y workspaces) | AWS | ~0 € |
| `11-modulos` | Módulos `static-site` y `etiquetas` (con tests) | AWS | ~0 € |
| `12-import` | Importar recursos creados a mano | AWS | ~0 € |
| `13-ansible-intro` | Inventario y comandos ad-hoc | No | 0 € |
| `14-ansible-playbooks` | Primer playbook | No | 0 € |
| `15-ansible-plantillas` | Variables, facts y plantillas Jinja2 | No | 0 € |
| `16-ansible-handlers` | Handlers, bucles y condiciones | No | 0 € |
| `17-ansible-roles` | Roles y colecciones | No | 0 € |
| `18-ansible-vault` | Ansible Vault y ansible-lint | No | 0 € |
| `20-calidad-testing` | `terraform test`, postconditions, TFLint, pre-commit | No | 0 € |
| `21-cicd` | Rol OIDC para GitHub Actions + workflow de ejemplo | AWS | 0 € |

Los labs de Ansible usan tu propia máquina como servidor (`ansible_connection=local`) y solo escriben en `/tmp`. Necesitas Linux, macOS o WSL.

El proyecto guiado completo (módulos 0 a 22) está en la carpeta [`proyecto/`](../proyecto/).

El workflow `.github/workflows/labs.yml` comprueba en cada push que los labs de Terraform pasan `fmt`, `validate` y `test`, que los de Ansible pasan `ansible-lint` y se ejecutan dos veces sin cambios, y que el playbook del proyecto funciona de verdad en una máquina Ubuntu.

Reglas:

- Los labs con nube terminan siempre con `terraform destroy`.
- Nunca se suben `*.tfstate`, `.terraform/` ni secretos.
