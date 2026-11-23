# Análisis y diseño del curso «Terraform y Ansible desde cero»

Documento de diseño: qué hay que enseñar, en qué orden, cómo y por qué. Sirve de guía para ir escribiendo las lecciones de la web.

---

## 1. Objetivo general

Que una persona **sin experiencia previa en Terraform ni en la nube** termine el curso siendo capaz de:

1. Describir infraestructura real (red, servidores, almacenamiento) en código HCL.
2. Gestionar su ciclo de vida completo de forma segura (`plan` → `apply` → `destroy`).
3. Trabajar en equipo: estado remoto, módulos reutilizables, revisiones por Pull Request y CI/CD.
4. Presentarse a la certificación **HashiCorp Certified: Terraform Associate** con garantías.

## 2. Público objetivo y prerrequisitos

| Perfil | Qué trae | Qué le falta |
|---|---|---|
| Estudiante / junior | Ganas, algo de informática | Terminal, Git, conceptos de red y cloud |
| Desarrollador/a | Git, lógica, editor | Redes, IAM, cómo funciona la nube |
| Sysadmin / soporte | Redes, servidores, scripts | Enfoque declarativo, Git, flujo de PRs |

**Prerrequisitos mínimos:** saber usar el ordenador con soltura y estar dispuesto a usar la terminal. Todo lo demás (terminal, Git, AWS básico) se cubre en el módulo 1 y en la [chuleta de comandos](../comandos.html).

**No se exige:** saber programar. HCL es un lenguaje de configuración.

## 3. Decisiones de diseño

| Decisión | Elección | Motivo |
|---|---|---|
| Herramientas | Terraform ≥ 1.10 y Ansible (ansible-core) | Estándar del mercado; 1.10 añade bloqueo nativo en S3 (`use_lockfile`). Se menciona OpenTofu en cada punto relevante. |
| Nube principal | AWS | Mayor cuota de mercado, capa gratuita y más ejemplos/ofertas de empleo. Los conceptos son trasladables a Azure/GCP. |
| Primeros pasos | Providers `local` y `random` | Cero coste y cero configuración: el alumno aprende el flujo sin miedo a la factura. |
| Idioma | Español, términos técnicos en inglés | Los mensajes de error y la documentación están en inglés; conviene reconocer los términos originales. |
| Formato | Web estática (GitHub Pages) + carpeta `labs/` | Sin dependencias, fácil de mantener y de contribuir. |
| Ritmo | 16 módulos, ~35 h | 2–4 h/semana → 2–3 meses. |

## 4. Metodología

Cada módulo sigue **la misma plantilla** (ya montada en las páginas de `modulos/`):

1. **Objetivos** medibles («serás capaz de…»).
2. **Contenido**: teoría breve, un concepto por apartado, con analogías.
3. **Ejemplo** de código comentado y copiable.
4. **Práctica guiada** paso a paso (lab).
5. **Comandos clave** del módulo.
6. **Errores frecuentes** y cómo resolverlos (aprender a leer errores es la mitad del trabajo).
7. **Test de autoevaluación** interactivo (6–10 preguntas con explicación) y **retos** con pista y solución.
8. Casilla «He completado este módulo» (progreso guardado en el navegador).

Principios:

- **Primero hacer, luego profundizar**: el alumno ejecuta `apply` en la primera hora (módulo 2).
- **Espiral**: conceptos como el estado aparecen pronto de forma superficial (módulo 2) y se profundizan después (módulos 9–10).
- **Romper cosas a propósito**: provocar drift, bloqueos, errores de validación… en un entorno seguro.
- **Coste cero o casi**: avisos de `destroy` en todos los labs con nube.

## 5. Mapa del temario

| # | Módulo | Nivel | Horas |
|---|---|---|---|
| 00 | Introducción a la Infraestructura como Código | Básico | 1 h |
| 01 | Preparación del entorno | Básico | 1,5 h |
| 02 | Tu primer proyecto: el flujo de trabajo | Básico | 1,5 h |
| 03 | El lenguaje HCL | Básico | 1,5 h |
| 04 | Variables, outputs y locals | Básico | 2 h |
| 05 | Providers y conexión con la nube | Básico | 1,5 h |
| 06 | Recursos, data sources y dependencias | Básico | 2,5 h |
| 07 | Meta-argumentos: count, for_each y lifecycle | Intermedio | 2 h |
| 08 | Expresiones y funciones | Intermedio | 2 h |
| 09 | El estado (state) en profundidad | Intermedio | 2 h |
| 10 | Backends remotos, bloqueo y workspaces | Intermedio | 2 h |
| 11 | Módulos | Intermedio | 3 h |
| 12 | Importar y refactorizar | Intermedio | 1,5 h |
| 13 | Introducción a Ansible | Básico | 1,5 h |
| 14 | Playbooks | Básico | 2 h |
| 15 | Variables, facts y plantillas | Básico | 2 h |
| 16 | Handlers, condiciones y bucles | Intermedio | 1,5 h |
| 17 | Roles y colecciones | Intermedio | 2 h |
| 18 | Ansible Vault y buenas prácticas | Intermedio | 1,5 h |
| 19 | Terraform y Ansible juntos | Intermedio | 2 h |
| 20 | Calidad, tests y seguridad | Avanzado | 2,5 h |
| 21 | Trabajo en equipo y CI/CD | Avanzado | 2,5 h |
| 22 | Proyecto final y siguientes pasos | Avanzado | 3 h |

