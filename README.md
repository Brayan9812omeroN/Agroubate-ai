# AgroUbaté AI

Plataforma web de apoyo a la decisión para ganaderos de la provincia de Ubaté
(Cundinamarca): compara precios de insumos entre almacenes agropecuarios e
identifica el comprador de leche que mejor paga por litro.

## Arquitectura

```
Navegador (HTML + CSS + JS puro, sin build step)
        │  fetch() → JSON
        ▼
Flask (Python) ── API REST (/api/...) + sirve la interfaz (templates/static)
        │  sqlite3 (módulo estándar de Python, sin ORM externo)
        ▼
SQLite (archivo agroubate.db, se crea y se llena solo al arrancar)
```

Todo corre en un único proceso Python, con una única dependencia externa
(Flask): no se necesita Node, ni un servidor de base de datos aparte, ni
pasos de compilación en el frontend, ni instalar un ORM adicional.

## Estructura del proyecto

```
agroubate-ai/
├── app.py              # App Flask: rutas web + API REST
├── database.py           # Esquema (sqlite3) y siembra de datos de ejemplo
├── requirements.txt
├── templates/
│   └── index.html        # Interfaz principal
└── static/
    ├── css/style.css
    └── js/main.js         # Lógica de interfaz (fetch a la API)
```

## Cómo ejecutar el proyecto localmente

1. Requisitos: tener Python 3.10+ instalado.
2. Crear un entorno virtual (recomendado) e instalar dependencias:

   ```bash
   cd agroubate-ai
   python -m venv venv
   source venv/bin/activate      # En Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Ejecutar la aplicación:

   ```bash
   python app.py
   ```

4. Abrir el navegador en: **http://localhost:5000**

La primera vez que se ejecuta, `app.py` crea el archivo `agroubate.db`
(SQLite) y lo llena automáticamente con datos de ejemplo (almacenes de
Ubaté, Carmen de Carupa y Sutatausa, insumos, y compradores de leche), para
que la plataforma sea usable de inmediato.

## Funcionalidades implementadas en esta fase

- **Comparación de insumos**: filtrar por tipo (concentrados, sales
  mineralizadas, medicamentos), elegir un producto y ver su precio en cada
  almacén, ordenado del más barato al más caro.
- **Mejor precio de leche**: tabla de compradores (industrias, cooperativas
  de acopio, lecherías locales) ordenada de mayor a menor precio total
  (precio base + bonificación por calidad), con el mejor destacado.
- **API REST** documentada abajo, reutilizable por cualquier frontend futuro
  o por un módulo de inteligencia artificial.
- Base de datos relacional con datos reales de referencia de la subregión
  de Ubaté, lista para ampliarse con registros reales.

## Endpoints de la API

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/insumos?tipo=` | Lista insumos (filtro opcional por tipo) |
| GET | `/api/insumos/<id>/precios` | Compara precios de un insumo entre almacenes |
| GET | `/api/almacenes` | Lista los almacenes registrados |
| GET | `/api/leche/compradores` | Lista compradores de leche ordenados por precio |
| GET | `/api/leche/mejor-precio` | Devuelve el comprador con el mejor precio |
| GET | `/api/health` | Verifica que el servicio esté activo |

## Próximas ampliaciones (fuera del alcance de esta fase)

- Módulo de IA en Python (scikit-learn / pandas) para predecir tendencias de
  precios de insumos y leche a partir del histórico.
- Formulario de administración para que los almacenes y compradores
  actualicen sus propios precios.
- Autenticación de usuarios (ganaderos, almacenes, compradores).
- Despliegue en un servicio como Render, Railway o PythonAnywhere.
