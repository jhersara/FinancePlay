# Finanzas Personales: Control de Ingresos y Gastos

Este proyecto es una aplicación web sencilla y personalizable para llevar un control detallado de tus ingresos y gastos. Inspirado en la estética moderna de Trii, ofrece una interfaz limpia y visualizaciones claras para ayudarte a entender mejor tu salud financiera.

## ✨ Características

-   **Dashboard Interactivo**: Visualiza un resumen de tu balance total, ingresos y gastos del mes actual.
-   **Gestión de Transacciones**: Registra fácilmente tus ingresos y gastos con descripciones, montos, fechas y categorías.
-   **Categorías Personalizables**: Crea y gestiona tus propias categorías de ingresos y gastos, asignándoles colores para una mejor organización visual.
-   **Gráficas Estadísticas**: Obtén insights a través de:
    -   Un gráfico de barras que compara ingresos y gastos mensuales.
    -   Un gráfico de dona que muestra la distribución de tus gastos por categoría.
    -   Un gráfico de líneas para visualizar tendencias de ingresos y gastos a lo largo del tiempo.
-   **Diseño Moderno y Responsivo**: Interfaz de usuario intuitiva con un tema de color naranja vibrante, optimizada para dispositivos móviles y de escritorio.
-   **Base de Datos Local**: Utiliza SQLite para almacenar tus datos de forma segura y privada en tu máquina.

## 🚀 Tecnologías Utilizadas

-   **Backend**: `Flask` (Python)
    -   `Flask-SQLAlchemy`: ORM para interactuar con la base de datos.
    -   `SQLite`: Base de datos ligera y embebida.
    -   `Flask-CORS`: Para manejar las políticas de Cross-Origin Resource Sharing.
-   **Frontend**:
    -   `HTML5`, `CSS3`, `JavaScript` (Vanilla JS)
    -   `Bootstrap 5`: Framework CSS para un diseño responsivo y moderno.
    -   `Chart.js`: Librería para la creación de gráficos interactivos.
-   **Despliegue**: Compatible con entornos de despliegue basados en Flask.

## ⚙️ Configuración y Ejecución Local

Sigue estos pasos para configurar y ejecutar el proyecto en tu máquina local:

1.  **Clonar el Repositorio**:
    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd finanzas_personales
    ```

2.  **Crear y Activar el Entorno Virtual**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instalar Dependencias**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Ejecutar la Aplicación Flask**:
    ```bash
    python src/main.py
    ```
    El servidor se iniciará en `http://127.0.0.1:5000`.

5.  **Acceder a la Aplicación**: Abre tu navegador web y visita `http://127.0.0.1:5000`.

## 💡 Estructura del Proyecto

```
finanzas_personales/
├── venv/                   # Entorno virtual de Python
├── src/
│   ├── database/           # Contiene el archivo de la base de datos SQLite (app.db)
│   ├── models/             # Definiciones de los modelos de la base de datos (User, Categoria, Transaccion)
│   ├── routes/             # Archivos con las rutas de la API (transacciones, categorias, estadisticas, user)
│   ├── static/             # Archivos estáticos del frontend (HTML, CSS, JS, favicon)
│   │   ├── index.html
│   │   ├── styles.css
│   │   └── app.js
│   └── main.py             # Punto de entrada principal de la aplicación Flask
├── requirements.txt        # Lista de dependencias de Python
└── README.md               # Este archivo
```

## 🔌 Endpoints de la API (Backend)

La aplicación expone los siguientes endpoints RESTful:

-   `GET /api/dashboard`: Obtiene datos resumidos para el dashboard.
-   `GET /api/transacciones`: Lista todas las transacciones (con filtros opcionales).
-   `POST /api/transacciones`: Crea una nueva transacción.
-   `PUT /api/transacciones/<id>`: Actualiza una transacción existente.
-   `DELETE /api/transacciones/<id>`: Elimina una transacción.
-   `GET /api/categorias`: Lista todas las categorías.
-   `POST /api/categorias`: Crea una nueva categoría.
-   `PUT /api/categorias/<id>`: Actualiza una categoría existente.
-   `DELETE /api/categorias/<id>`: Elimina una categoría.
-   `GET /api/estadisticas/resumen-mensual`: Resumen de ingresos y gastos por mes.
-   `GET /api/estadisticas/por-categoria`: Estadísticas de gastos/ingresos por categoría.
-   `GET /api/estadisticas/tendencias`: Tendencias de ingresos y gastos en los últimos meses.
-   `GET /api/estadisticas/metricas`: Métricas clave como promedio de gasto, categoría más gastada, etc.

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Si tienes ideas para mejorar la aplicación, no dudes en abrir un issue o enviar un pull request.

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo `LICENSE` para más detalles.
