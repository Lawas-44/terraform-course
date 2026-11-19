# Lab 17 · Roles

```bash
cd labs/17-ansible-roles
ansible-playbook site.yml
ansible-playbook site.yml -e "miweb_carpeta=/tmp/otraweb"   # cambia un default
ansible-galaxy role init roles/otro                           # crea un rol nuevo
ansible-galaxy install -r requirements.yml                    # instala colecciones
```
