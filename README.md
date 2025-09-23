
# Correr container posgres
```
docker run --name postgres-peluqueria -e POSTGRES_USER=admin -e POSTGRES_PASSWORD=admin123 -e POSTGRES_DB=peluqueria_db -p 5432:5432 -d postgres
```

# Iniciar ejecucion container stopped
```
docker start container_id
```

# Acceder por consola a container postgres 
```
docker exec -it postgres-peluqueria psql -U admin -d peluqueria_db 
```

comandos para acceder a la bd por consola.

1. Mostrar todas las bases de datos
```
\l
```

2. Cambiar a otra bd
```
\c postgres
```

3. Mostrar todas las tablas en la base de datos actual
```
\dt
```

4. Hacer un SELECT para ver datos de cualquier tabla
```
SELECT * FROM empleados;

SELECT * FROM turnos ORDER BY date DESC LIMIT 5;

```

5. Hacer un INSERT
```
INSERT INTO peluquerias (id, nombre) VALUES (1, 'Peluquería Central');
```

6. Borrar database
```
DROP DATABASE peluqueria_db ;
```

7. Settear huso horario
```
SET TIMEZONE TO 'America/Argentina/Buenos_Aires';
```

8. Ver sesiones abieras
```
SELECT pid, datname, usename, application_name, client_addr, state FROM pg_stat_activity WHERE datname = 'peluqueria_db';
```

9. Kill session
```
SELECT pg_terminate_backend(<pid>);
```

10. Salir de psql
```
\q
```

11. Ver roles de usuarios
```
\du
```



# Usuarios en db

Agregar usuario
```
python -m app.create_users_pass_db
```

```
python -m app.delete_users_pass_db
```






## Frontend

Quiero que crees una landing page para una barbería, desarrollada en React.
Los requisitos son:

Logo visible en el encabezado.

Sección de servicios con el detalle de los servicios que ofrece la barbería (ejemplo: cortes, perfilado de barba, color, etc.).

Links externos:

Link a Instagram de la barbería.

Link a gestor de turnos online.

Link a WhatsApp para agendar un turno rápido.

Ubicación: integrar un mapa o mostrar la dirección física de la barbería.

Teléfono de contacto visible.

Detalles adicionales:

Diseño moderno, limpio y responsivo (que se vea bien en PC y en celular).

Paleta de colores acorde a barbería (negro, blanco, gris, con detalles en dorado o rojo).

Usar componentes reutilizables y estilos con CSS Modules o Tailwind.

Incluir un botón de "Reservar Turno" que lleve directamente al gestor de turnos.

Entrega: código React completo con componentes, estilos y una estructura lista para correr.

¿Querés que te lo adapte también como prompt para pedir imágenes (logo/banners) en una IA de imágenes o solo lo enfocamos en el desarrollo web en React?




# Levantar react con python
```
cd landing_v1
npm install
npm run build
```

