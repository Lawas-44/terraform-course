# Lab 16 · Handlers, bucles y condiciones

En lugar de instalar nginx en tu máquina, el handler muestra un mensaje. Fíjate en cuándo aparece.

```bash
cd labs/16-ansible-handlers
ansible-playbook site.yml                      # el handler se ejecuta
ansible-playbook site.yml                      # sin cambios: el handler NO se ejecuta
ansible-playbook site.yml -e app_puerto=9090   # cambia la plantilla: el handler vuelve
ansible-playbook site.yml -e app_modo=produccion   # la tarea con when se salta
```
