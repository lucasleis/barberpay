# CODEBASE_OVERVIEW.md

> Auto-generated documentation — describes what the application **does**, not just what files exist.

---

## 1. Project Summary

BarberPay is a web-based payment and operations management system built for barbershops. It lets barbershop staff register client payments for services, products, and membership plans in real time; calculates the revenue split between the shop owner and each barber; produces period-closing reports; and manages payroll for barbers. A secondary public-facing landing page promotes the barbershop (Barba&Co) to clients.

**Tech stack**

| Layer | Technology |
|---|---|
| Backend framework | Python / Flask |
| ORM | Flask-SQLAlchemy (SQLAlchemy) |
| Database | PostgreSQL 14 |
| Auth | Session-based (Flask sessions) with password hashing via Werkzeug |
| Email | Flask-Mail (SMTP, configured for Gmail) |
| CSRF protection | Flask-WTF / WTF CSRF |
| CORS | Flask-CORS |
| Containerization | Docker + Docker Compose |
| Frontend (admin app) | Server-side Jinja2 templates + Bootstrap 5 + vanilla JS |
| Frontend (landing v1) | React 18 + TypeScript + Tailwind CSS (Vite SPA, served from Flask) |
| Landing v2 | Jinja2 template |
| Timezone | `zoneinfo` (America/Argentina/Buenos_Aires) |
| Key Python libraries | psycopg2-binary, python-dateutil, mercadopago (imported but not wired in production routes) |

---

## 2. Application Structure Overview

The repository has two sub-systems that share the same Flask process:

```
barberpay/
├── app/                     # Flask application package
│   ├── __init__.py          # App factory, DB bootstrap, extensions init
│   ├── models.py            # SQLAlchemy models (all tables)
│   ├── routes.py            # All routes and business logic (~2600 lines)
│   ├── auth.py              # login_required decorator (secondary, partially superseded)
│   ├── static/              # CSS files, logo images, utils.js
│   └── templates/           # Jinja2 HTML templates for every page
├── landing_v1/              # React/TypeScript SPA (public barbershop landing)
├── run.py                   # Entrypoint — calls create_app()
├── docker-compose.yml       # Postgres + Flask containers
└── .env.example             # Environment variable reference
```

### Main modules

| Module | What it does |
|---|---|
| **Payment registration** (`/payments/new`) | Core daily workflow: register a client visit with barber, service, products, membership use or purchase, payment method(s), and optional tip |
| **Period closing / Cierres** (`/cierres/<salon_id>`) | Date-range report showing all payments, totals per barber, totals per payment method, and owner profit |
| **Barber payroll** (`/barbers_payment`) | Record and track what has been paid to each barber for a period; auto-calculates the owed amount; sends email receipts |
| **Admin catalog** | CRUD for barbers, services, products, payment methods, membership types, users |
| **Memberships** | Prepaid-use plans: create a client membership, sell it during checkout, and consume uses at each visit |
| **Metrics** (`/admin/metricas`) | 30-day dashboard with peak hours, most-sold services, most-sold products, memberships sold |
| **Public landing** (`/`) | Static promotional page for the barbershop |
| **Landing v1** (`/landings/v1/`) | React SPA: full promotional single-page site for Barba&Co |
| **Landing v2** (`/landings/v2`) | Alternative Jinja2 promotional page |

### User roles

| Role | What they can do |
|---|---|
| **admin** | Full access: all catalog management, cierres, barber payroll, metrics, payment editing/deletion, user management, dashboard |
| **barber** (non-admin) | Can register payments (`/payments/new`) and view cierres, but **cannot** see owner totals in cierres reports, and cannot edit payments |

Both roles are stored in the `usuario.rol` column. Role is checked at the route level and also filters data returned by the `/pagos_entre_fechas` API endpoint.

---

## 3. Pages & Screens

### `/login` — Login page
- Shows a username/password form.
- On successful authentication: sets `session['user']`, `session['salon_id']`, `session['rol']`.
- Admins are redirected to `/dashboard`; non-admins to `/payments/new`.
- No authentication required to view the form.

### `/dashboard` — Admin dashboard
- Shows the logged-in username and links to all admin sections.
- **Requires authentication and admin role.**

