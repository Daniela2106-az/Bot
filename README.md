# Bot

Bot en Python (Selenium) que extrae datos de negocios desde Google Maps y los guarda en una base de datos SQLite y en un archivo Excel. Útil para generar listas de prospectos por tipo de empresa y ciudad.

## Características

- Pide por consola el tipo de empresa y la ciudad (ej: `restaurantes` / `Barranquilla, Colombia`).
- Busca en Google Maps y hace scroll automático en la lista de resultados hasta que no aparecen más negocios.
- Entra a cada negocio y extrae: nombre, dirección, teléfono y página web.
- Normaliza teléfonos colombianos (agrega `+57`, y `+57601` para fijos de Bogotá).
- Guarda todo en SQLite (`negocios.db`) evitando duplicados por `maps_link`.
- Exporta los resultados a `negocios_extraidos.xlsx`.
- Menú con opción para vaciar la base de datos.

## Estructura

```
Bot/
├── maps_links.py            # Bot de Google Maps -> SQLite -> Excel
├── negocios_extraidos.xlsx  # Exportación de los negocios
└── README.md
```

`negocios.db` se crea automáticamente al ejecutar el bot.

### Tabla `negocios`

| Campo | Tipo | Descripción |
|---|---|---|
| id | INTEGER PK | Identificador |
| categoria | TEXT | Tipo de empresa buscada |
| ciudad | TEXT | Ciudad/país de la búsqueda |
| nombre, direccion, telefono, pagina_web | TEXT | Datos del negocio |
| maps_link | TEXT UNIQUE | URL del negocio en Maps |
| fecha_registro | TIMESTAMP | Fecha de inserción |

## Requisitos

- Python 3.9+
- Google Chrome
- Dependencias: `selenium`, `webdriver-manager`, `pandas`, `openpyxl`

```bash
pip install selenium webdriver-manager pandas openpyxl
```

## Uso

```bash
python maps_links.py
```

1. Elige `1` para iniciar una búsqueda o `2` para vaciar la base de datos.
2. Ingresa el tipo de empresa y la ciudad.
3. Al terminar, revisa `negocios_extraidos.xlsx`.

## Aviso

Automatizar Google Maps puede ir contra sus términos de servicio. Úsalo de forma responsable.
