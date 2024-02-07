# Project Title

## Table of Contents

- [About](#about)
- [Getting Started](#getting_started)
- [Usage](#usage)
- [Contributing](../CONTRIBUTING.md)

## About <a name = "about"></a>

Automatizacion de procesos de la empresa, con el fin de optimizar tiempos y evitar actualizar el catalogo de empleados de forma manual, catalogo de empleados de herramienta de archivo, auditoria de expedientes.

## Getting Started <a name = "getting_started"></a>

Al cargar este proyecto a servidor de automatizaciones realizar las siguientes acciones:

- Ejecutar el siguiente comando en la terminal:

```
pip install -r requirements.txt
```

## Usage <a name = "usage"></a>

Implementar para actualizar el catalogo de empleados de la herramienta usando un cronjob.

### Ejemplo de uso y automatizacion con cronjob

- Ejecutar el siguiente comando en la terminal:

```
crontab -e
```

- Agregar el siguiente cronjob:

```
* * * * cd /home/usuario/automatizacion_procesos_empresa && python3 automatizacion_procesos_empresa.py
```

- Guardar y salir de la terminal.