### `/payments/new` — Register a payment (main daily screen)
- **Requires authentication (any role).**
- Displays today's existing payments in a table (barber, service/product, amount, payment method).
- Lets the operator record a new payment by selecting:
  - Barber
  - One or more of: Service, Product(s), Membership sale
  - Pricing tier for services: standard (`comun`), friend/voucher (`amigo`), or discount (`descuento`)
  - Whether to apply an existing membership (consumes 1 use) instead of charging the service
  - Payment method (single or split across two methods)
  - Optional tip
- Shows the current stock for each product; prevents over-selling.
- On success: creates an `Appointment` record linked to a `Pago` (and possibly `AppointmentTurno` rows for products).

### `/cierres/<salon_id>` — Period closing report
- **Requires authentication.**
- Shows a date-range picker defaulting to the current Sunday-to-Sunday week.
- On date selection, calls `/pagos_entre_fechas` (AJAX POST) to fetch and display:
  - A payment-by-payment table (barber, service/product/membership, payment methods, amounts, employee and owner shares)
  - Totals per barber (amount earned, number of services, products sold)
  - Totals per payment method
  - Total revenue and owner profit (hidden from non-admin users)
- Admins can open an edit modal for service payments or membership payments to correct mistakes.
- Any authenticated user can delete payments from this view (with side-effects: stock restored, membership uses reversed).

