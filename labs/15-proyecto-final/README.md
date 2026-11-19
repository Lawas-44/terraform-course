# Lab 15 · Proyecto final: web escalable

Práctica del [módulo 15](../../modulos/15-proyecto-final.html).

```
modules/network   VPC, subredes públicas en 2-3 zonas, internet gateway
modules/web       ALB + Auto Scaling Group + security groups
envs/dev          Entorno dev (backend S3: cambia el nombre del bucket)
```

> **Importante:** el balanceador (ALB) no es gratuito. Despliega, prueba y destruye en la misma sesión.

```bash
cd envs/dev
terraform init
terraform apply
curl $(terraform output -raw url)
terraform destroy
```

Tests del módulo de red (con provider simulado, sin coste):

```bash
cd modules/network
terraform init
terraform test
```

Retos: crear `envs/prod`, añadir CI (lab 14), HTTPS, subredes privadas, autoescalado por CPU.
