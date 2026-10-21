# Chaud & Glace - Sistema Analítico y Predictivo de Clientes 🍦☕

Aplicación web interactiva desarrollada con **Streamlit**, **Pandas** y **Scikit-Learn** para optimizar las campañas comerciales de **"Chaud & Glace"** (cafetería y heladería artesanal). 

Este sistema responde a la pregunta de negocio: **¿Qué clientes tienen mayor probabilidad de volver a comprar en nuestra última campaña y qué promoción o estrategia comercial deberíamos darles?**

## 🚀 Arquitectura y Estructura del Proyecto

El proyecto está construido bajo un enfoque modular de ciencia de datos y desarrollo full stack para facilitar el mantenimiento y la escalabilidad:


chaud_glace_streamlit/
│
├── .streamlit/
│   └── config.toml             # Configuración del tema visual y estilos (UI)
├── data/
│   └── clientes_chaud_glace.csv # Dataset generado sintéticamente
├── modules/
│   ├── __init__.py
│   ├── entender.py             # Carga inicial y estructura de datos
│   ├── limpiar.py              # Limpieza de nulos (mediana) y duplicados
│   ├── describir.py            # KPIs descriptivos y visualizaciones Plotly
│   ├── predecir.py             # Modelo de Regresión Logística (Scikit-Learn)
│   ├── prescribir.py           # Segmentación de clientes por probabilidad
│   └── decidir.py              # Acciones comerciales y estrategias de marketing
│
├── .gitignore                  # Archivos ignorados por Git
├── app.py                      # Punto de entrada principal de Streamlit
├── generar_datos_heladeria.py  # Script generador del dataset de clientes
├── requirements.txt            # Dependencias del proyecto
└── README.md                   # Documentación del proyecto

## 🎨 Configuración de Estilo y Tema (.streamlit/config.toml)
La carpeta .streamlit almacena el archivo config.toml, el cual define la tipografía customizada (Google Fonts Manrope y Fraunces), los bordes, espaciados y las paletas cromáticas personalizadas para el modo claro ([theme.light]) y modo oscuro ([theme.dark]), alineadas a la identidad de marca de Chaud & Glace:

## 📊 Descripción de Módulos

generar_datos_heladeria.py: Genera un dataset robusto con más de 250 filas y 8 variables (id_cliente, frecuencia_visita_mes, gasto_promedio_mxn, producto_favorito, antiguedad_meses, visita_fin_semana, compro_ultima_campana, y edad), introduciendo intencionalmente valores nulos y filas duplicadas para simular un escenario de datos reales.

modules/entender.py: Realiza una exploración inicial mostrando dimensiones, vista previa de registros y tipos de datos.

modules/limpiar.py: Automatiza la detección/eliminación de duplicados y la imputación de valores nulos numéricos usando la mediana estadística.

modules/describir.py: Presenta KPIs clave mediante métricas visuales y gráficos de distribución por categoría de producto favorito (px.histogram).

modules/predecir.py: Entrena un modelo de Regresión Logística evaluando la probabilidad de compra en base a frecuencia de visitas, gasto promedio y antigüedad. Muestra el Accuracy y los coeficientes predictivos.

modules/prescribir.py: Segmenta la base de clientes según su probabilidad predicha en tres categorías: Alta (≥60%), Moderada (35-59%) y Baja (<35%).

modules/decidir.py: Panel dinámico interactivo que vincula cada segmento con una acción comercial concreta, un mensaje de marketing directo y su justificación analítica.

app.py: Orquestador principal con diseño adaptativo (wide layout), caché de datos y navegación basada en pestañas (st.tabs).

## 🛠️ Requisitos del Sistema
Python >= 3.10

Gestor de paquetes pip

Las dependencias principales se encuentran en el archivo requirements.txt:

streamlit >= 1.30.0

pandas >= 2.0.0

numpy >= 1.24.0

scikit-learn >= 1.3.0

plotly >= 5.18.0

## ⚙️ Guía de Instalación y Ejecución
Sigue estos pasos en tu terminal para configurar el entorno de ejecución desde cero:

1. Clonar el repositorio y posicionarte en el directorio


```
git clone <URL_DE_TU_REPOSITORIO>
cd chaud_glace_streamlit

```

2. Crear el entorno virtual
Windows:


```
python -m venv chaud_glace

```
macOS / Linux:


```
python3 -m venv chaud_glace

```
3. Activar el entorno virtual
Windows (Git Bash / Terminal):


```
source chaud_glace/Scripts/activate

```
Windows (Command Prompt / CMD):

DOS
chaud_glace\Scripts\activate.bat
Windows (PowerShell):

PowerShell
.\chaud_glace\Scripts\Activate.ps1

macOS / Linux:


```
source chaud_glace/bin/activate

```
4. Instalar dependencias
Con el entorno virtual activado, instala todas las librerías necesarias:


```
pip install --upgrade pip
pip install -r requirements.txt

```

5. Generar el conjunto de datos
Ejecuta el script para construir el archivo data/clientes_chaud_glace.csv:


```
python generar_datos_heladeria.py

```
6. Ejecutar la aplicación de Streamlit
Inicia el servidor local para abrir el panel en tu navegador web:

```
streamlit run app.py

```

👥 Autor
Desarrollado como solución analítica integral para Chaud & Glace.