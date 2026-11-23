resource "aws_s3_bucket" "this" {
  bucket_prefix = "${var.nombre}-${var.entorno}-"
  force_destroy = true
  tags          = merge(var.etiquetas, { Entorno = var.entorno })
}

resource "aws_s3_bucket_website_configuration" "this" {
  bucket = aws_s3_bucket.this.id

  index_document {
    suffix = "index.html"
  }

  dynamic "error_document" {
    for_each = var.error_html == null ? [] : [1]
    content {
      key = "error.html"
    }
  }
}

# trivy:ignore:AVD-AWS-0086 trivy:ignore:AVD-AWS-0087 Web estática pública por diseño
resource "aws_s3_bucket_public_access_block" "this" {
  bucket                  = aws_s3_bucket.this.id
  block_public_acls       = true
  ignore_public_acls      = true
  block_public_policy     = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_policy" "lectura_publica" {
  bucket = aws_s3_bucket.this.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid       = "LecturaPublica"
      Effect    = "Allow"
      Principal = "*"
      Action    = "s3:GetObject"
      Resource  = "${aws_s3_bucket.this.arn}/*"
    }]
  })

  depends_on = [aws_s3_bucket_public_access_block.this]
}

resource "aws_s3_object" "index" {
  bucket       = aws_s3_bucket.this.id
  key          = "index.html"
  content      = var.index_html
  content_type = "text/html"
}

resource "aws_s3_object" "error" {
  count        = var.error_html == null ? 0 : 1
  bucket       = aws_s3_bucket.this.id
  key          = "error.html"
  content      = var.error_html
  content_type = "text/html"
}
