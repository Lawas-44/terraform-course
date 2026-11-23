# Test con provider simulado: no necesita credenciales ni crea nada en AWS.
mock_provider "aws" {}

variables {
  nombre  = "curso"
  entorno = "dev"
}

run "crea_bucket_con_prefijo" {
  command = apply

  assert {
    condition     = aws_s3_bucket.this.bucket_prefix == "curso-dev-"
    error_message = "Prefijo de bucket incorrecto"
  }

  assert {
    condition     = aws_s3_object.index.content_type == "text/html"
    error_message = "index.html debe servirse como text/html"
  }

  assert {
    condition     = length(aws_s3_object.error) == 0
    error_message = "Sin error_html no debe crearse error.html"
  }
}

run "con_pagina_de_error" {
  command = apply

  variables {
    error_html = "<h1>404</h1>"
  }

  assert {
    condition     = length(aws_s3_object.error) == 1
    error_message = "Con error_html debe crearse error.html"
  }
}
