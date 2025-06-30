
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
