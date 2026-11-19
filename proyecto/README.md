# Proyecto guiado: mi web en la nube

Código terminado del proyecto que se construye paso a paso en el curso. Úsalo para comparar con el tuyo.

Una web personal en dos servidores de AWS:

- **Terraform** crea una VPC, una subred pública, un firewall (SSH solo desde tu IP), una clave SSH y dos servidores Ubuntu 24.04. También genera el inventario de Ansible.
- **Ansible** configura los servidores con tres roles: `comun` (paquetes básicos), `nginx` (servidor web) y `web` (tu página, `/estado.html` y una zona `/privado/` con contraseña cifrada con Vault).

## Requisitos

- Terraform 1.10 o superior y Ansible (en Windows, dentro de WSL).
- Credenciales de AWS configuradas: `aws sts get-caller-identity`.
- Una clave SSH en `~/.ssh/id_ed25519.pub`.
- Un bucket para el estado (ver `labs/10-backend-s3/bootstrap`).

## Uso

```bash
cd proyecto
cp terraform/terraform.tfvars.example terraform/terraform.tfvars    # pon tu IP
cp terraform/backend.hcl.example terraform/backend.hcl              # pon tu bucket
cp ansible/inventario/group_vars/all/vault.yml.example ansible/inventario/group_vars/all/vault.yml
ansible-vault encrypt ansible/inventario/group_vars/all/vault.yml
terraform -chdir=terraform init -backend-config=backend.hcl
./scripts/desplegar.sh
```

Al terminar:

```bash
./scripts/destruir.sh
```

## Probar sin AWS

```bash
terraform -chdir=terraform init -backend=false
terraform -chdir=terraform test          # AWS simulado con mock_provider

cd ansible
ansible-lint
# Aplicar el playbook en tu propia máquina Ubuntu (instala nginx):
ansible-playbook -i inventario/local.ini site.yml -e web_privado_password=prueba
```

El workflow `.github/workflows/labs.yml` del repositorio del curso ejecuta todo esto en cada cambio.

## Coste

Los servidores `t3.micro` entran en la capa gratuita de AWS para cuentas nuevas. Destruye todo al terminar cada sesión.
