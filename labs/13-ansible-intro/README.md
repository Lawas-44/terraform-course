# Lab 13 · Primeros comandos con Ansible

Práctica del módulo 13. Usa tu propia máquina como servidor (`ansible_connection=local`), así que no cuesta nada.

```bash
cd labs/13-ansible-intro
ansible-inventory --graph
ansible local -m ping
ansible local -a "uptime"
ansible local -m setup -a "filter=ansible_distribution*"
```

Ansible lee `ansible.cfg` de la carpeta actual, por eso no hace falta `-i inventario.ini`.
