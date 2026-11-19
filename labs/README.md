# Laboratorios

Una carpeta por práctica, con el número del módulo como prefijo (`02-primer-proyecto`, `06-servidor-web`…).

Reglas:

- Cada lab debe poder ejecutarse con `terraform init && terraform apply` desde su carpeta.
- Los labs con recursos en la nube indican el coste estimado y terminan con `terraform destroy`.
- Nunca se suben `*.tfstate`, `.terraform/` ni `*.tfvars` con secretos (ver `.gitignore` en la raíz).
