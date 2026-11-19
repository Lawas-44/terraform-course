# Lab 12 · Importar recursos

Práctica del [módulo 12](../../modulos/12-import-refactor.html).

```bash
# Crear recursos «a mano»
CUENTA=$(aws sts get-caller-identity --query Account --output text)
aws s3api create-bucket --bucket legado-$CUENTA --region eu-west-1 \
  --create-bucket-configuration LocationConstraint=eu-west-1
aws ec2 create-security-group --group-name legado-sg --description "Creado a mano"
```

Sustituye los identificadores en `import.tf` y `main.tf`, y después:

```bash
terraform init
terraform plan      # debe decir: 2 to import, 0 to add, 0 to change
terraform apply
terraform destroy   # al terminar
```
