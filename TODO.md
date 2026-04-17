# Tareas

## 1. Editar movimientos
- [ ] Poder editar los movimientos en la solapa de cierre
  - [x] Desarrollar servicios
  - [x] Desarrollar para membresía
  - [ ] Desarrollar para producto
    - [ ] Solo los que tengan rol de admin

---

## 2. valeXmembresia - Números de membresía con DNI
- [ ] Separar de alguna forma el tipo de membresía para almacenar varios tipos para el mismo usuario

---

## 3. Fecha en formularios
- [ ] Las fechas en los formularios aparecen como `mm/dd/aaaa`. Modificar para que sean `dd/mm/aaaa`
- [ ] Revisar entornos
  - [x] Máquina de trabajo → `dd/mm/aaaa`
  - [ ] Máquina propia → `mm/dd/aaaa`
  - [ ] Server → `mm/dd/aaaa`

---

## 4. Ocultar elementos de navegación
- [ ] Si no está logueado, ocultar:
  - [ ] Agregar pago
  - [ ] Cierre
  - [ ] Administrar

---

## 5. calcular_pagos_entre_fechas
- [ ] Factorizar función

---

## 6. Múltiples peluquerías
- [ ] Cambiar logo dependiendo de la peluquería desde donde se accede

---

# 7. Nuevo módulo: Pagos a barberos

## 7.1 Agregar Pago

### Seleccionar
- [x] Barbero a pagar
- [x] Plazo que se le va a pagar
  - [x] Fecha inicio
  - [x] Fecha fin

### Mostrar
- [x] Monto a pagar (mismo método que hay en pagos)

### Ingresar
- [x] Descuentos + justificación
- [x] Agregados + justificación
- [x] Monto y método de pago
  - [x] Transferencia
  - [x] Efectivo

### Botones
- [x] Guardar
- [ ] Cancelar
- [ ] Enviar mail
  - [ ] Enviar mail con "recibo" a ambos

---

## 7.2 Pagos Realizados

- [x] Panel donde se muestren los pagos realizados (similar a sección pagos)

### Debe contener
- [x] Barbero
- [x] Fecha inicio
- [x] Fecha fin
- [x] Monto por rango
- [x] Fecha pago
- [x] Monto descuento (*)
- [x] Monto agregado (*)
- [x] Monto final = Monto por rango - Monto descuento + Monto agregado

### Acciones
- [ ] Botón para visualizar
  - [x] Registro completo con todos los datos ingresados
  - [x] Monto descuento (*)
  - [x] Justificación descuento
  - [x] Monto agregado (*)
  - [x] Justificación agregado
  - [ ] Botón enviar mail

- [x] Botón editar
  - [x] Modificar
  - [x] Eliminar