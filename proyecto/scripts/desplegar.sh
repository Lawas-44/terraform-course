#!/usr/bin/env bash
# Crea la infraestructura con Terraform y la configura con Ansible (paso 19).
set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> 1/3 Creando la infraestructura con Terraform"
terraform -chdir=terraform apply -auto-approve

echo "==> 2/3 Esperando a que los servidores acepten SSH"
cd ansible
ansible web -m ansible.builtin.wait_for_connection -a "timeout=300"

echo "==> 3/3 Configurando los servidores con Ansible"
ansible-playbook site.yml --ask-vault-pass

echo
echo "Listo. Tu web está en:"
terraform -chdir=../terraform output urls