### `/barbers_payment` — Barber payroll
- **Requires authentication.**
- Shows a form to record a payout to a barber:
  - Select barber and date range
  - System auto-fetches the owed amount via `/api/calcular_monto_barbero` (the barber's commission percentage applied to all payments in the period)
  - Optionally apply a discount (with required justification) or add extra (with required justification)
  - Specify split between bank transfer and cash
- Shows a history table of all past barber payments.
- Each past payment has a "send receipt" button that emails the barber their pay slip via SMTP.

### `/admin/barbers` — Employee management
- **Requires authentication.**
- Lists all active barbers with their commission percentage and email.
- Allows adding new barbers (name, commission %, email), editing (inline modal), and soft-deleting (sets `active=False`).

### `/admin/services` — Service catalog
- **Requires authentication.**
- Lists active services with standard price, friend price, and discount price.
- Adding/editing a service creates a new record and soft-deletes the old one (preserves historical payment references).

### `/admin/products` — Product catalog
- **Requires authentication.**
- Lists products with name, price, stock quantity, and employee commission %.
- Allows adding, editing (name, price, quantity, commission), and soft-deleting products.
- Employee commission for products is constrained between 1% and 100%.

### `/admin/payment_methods` — Payment method catalog
- **Requires authentication.**
- Lists active payment methods (e.g., cash, card, Mercado Pago).
- Allows adding, editing name, and soft-deleting.

### `/admin/memberships` — Membership type and client membership management
- **Requires authentication.**
- Two sections:
  1. **Membership types** (plans): name, price, number of uses, and the linked service. Allows create, edit, soft-delete.
  2. **Client memberships**: lists all active memberships with client identifier (DNI or legacy numeric ID) and remaining uses. Allows manual adjustment of ID and use count.

### `/admin/metricas` — Analytics
- **Requires authentication.**
- Displays bar charts (text-based, CSS-styled) for the last 30 days:
  - Peak hours by 30-minute slot (based on appointment timestamps)
  - Most-sold services (broken down by pricing tier: common / friend / discount / membership)
  - Most-sold products (by unit quantity)
  - Most-sold membership plans (by purchase count)

### `/admin/users` — User management
- **Requires authentication.**
- Lists all users belonging to the current salon.
- Allows adding users (username, password, role, email), changing passwords, updating email, and deleting users.

### `/` — Public landing page (Jinja2)
- No authentication required.
- A simple promotional page for the barbershop: hero text, "book a turn" link, three feature highlights.

### `/landings/v1/` — React SPA landing page
- No authentication required.
- Full single-page promotional site for Barba&Co (Avellaneda, Buenos Aires):
  - Hero section with logo and "Book a Turn" button (links to Fresha booking platform)
  - Services section (hardcoded: Haircut, Haircut+Beard, Beard Trim, Eyebrow Shaping)
  - Membership explanation (3-step how-it-works)
  - Payment methods section (Cash, Cards, Mercado Pago)
  - Location section with embedded Google Maps iframe
  - Contact section (Instagram and WhatsApp links)
  - Online booking section (Fresha link)
- Built with React 18 + Tailwind CSS. Served as a static build from Flask via `send_from_directory`.

### `/landings/v2` — Alternative landing (Jinja2)
- No authentication required.
- Unclear — file exists at `templates/landing_v2/home.html` but content was not inspected in detail; appears to be a promotional page template.

### `/turnos` — Appointment redirect
- No authentication required.
- Immediately redirects the browser to the Fresha online booking page for Barba&Co.

---

## 4. Core Features

### Payment Registration

The central workflow: when a client is served, staff open `/payments/new` and fill in the form. The system:
1. Creates an `Appointment` record (barber, service/product/membership references, pricing tier).
2. If products are included, creates `AppointmentTurno` rows and decrements stock.
3. If a membership is being **used** (not purchased), decrements `Membresia.usos_disponibles` by 1.
4. If a membership is being **purchased**, creates or recharges a `Membresia` row linked by client DNI or auto-assigned numeric ID.
5. Creates a `Pago` record with up to two payment methods, amounts, and optional tip.
6. Validates that the total paid equals the total owed (within 1-peso tolerance).

### Period Closing (Cierres)

For any date range, the `/pagos_entre_fechas` endpoint:
- Loads all `Pago` records in the range for the current salon.
- For each payment, determines: type (service / product / membership sale / membership use), employee commission, owner share.
- Aggregates totals per barber (services count, products count, tips, money earned) and per payment method.
- Applies special logic for the "amigo" pricing tier: the barber's commission is subtracted from the owner's total (it's treated as a cost to the owner, not revenue).
- For discount pricing: owner receives only the margin above the discounted amount.
- Non-admin users receive results with owner profit and grand total stripped out.

### Barber Commission Calculation

Each `Empleado` has a `porcentaje` (integer). For each payment:
- Services: `service.precio × barber.porcentaje / 100` → barber's share
- Products: `product.precio × product.comision_empleado / 100` per item
- Membership uses: uses the linked service's standard price as the base, applies barber %
- Membership purchases: 100% goes to the owner (barber gets 0%)
- Tips: 100% go to the barber

### Barber Payroll

The `/barbers_payment` workflow:
1. User picks a barber and date range.
2. A JS call to `/api/calcular_monto_barbero` returns the owed amount (same commission logic as cierres).
3. User can enter a discount amount (with mandatory written justification) and/or an extra amount (also requiring justification).
4. Final amount = base − discount + extra.
5. User specifies how much is paid by bank transfer and how much in cash (must sum to final amount).
6. Prevents duplicate payroll entries for the same barber and date range (returns HTTP 409).
7. On save, optionally triggers email delivery of a payment receipt.

### Membership System

- **Membership types** (`TipoMembresia`): define name, price, number of uses, and which service they cover.
- **Client memberships** (`Membresia`): a client is identified either by DNI (new system) or a legacy numeric ID (`id_usuario`). Each record holds the count of remaining uses.
- When purchasing: if the client already has an active membership of the same type (matched by DNI), the uses are added to the existing record rather than creating a new one.
- When using: membership ID or DNI is entered at checkout; the system validates there are available uses, decrements by 1, and records the `membresia_id` on the appointment.
- Payment deletion reverses membership changes: if the deleted payment was a purchase, the membership is deleted (or uses reversed); if it was a use, 1 use is restored.

### Email Receipts

After saving a barber payment, staff can click "Send Receipt" which calls `/api/enviar_recibo_pago/<id>`. The system:
- Renders `templates/emails/recibo_pago.html` with the payment breakdown.
- Sends it to the barber's email address via Flask-Mail (SMTP).
- BCC's all admin users who have an email configured.
- Falls back to finding an active barber by the same name if the stored barber record lacks an email.

### Availability API (Scheduling, partially implemented)

`/availability/<barber_id>/day` returns a JSON list of free 30-minute slots for a barber on a given date, based on existing `TurnoCliente` records. Working hours are hardcoded to 11:00–20:00.

---

## 5. API Routes & Server Actions

### Authentication

| Route | Method | What it does |
|---|---|---|
| `/login` | GET | Renders login form |
| `/login` | POST | Validates username/password, sets session, redirects by role |
| `/logout` | GET | Clears session, redirects to login |

### Dashboard

| Route | Method | What it does |
|---|---|---|
| `/dashboard` | GET | Admin-only landing page with navigation links |

### Payments

| Route | Method | What it does |
|---|---|---|
| `/payments/new` | GET | Renders payment form with today's payments, active barbers/services/products/memberships |
| `/payments/new` | POST | Validates and creates Appointment + Pago (and optionally AppointmentTurno, Membresia records). Validates totals to within $0.01. |
| `/payments/delete/<pago_id>` | POST | Deletes a payment and its appointment. Restores product stock. Reverses membership use/purchase. |
| `/pagos/editar/<pago_id>` | POST | Admin only. Edits date, barber, service, payment method, amounts for a **service** payment. Validates amounts match service price. Cannot edit payments with products or memberships. |
| `/pagos/editar_membresia/<pago_id>` | POST | Admin only. Edits date, barber, payment method, amounts for a **membership** payment. Updates linked membership type. |
| `/pagos_entre_fechas` | POST (JSON) | Returns all payments in a date range with per-barber and per-payment-method aggregations. Strips owner totals for non-admin callers. |

### Barber Payroll

| Route | Method | What it does |
|---|---|---|
| `/barbers_payment` | GET | Renders payroll page with barber list and payment history |
| `/barbers_payment/save` | POST (JSON) | Creates a new `PagoBarbero`. Validates: non-negative amounts, base−discount+extra=final, transfer+cash=final, justifications required when discount/extra > 0, no duplicate period for same barber. Returns 409 on duplicate. |
| `/barbers_payment/<payment_id>` | GET | Returns JSON of a single barber payment record |
| `/barbers_payment/<payment_id>` | PUT (JSON) | Updates an existing barber payment with same validations as save |
| `/barbers_payment/<payment_id>` | DELETE | Deletes a barber payment record |
| `/api/calcular_monto_barbero` | GET | Query params: `barbero_id`, `fecha_inicio`, `fecha_fin`. Returns `{"monto_total": float}` — the commission owed to the barber in the period. |
| `/api/enviar_recibo_pago/<pago_id>` | POST | Sends an HTML email receipt to the barber. Returns 422 if no email is configured. |

### Employee (Barber) Management

| Route | Method | What it does |
|---|---|---|
| `/barbers` | GET | JSON list of all active barbers (public, used by frontend) |
| `/admin/barbers` | GET | HTML list of active barbers for the current salon |
| `/admin/barbers/add` | POST | Creates a new barber. Validates email format (regex + max 254 chars). |
| `/admin/barbers/delete/<id>` | GET | Soft-deletes barber (sets `active=False`) |
| `/admin/barbers/update/<id>` | POST | Updates name, commission %, and email with email validation |

### Service Management

| Route | Method | What it does |
|---|---|---|
| `/services` | GET | JSON list of all active services |
| `/admin/services` | GET | HTML list of active services for the current salon |
| `/admin/services/add` | POST | Creates a new service with name, price, and optional discount price |
| `/admin/services/delete/<id>` | GET | Soft-deletes service |
| `/update_service/<id>` | POST | Soft-deletes the existing service and creates a new one with updated values. Preserves foreign key references in historical data. |

### Product Management

| Route | Method | What it does |
|---|---|---|
| `/admin/products` | GET | HTML list of active products |
| `/admin/products/add` | POST | Creates product with name, price, stock quantity, employee commission %. Validates commission 1–100. |
| `/admin/products/update_quantity/<id>` | POST | Updates name, price, quantity, and commission for a product |
| `/admin/products/delete/<id>` | GET | Soft-deletes product |

### Payment Method Management

| Route | Method | What it does |
|---|---|---|
| `/admin/payment_methods` | GET | HTML list of active payment methods |
| `/admin/payment_methods/add` | POST | Creates a named payment method |
| `/admin/payment_methods/delete/<id>` | GET | Soft-deletes payment method |
| `/admin/payment_methods/update/<id>` | POST | Renames a payment method |

### Membership Management

| Route | Method | What it does |
|---|---|---|
| `/admin/memberships` | GET | HTML page with membership types and active client memberships |
| `/admin/memberships/add` | POST | Creates a new `TipoMembresia` (plan) |
| `/admin/memberships/delete/<id>` | GET | Hard-deletes a membership type |
| `/update_membership_type/<id>` | POST | Soft-deletes old type and creates new one with updated values |
| `/admin/memberships/update/<membresia_id>` | POST | Updates a client membership's ID/DNI and remaining use count |
| `/membresias/incrementar/<id>` | POST | Adds 1 use to a client membership |
| `/membresias/decrementar/<id>` | POST | Removes 1 use from a client membership (fails with 400 if none left) |

### User Management

| Route | Method | What it does |
|---|---|---|
| `/admin/users` | GET | HTML list of users for the current salon |
| `/admin/users/add` | POST | Creates a user with username, hashed password, role, salon_id, and optional email |
| `/admin/users/delete/<id>` | GET | Hard-deletes a user |
| `/admin/users/update/<id>` | POST | Changes a user's password (hashed) |
| `/admin/users/update_email/<id>` | POST | Changes a user's email with validation |

### Metrics

| Route | Method | What it does |
|---|---|---|
| `/admin/metricas` | GET | Renders metrics page with last-30-day data for services, products, memberships sold, and peak hours |

### Scheduling (Client Appointments — partially implemented)

| Route | Method | What it does |
|---|---|---|
| `/availability/<barber_id>/day` | GET | Returns available 30-min slots for a barber on a given date (`?fecha=YYYY-MM-DD`). Works from 11:00–20:00 |
| `/clientes/<client_dni>` | GET | Returns client JSON by DNI |
| `/clientes` | POST | Creates a new client (name, surname, DNI, email, phone). DNI must be unique per salon. CSRF exempt. |

### Landing / Public pages

| Route | Method | What it does |
|---|---|---|
| `/` | GET | Renders public_landing.html (generic barbershop promo page) |
| `/app` | GET | Renders index.html |
| `/turnos` | GET | Redirects to the Fresha booking page |
| `/landings/v2` | GET | Renders the v2 Jinja2 landing page |
| `/landings/v1/` | GET | Serves the built React SPA (index.html) |
| `/landings/v1/<path>` | GET | Serves static assets for the React SPA |

---

## 6. Data Models

### `peluquerias` — Barbershop / Salon
Represents a single barbershop location. All other entities belong to a salon via `peluqueria_id`.

| Field | Description |
|---|---|
| `id` | Primary key |
| `nombre` | Salon name |
| `direccion` | Address (text) |
| `telefono` | Phone number |

The app bootstrap inserts a default salon with `id=1` named "Peluquería Central" if none exists.

### `barberos` — Employees (Barbers)
| Field | Description |
|---|---|
| `id` | Primary key |
| `name` | Employee name |
| `active` | Soft-delete flag |
| `porcentaje` | Commission percentage (integer, 0–100) applied to services |
| `email` | Email address for payroll receipts |
| `peluqueria_id` | FK → `peluquerias` |

### `metodos_pago` — Payment Methods
| Field | Description |
|---|---|
| `id` | Primary key |
| `nombre` | Name (e.g., "Efectivo", "Tarjeta") — unique |
| `active` | Soft-delete flag |
| `peluqueria_id` | FK → `peluquerias` |

### `servicios` — Services
| Field | Description |
|---|---|
| `id` | Primary key |
| `name` | Service name |
| `active` | Soft-delete flag |
| `precio` | Standard price |
| `precio_amigo` | "Friend" price (used for voucher/friend pricing tier) |
| `precio_descuento` | Discounted price |
| `peluqueria_id` | FK → `peluquerias` |

Note: updating a service creates a new record and soft-deletes the old one, preserving FK integrity on historical payments.

### `productos` — Products (retail items sold alongside services)
| Field | Description |
|---|---|
| `id` | Primary key |
| `name` | Product name |
| `precio` | Unit price |
| `cantidad` | Stock quantity |
| `comision_empleado` | Employee commission % for selling this product (1–100) |
| `active` | Soft-delete flag |
| `peluqueria_id` | FK → `peluquerias` |

### `tipos_membresia` — Membership Plans
| Field | Description |
|---|---|
| `id` | Primary key |
| `nombre` | Plan name |
| `precio` | Total plan price |
| `usos` | Number of service uses included |
| `active` | Soft-delete flag |
| `servicio_id` | FK → `servicios` — which service the plan covers |
| `peluqueria_id` | FK → `peluquerias` |

### `membresias` — Client Memberships (instances)
| Field | Description |
|---|---|
| `id` | Primary key |
| `id_usuario` | Legacy numeric client identifier (unique per salon, nullable) |
| `dni` | Client national ID number (unique per salon, nullable) |
| `tipo_membresia_id` | FK → `tipos_membresia` |
| `usos_disponibles` | Remaining service uses |
| `fecha_compra` | Purchase timestamp |
| `active` | Whether membership is active |
| `peluqueria_id` | FK → `peluquerias` |

A membership is identified by either `dni` or `id_usuario`. There is a unique constraint on `(dni, peluqueria_id)`.

### `turnos` — Appointments
Created for every client visit. Each appointment is linked to exactly one payment.

| Field | Description |
|---|---|
| `id` | Primary key |
| `date` | Visit timestamp (Buenos Aires timezone) |
| `barber_id` | FK → `barberos` |
| `service_id` | FK → `servicios` (nullable if only products/membership) |
| `membresia_id` | FK → `membresias` (set when an existing membership is used) |
| `peluqueria_id` | FK → `peluquerias` |
| `tipo_precio_servicio` | Pricing tier: `comun`, `amigo`, or `descuento` |

### `productos_turno` — Products in an Appointment
Junction table between an appointment and the products sold in that visit.

| Field | Description |
|---|---|
| `id` | Primary key |
| `turno_id` | FK → `turnos` (cascade delete) |
| `producto_id` | FK → `productos` |
| `cantidad` | Units sold |
| `precio_unitario` | Price at time of sale (snapshot) |

### `pagos` — Payments
One record per client visit. Always linked to an appointment.

| Field | Description |
|---|---|
| `id` | Primary key |
| `appointment_id` | FK → `turnos` |
| `membresia_comprada_id` | FK → `membresias` — set when a membership was *purchased* in this payment |
| `payment_method1_id` | FK → `metodos_pago` (required) |
| `payment_method2_id` | FK → `metodos_pago` (optional, for split payments) |
| `amount_method1` | Amount paid via method 1 |
| `amount_method2` | Amount paid via method 2 (0 if unused) |
| `amount_tip` | Tip amount (goes entirely to the barber) |
| `date` | Payment timestamp |
| `peluqueria_id` | FK → `peluquerias` |

### `usuario` — App Users
| Field | Description |
|---|---|
| `id` | Primary key |
| `username` | Unique username |
| `password` | Werkzeug-hashed password |
| `salon_id` | Which salon this user belongs to |
| `rol` | Role: `admin` or `barber` |
| `email` | Optional email (used for BCC on payroll receipts) |

### `clientes` — Clients (scheduling module)
| Field | Description |
|---|---|
| `id` | Primary key |
| `nombre`, `apellido` | Name and surname |
| `email`, `telefono` | Contact details |
| `dni` | National ID |
| `peluqueria_id` | FK → `peluquerias` |
| `created_at` | Registration timestamp |

### `turnos_clientes` — Scheduled Appointments (scheduling module)
| Field | Description |
|---|---|
| `id` | Primary key |
| `cliente_id` | FK → `clientes` |
| `barber_id` | FK → `barberos` |
| `service_id` | FK → `servicios` |
| `peluqueria_id` | FK → `peluquerias` |
| `fecha` | Date of appointment |
| `hora_inicio` | Start time |
| `duracion_minutos` | Duration in minutes |
| `hora_fin` | Computed column (PostgreSQL Generated Column: `hora_inicio + duracion_minutos minutes`) |
| `estado` | Status: `pendiente`, `confirmado`, or `cancelado` |
| `notas` | Free-text notes |
| `precio_aplicado` | Applied price |

### `pagos_barberos` — Barber Payroll Records
| Field | Description |
|---|---|
| `id` | Primary key |
| `peluqueria_id` | FK → `peluquerias` |
| `barber_id` | FK → `barberos` |
| `fecha_inicio_periodo` / `fecha_fin_periodo` | Pay period dates |
| `fecha_pago` | Timestamp when payment was recorded |
| `monto_periodo` | Commission earned in the period |
| `monto_descuento` | Deduction amount |
| `justificacion_descuento` | Written reason for deduction (required if > 0) |
| `monto_agregado` | Extra addition |
| `justificacion_agregado` | Written reason for addition (required if > 0) |
| `monto_final` | Final amount = period − discount + extra |
| `metodo_transferencia` | Amount paid by bank transfer |
| `metodo_efectivo` | Amount paid in cash |

---

## 7. Authentication & Roles

**Login mechanism:** Standard Flask session-based authentication. On POST to `/login`, the system looks up the `Usuario` record by username and calls `werkzeug.security.check_password_hash` to verify the password. On success, `session['user']`, `session['salon_id']`, and `session['rol']` are set. Sessions are permanent with a 12-hour lifetime.

**Protection:** Routes are protected by an inline `login_required` decorator defined in `routes.py` (the one in `auth.py` is a legacy version that checks a different session key and is not used by current routes). This decorator checks `'user' in session` and redirects to `/login` with the original URL as the `next` query parameter if not authenticated.

**Role enforcement:**
- The `/dashboard` route checks `session.get('rol') == 'admin'` and redirects non-admins away.
- Payment edit routes (`/pagos/editar/`, `/pagos/editar_membresia/`) check for admin role and redirect with a flash error if not admin.
- `/pagos_entre_fechas` strips `propietario_total` and `monto_total` from the response for non-admin users.

**Cookie security:** Sessions are configured with `SESSION_COOKIE_SECURE=True`, `SESSION_COOKIE_HTTPONLY=True`, and `SESSION_COOKIE_SAMESITE='Lax'`. CSRF tokens are generated via Flask-WTF and injected into every template via a context processor.

**Multi-salon isolation:** Every query for sensitive data is filtered by `salon_id = session.get('salon_id')`. A user can only see and manage data for their own salon.

---

## 8. External Services & Integrations

### Flask-Mail / SMTP (Gmail)
- **What:** Sends HTML email receipts to barbers after a payroll entry is saved.
- **Triggered by:** `POST /api/enviar_recibo_pago/<pago_id>`
- **Template:** `templates/emails/recibo_pago.html` — a polished HTML email with payment breakdown table, discount/addition details, payment methods, and footer branding.
- **Configuration:** `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD` from environment variables. Supports both STARTTLS (port 587) and SSL (port 465).

### Fresha (Online Appointment Booking)
- **What:** External third-party booking platform used by Barba&Co for client appointment scheduling.
- **Triggered by:** The "Reserve Turn" button in the React landing page (`/landings/v1/`), the `/turnos` redirect route, and the booking section of the landing. All link out to a hardcoded Fresha URL for Barba&Co.
- **No API integration** — it is only an external hyperlink.

### Google Maps (Embed)
- **What:** An embedded `<iframe>` showing the barbershop's location.
- **Where:** The React SPA landing page (`/landings/v1/`) location section. Static embed URL, no API key required.

### Mercado Pago (SDK imported, not active in production routes)
- **What:** The `mercadopago` Python package is listed in `requirements.txt` and the app factory has a commented-out `mp_test` blueprint import. No active payment processing routes exist in the current codebase.
- **Status:** Unclear — the integration appears to be stubbed out or removed; the routes are not registered.

### Font Awesome (CDN)
- **What:** Icon library loaded via CDN in several admin templates (barbers, memberships, cierres, barbers_payment). Used for edit (pen) and delete (trash) icons.

### Bootstrap 5 (CDN)
- **What:** CSS framework loaded via CDN in the main layout template. Used across all admin pages.

### Google Fonts (CDN)
- **What:** Loads the "Azeret Mono" font used for the brand logo text fallback when not on `barbacompany.com.ar`.

---

## 9. Environment Variables

| Variable | What it controls |
|---|---|
| `DB_NAME` | PostgreSQL database name (default: `peluqueria_db`) |
| `DB_USER` | PostgreSQL username (default: `admin`) |
| `DB_PASSWORD` | PostgreSQL password (default: `admin123`) |
| `DB_HOST` | PostgreSQL host (default: `localhost`) |
| `DB_PORT` | PostgreSQL port (default: `5432`) |
| `SECRET_KEY` | Flask secret key used for session signing and CSRF tokens |
| `TZ` | System timezone (should be `America/Argentina/Buenos_Aires`) |
| `POSTGRES_DB` | Database name for Docker Compose Postgres container |
| `POSTGRES_USER` | Username for Docker Compose Postgres container |
| `POSTGRES_PASSWORD` | Password for Docker Compose Postgres container |
| `MAIL_SERVER` | SMTP server hostname (default: `smtp.gmail.com`) |
| `MAIL_PORT` | SMTP port (default: `587`) |
| `MAIL_USE_TLS` | Whether to use STARTTLS (`true`/`false`, default: `true`) |
| `MAIL_USE_SSL` | Whether to use SSL (default: `false`) |
| `MAIL_USERNAME` | SMTP account email address (Gmail recommended) |
| `MAIL_PASSWORD` | SMTP password or Gmail App Password |
| `MAIL_SENDER_NAME` | Display name for outgoing emails (default: `BarberPay`) |

---

## 10. Key Business Logic & Rules

### Payment Amount Validation
- When recording a payment, the system enforces that the amounts entered match the expected total within a $0.01 tolerance.
- For single-method payments: `amount_method1 − tip == service_price` (tip is separate from the service cost).
- For split payments: `amount_method1 + amount_method2 == total_owed + tip`.
- Negative amounts or tips are rejected.
- The same payment method cannot be used twice in a split payment.

### Service Pricing Tiers
Three tiers exist per service:
- **Comun (standard):** Full price. Owner receives `price − employee_commission`.
- **Amigo (friend/voucher):** Uses `precio_amigo`. The barber's commission is treated as a **cost to the owner** (i.e., subtracted from owner total). This models a scenario where the service is provided as a courtesy or at cost.
- **Descuento (discount):** Uses `precio_descuento`. Owner's share is calculated as the difference between the standard and discounted owner margin.

### Membership Logic
- A client can hold at most one active membership per plan type per salon (enforced by the `(dni, peluqueria_id)` unique constraint).
- If a client with an existing active membership purchases again, their uses are **topped up** rather than creating a duplicate.
- A membership use decrements `usos_disponibles` by 1 at checkout. If uses reach 0, the system rejects the checkout.
- Deleting a payment that used a membership restores 1 use. Deleting a payment that purchased a new membership deletes the membership (if unused) or reverses the purchased uses (if it was a top-up on an existing membership). Deletion is blocked if the membership was partially used after purchase.

### Product Stock Management
- Stock (`cantidad`) is decremented when products are sold and restored when the corresponding payment is deleted.
- If stock is insufficient at checkout, the transaction is rejected before any database write.

### Barber Payroll Duplicate Prevention
- The system prevents recording two payroll entries for the same barber covering the same date range in the same salon (HTTP 409 conflict).
- Discounts and extras require written justifications when their amounts are greater than zero.
- The sum of bank transfer + cash must equal the final payout amount.

### Domain-Based Branding
The layout template and a client-side script check `window.location.hostname`. If the host is `barbacompany.com.ar`, the Barba&Co logo image is shown; otherwise a text fallback ("Gestor de Pagos") is rendered. The server-side `inject_logo` context processor does the same check on `request.host`.

### Session Scoping
All data queries are scoped to `session['salon_id']`, ensuring users of one salon cannot access another salon's data. This is enforced in every route individually (there is no middleware-level enforcement).

### Soft Deletion
Barbers, services, products, and payment methods use a soft-delete pattern (`active = False`) rather than being deleted from the database. This preserves the integrity of historical payment records that reference these entities via foreign keys. Membership types and hard user records are hard-deleted.

### Timezone Handling
All timestamps are stored and compared in `America/Argentina/Buenos_Aires` (UTC-3, no DST). The database timezone is explicitly set at startup. The `now_buenos_aires()` helper function is used as the default for all timestamp columns.