Agrupación en partes (así aparece en la web):

- **Parte 1 · Primeros pasos** (00–01): qué es la IaC, qué hacen Terraform y Ansible, preparación del entorno.
- **Parte 2 · Terraform** (02–12): crear la infraestructura.
- **Parte 3 · Ansible** (13–18): configurar los servidores.
- **Parte 4 · Todo junto** (19–22): integración, calidad, CI/CD y proyecto final.

## 5 bis. Proyecto guiado

Para que el alumno vea un resultado real y no solo conocimientos, todo el curso construye un único proyecto: **una web personal en dos servidores de AWS**.

- Cada módulo (salvo el 12) termina con un **paso del proyecto**: código concreto que se añade al repositorio del alumno y un resultado comprobable.
- Pasos de Terraform (módulos 01–11): repositorio, variables, conexión con AWS, primer servidor, `for_each`, inventario generado, estado en S3, módulos y red propia.
- Pasos de Ansible (13–18): conexión, primer playbook con nginx (primer resultado visible en el navegador), plantillas con datos del alumno y facts, handlers, roles y zona privada con Vault.
- Pasos finales (19–22): despliegue con un comando, tests con AWS simulado, GitHub Actions y entrega.
- El código terminado está en `proyecto/` y se verifica en CI: tests de Terraform con `mock_provider`, `ansible-lint` y una ejecución real del playbook en una máquina Ubuntu de GitHub Actions comprobando la web, la página de estado, la zona privada y la idempotencia.
- Se usa Ubuntu en los servidores para que los roles (apt) se puedan probar igual en CI y en WSL.

## 6. Cobertura de la certificación Terraform Associate

Los dominios del examen (revisa siempre la versión vigente en la web de HashiCorp) se reparten así:

| Dominio | Módulos |
|---|---|
| Conceptos de IaC | 00 |
| Propósito de Terraform (vs otras herramientas, multi-cloud) | 00, 05 |
| Fundamentos (instalación, providers, versiones) | 01, 05 |
| Flujo de trabajo core (init, validate, plan, apply, destroy, fmt) | 02, 03 |
| Uso fuera del flujo core (import, state, logs, -replace) | 07, 09, 12 |
| Módulos | 11 |
| Configuración (variables, outputs, recursos, data, funciones, dependencias, validación) | 03, 04, 06, 07, 08, 13 |
| Estado (backends, bloqueo, drift) | 09, 10 |
| HCP Terraform | 10, 14 |

## 7. Costes y seguridad para el alumnado

- Módulos 0–4: **0 €** (sin nube).
- Módulos 5–14: recursos de la capa gratuita (S3, `t3.micro`/`t2.micro`, IAM, VPC). Coste esperado < 1 € si se destruye al terminar.
- Proyecto final: ALB y NAT Gateway **no son gratuitos** (cobran por hora). Avisar y limitar a sesiones cortas.
- Obligatorio antes del módulo 5: MFA en root, usuario no-root, **AWS Budgets** con alerta.
- Nunca: claves en el código, `.tfstate` en Git, `-auto-approve` fuera de CI.

## 8. Evaluación

- **Formativa**: autoevaluación al final de cada módulo y retos opcionales en los labs.
- **Sumativa**: proyecto final con rúbrica:

| Criterio | Peso |
|---|---|
| Funciona: despliega y destruye sin errores | 30 % |
| Organización: módulos, entornos, nombres | 20 % |
| Seguridad: sin secretos, mínimos privilegios, escáneres limpios | 20 % |
| Automatización: CI con fmt/validate/plan | 15 % |
| Documentación: README, diagrama, outputs | 15 % |

## 9. Estructura del repositorio

```
terraform-course/
├── index.html            # Portada + temario + progreso
├── comandos.html         # Chuleta con buscador
├── glosario.html
├── modulos/              # Una página por módulo (00–15)
├── labs/                 # Código de las prácticas, una carpeta por lab
├── assets/
│   ├── css/styles.css
│   ├── js/main.js        # Tema, copiar, progreso, buscador
│   └── img/
├── src/                  # Generador + contenido (lecciones, tests, retos)
└── docs/ANALISIS.md      # Este documento
```

## 10. Hoja de ruta de publicación

- [x] Estructura web, estilos y navegación.
- [x] Guion completo de los 16 módulos (objetivos, contenido, práctica, comandos, errores, quiz).
- [x] Chuleta de comandos y glosario.
- [x] Lab 02 de ejemplo.
- [x] Redactar la lección completa de cada módulo.
- [x] Test interactivo autocorregido y retos con solución en cada módulo.
- [x] Código de los labs en `labs/`.
- [x] CI del propio repositorio: `fmt`, `validate` y `test` sobre `labs/`.
- [ ] Añadir diagramas (arquitectura del lab 06 y del proyecto final).
- [ ] Banco de preguntas tipo test ampliado para la certificación (hay un simulacro de 10 en el módulo 15).

## 11. Ideas para ampliar

- Módulos extra: Azure y GCP, Kubernetes (EKS + provider `kubernetes`/`helm`), Terragrunt, OpenTofu en profundidad, CDK for Terraform.
- Vídeos cortos por módulo o GIFs de la terminal (asciinema).
- Ejercicios de «encuentra el error» con código roto.
- Entorno sin instalación con GitHub Codespaces (`.devcontainer/` con Terraform y AWS CLI preinstalados).
