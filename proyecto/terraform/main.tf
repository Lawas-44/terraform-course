# Red propia: VPC con una subred pública (paso 11)
module "red" {
  source   = "./modules/red"
  nombre   = local.prefijo
  vpc_cidr = "10.0.0.0/16"
}

# Clave SSH para entrar en los servidores (paso 6)
resource "aws_key_pair" "this" {
  key_name   = "${local.prefijo}-clave"
  public_key = file(pathexpand(var.ruta_clave_publica))
}

# Servidores web (pasos 6, 7 y 11)
module "servidores" {
  source     = "./modules/servidores"
  nombre     = local.prefijo
  servidores = var.servidores
  vpc_id     = module.red.vpc_id
  subnet_id  = module.red.subnet_id
  clave_ssh  = aws_key_pair.this.key_name
  mi_ip      = var.mi_ip
}

# Inventario de Ansible generado automáticamente (paso 8)
resource "local_file" "inventario" {
  filename        = "${path.module}/../ansible/inventario/hosts.ini"
  file_permission = "0644"
  content = templatefile("${path.module}/templates/inventario.ini.tftpl", {
    servidores = module.servidores.ips
  })
}
