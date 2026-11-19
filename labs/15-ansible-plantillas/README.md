# Lab 15 · Variables y plantillas

```bash
cd labs/15-ansible-plantillas
ansible-playbook site.yml
cat /tmp/lab15/pagina.html
ansible-playbook site.yml -e "web_nombre=Luis"    # -e gana a group_vars
```

`group_vars/all.yml` está junto al playbook: Ansible también busca `group_vars` en esa carpeta.
