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
| `13-testing` | `terraform test`, postconditions, TFLint, pre-commit | No | 0 € |
| `14-cicd` | Rol OIDC para GitHub Actions + workflow de ejemplo | AWS | 0 € |
| `15-proyecto-final` | VPC + ALB + Auto Scaling (con tests de red) | AWS | ALB ≈ 0,03 €/h |

El workflow `.github/workflows/labs.yml` comprueba en cada push que todos los labs pasan `terraform fmt`, `terraform validate` y `terraform test`.

Reglas:

- Los labs con nube terminan siempre con `terraform destroy`.
- Nunca se suben `*.tfstate`, `.terraform/` ni secretos.
