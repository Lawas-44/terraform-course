# 1. Crea los recursos a mano (ver README.md) y pon aquí sus identificadores.
# 2. Borra main.tf y ejecuta: terraform plan -generate-config-out=generado.tf
#    o usa main.tf como punto de partida ya limpio.

import {
  to = aws_s3_bucket.legado
  id = "legado-123456789012" # nombre de tu bucket
}

import {
  to = aws_security_group.legado
  id = "sg-0abc123def4567890" # ID de tu security group
}
