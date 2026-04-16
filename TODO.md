# Tareas

## 1. Editar movimientos [ ]
- Poder editar los movimientos en la solapa de cierre. 
    - [✅] Desarrollar servicios
    - [✅] Desarrollar para membresia
    - [ ] Desarrollar para producto
        - [ ] Solo los que tengan rol de admin


## 2. valeXmembresia - Numeros de membresias con nro de dni
    - [ ] Separar de alguna forma el tipo de membresia para almacenar varios tipos para el mismo user


## 3. Fecha en formularios
    - [ ] Las fechas en lose muestra como s formularios aparecen como mm/dd/aaaa. modificar para que sean dd/mm/aaaa
    - [ ] Revisar entonrnos. 
        - [✅] Maquina laburo: dd/mm/aaaa. 
        - [ ] Maquina propia: mm/dd/aaaa
        - [ ] Server: mm/dd/aaaa


## 4. Ocultar elementos de agregar pago, cierre y administrar 
    - [ ] si no esta logueado elementos de agregar pago, cierre y administrar ocultos


## 5. calcular_pagos_entre_fechas
    - [ ] Factorizar funcion


## 6. Multiples peluquerias
    - [ ] Cambiar logo dependiendo de donde venga


## 7. Nuevo Modulo

- [ ] Agregar nueva seccion de pagos a barberos. Esta seccion va a tener 2 Partes:
	- [ ] Agregar Pago
	- [ ] Pagos Realizados

Agregar Pago
	Seleccionar:
		- [ ] Barbero a pagar
		- [ ] Plazo que se le va a pagar
			- [ ] Fecha Inicio 
			- [ ] Fecha Fin
	Mostrar:
		- [ ] Monto a pagar (mismo metodo que hay en pagos)
	Ingresar:
		- [ ] Descuentos + Justificacion
		- [ ] Agregados + Justificacion
		- [ ] Monto y metodo de pago (Transferencia y/o efectivo)
	Boton:
		- [ ] Guardar
		- [ ] Cancelar
		- [ ] Enviar mail
			Enviar mail con "recibo" a ambos


Pagos Realizados
	- [ ] Panel donde se muestren los pagos realizados. Similar a seccion pagos. Debe contener:
		- Barbero
		- Fecha Inicio
		- Fecha Fin
		- Monto por Rango
		- Fecha Pago
		- M. Descuento (*)
		- M. Agregado (*)
		- M. Final = Monto por Rango - M. Descuento + M. Agregado
		- Boton para visualizar:
			- Registro completo con todos los datos ingresados + : 
				- M. Descuento (*)
				- Justificacion Descuento
				- M. Agregado (*)
				- Justificacion Agregado
			- Boton enviar mail
		- Boton Editar
			- Modificar
			- Eliminar
			


