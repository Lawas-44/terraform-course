locals {
  replicas = { dev = 1, prod = 3 }
}

resource "local_file" "config" {
  filename = "${path.module}/config-${terraform.workspace}.txt"
  content  = "replicas=${lookup(local.replicas, terraform.workspace, 1)}\n"
}
