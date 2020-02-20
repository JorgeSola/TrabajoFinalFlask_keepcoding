## Instrucciones de instalación

1. Crear entorno virtual y activarlo.

2. Instalar las dependencias del fichero requirements.txt
```
pip install -r requirements.txt
```

3. Crear la variable de entorno `FLASK_APP` con el valor `run.py`

4. Obtener API key:
```
Meta el siguiente enlace en su navegador y siga las instruciones para conseguir su API key personal.
https://coinmarketcap.com/api/
```
```
Una vez conseguida la API key, vaya al archivo routes.py
```
```
Escriba la su API key donde pone <escriba aquí su Api key>
```

5. Ejecutar el archivo create_table.py una única vez para crear la tabla de datos.
```
run create_table.py 
```

6. Lanzar la aplicación
```
flask run
```
