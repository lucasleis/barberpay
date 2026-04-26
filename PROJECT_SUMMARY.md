# BarberPay — Resumen Técnico del Proyecto

## Qué es BarberPay

Sistema de gestión integral para peluquerías que digitaliza el cobro de servicios, la administración de barberos y el control de caja. Permite registrar turnos, cobrar con múltiples métodos de pago, calcular comisiones y generar cierres de caja diarios y semanales.

---

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Backend | Python / Flask + SQLAlchemy ORM |
| Base de datos | PostgreSQL (Docker) |
| Frontend (app) | Jinja2 templates + CSS custom |
| Frontend (landing) | React + Vite |
| Email | Flask-Mail |
| Infraestructura | Docker / docker-compose |

---

## Funcionalidades principales

- **Registro de pagos:** Cobro por servicio o producto con soporte de pago dividido entre múltiples métodos de pago simultáneos.
- **Gestión de barberos:** Alta de empleados con porcentaje de comisión configurable por barbero.
- **Liquidación de barberos:** Cálculo y registro de pagos a barberos por período con envío automático por email.
- **Membresías:** Sistema de membresías con usos disponibles y descuentos automáticos al momento del cobro.
- **Cierres de caja:** Reportes diarios, semanales y por rango de fechas con desglose por método de pago.
- **Métricas:** Visualización de ingresos, servicios más vendidos y rendimiento por barbero.

---

## Integraciones

- **MercadoPago:** SDK integrado para procesamiento de pagos digitales.
- **Flask-Mail:** Envío de resúmenes de liquidación a barberos por correo electrónico.

---

## Modelos de datos principales

| Modelo | Descripción |
|---|---|
| `Peluqueria` | Entidad central: nombre, dirección, teléfono |
| `Empleado` | Barberos con porcentaje de comisión |
| `Servicio` | Servicios ofrecidos con precios (común, amigo, descuento) |
| `Producto` | Inventario de productos con comisión por empleado |
| `Pago` | Pagos de turnos con soporte multi-método |
| `TipoMembresia` / `Membresia` | Tipos de membresía y membresías activas de clientes |
| `PagoBarbero` | Liquidaciones a barberos por período |
| `Appointment` | Turnos asignados a barbero y servicio |

---

## Tipo de usuarios

- **Administrador / Dueño:** Gestiona barberos, servicios, productos y membresías; consulta reportes financieros completos.
- **Operador / Cajero:** Registra pagos y cobra turnos en el día a día.
- **Clientes (landing pública):** Acceso informativo y checkout externo (flujo en desarrollo).

---

## Arquitectura general

Monolito Flask con separación en blueprints. La base de datos corre en Docker y la app se conecta vía variables de entorno. Existe una landing pública desacoplada en React/Vite que convive en el mismo repositorio.

```
barberpay/
├── app/
│   ├── models.py        # ORM models (SQLAlchemy)
│   ├── routes.py        # Endpoints y lógica de negocio
│   ├── auth.py          # Autenticación y sesiones
│   ├── templates/       # Jinja2 HTML templates
│   └── static/          # CSS y JS por módulo
├── landing_v1/          # Landing React/Vite
├── config_db.py         # Conexión directa a PostgreSQL
├── run.py               # Entry point
└── docker-compose.yml   # PostgreSQL en Docker
```

---

*Generado el 2026-04-26*
