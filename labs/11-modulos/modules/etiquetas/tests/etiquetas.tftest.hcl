variables {
  proyecto = "tienda"
  entorno  = "dev"
}

run "siempre_incluye_gestion" {
  command = plan

  assert {
    condition     = output.todas["Gestion"] == "terraform"
    error_message = "Falta la etiqueta Gestion"
  }
}

run "combina_extra" {
  command = plan

  variables {
    extra = { Equipo = "web" }
  }

  assert {
    condition     = output.todas["Equipo"] == "web" && output.todas["Proyecto"] == "tienda"
    error_message = "No se combinan las etiquetas extra"
  }
}

run "entorno_invalido" {
  command = plan

  variables {
    entorno = "qa"
  }

  expect_failures = [var.entorno]
}
