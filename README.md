
# Correr container posgres
```
docker run --name postgres-peluqueria -e POSTGRES_USER=admin -e POSTGRES_PASSWORD=admin123 -e POSTGRES_DB=peluqueria_db -p 5432:5432 -d postgres
```

# Iniciar ejecucion container stopped
```
docker start
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
```

5. Hacer un INSERT
```
INSERT INTO peluquerias (id, nombre) VALUES (1, 'Peluquería Central');
```

6. Salir de psql
```
\q
```