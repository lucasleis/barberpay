"""
Script de diagnóstico: verifica el estado de emails en barberos y pagos.
Ejecutar desde la raíz del proyecto:
    python diagnostico_emails.py
"""
import os
from dotenv import load_dotenv

load_dotenv()

import psycopg2

conn = psycopg2.connect(
    dbname=os.environ.get('DB_NAME', 'peluqueria_db'),
    user=os.environ.get('DB_USER', 'admin'),
    password=os.environ.get('DB_PASSWORD', 'admin123'),
    host=os.environ.get('DB_HOST', 'localhost'),
    port=os.environ.get('DB_PORT', '5432'),
)
cur = conn.cursor()

print("=" * 60)
print("BARBEROS EN LA BASE DE DATOS")
print("=" * 60)
cur.execute("SELECT id, name, active, email FROM barberos ORDER BY id;")
for row in cur.fetchall():
    bid, name, active, email = row
    estado = "✓ activo" if active else "✗ inactivo"
    email_str = email if email else "⚠️  NULL"
    print(f"  id={bid:3d}  [{estado}]  {name:<20}  email: {email_str}")

print()
print("=" * 60)
print("PAGOS A BARBEROS Y SUS EMAILS")
print("=" * 60)
cur.execute("""
    SELECT pb.id, pb.barber_id, b.name, b.email, b.active
    FROM pagos_barberos pb
    JOIN barberos b ON b.id = pb.barber_id
    ORDER BY pb.id DESC
    LIMIT 20;
""")
rows = cur.fetchall()
problemas = 0
for row in rows:
    pid, bid, name, email, active = row
    if not email:
        print(f"  ❌ pago_id={pid}  barber_id={bid}  [{name}]  email=NULL  active={active}")
        problemas += 1
    else:
        print(f"  ✅ pago_id={pid}  barber_id={bid}  [{name}]  email={email}  active={active}")

print()
if problemas:
    print(f"⚠️  {problemas} pago(s) referencian barberos SIN email.")
    print()
    print("SOLUCIÓN RÁPIDA: ejecutar el siguiente SQL para copiar emails")
    print("desde el barbero activo con el mismo nombre:")
    print()
    print("""UPDATE barberos b_viejo
SET email = b_nuevo.email
FROM barberos b_nuevo
WHERE b_viejo.email IS NULL
  AND b_viejo.active = FALSE
  AND b_nuevo.active = TRUE
  AND b_viejo.name = b_nuevo.name
  AND b_viejo.peluqueria_id = b_nuevo.peluqueria_id
  AND b_nuevo.email IS NOT NULL;""")
else:
    print("✅ Todos los pagos referencian barberos con email configurado.")

cur.close()
conn.close()
