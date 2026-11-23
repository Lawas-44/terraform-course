# Lab 18 · Ansible Vault y ansible-lint

```bash
cd labs/18-ansible-vault
ansible-vault encrypt secretos.yml      # elige una contraseña
cat secretos.yml                        # ilegible
ansible-playbook site.yml --ask-vault-pass
ansible-lint
```

En el repositorio `secretos.yml` está sin cifrar para que puedas practicar. En tus proyectos, súbelo siempre cifrado.
