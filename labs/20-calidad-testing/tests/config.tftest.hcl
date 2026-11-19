variables {
  proyecto = "tienda"
}

run "prefijo_por_defecto" {
  command = plan

  assert {
    condition     = output.prefijo == "tienda-dev"
    error_message = "El prefijo por defecto debería ser tienda-dev"
  }
}

run "archivo_en_prod" {
  command = apply

  variables {
    entorno = "prod"
  }

  assert {
    condition     = local_file.config.filename == "./tienda-prod.conf"
    error_message = "Nombre de archivo incorrecto: ${local_file.config.filename}"
  }

  assert {
    condition     = strcontains(local_file.config.content, "entorno=prod")
    error_message = "El contenido no incluye el entorno"
  }
}

run "rechaza_nombres_cortos" {
  command = plan

  variables {
    proyecto = "ab"
  }

  expect_failures = [var.proyecto]
}
