
# Variaciones de Acciones por Mercado

Este proyecto muestra las acciones con mayor variación en los mercados NYSE, NASDAQ, EuroStoxx, Madrid y Londres.

## Funciones

- Ranking diario, mensual y anual
- Enlace directo a gráficos de Yahoo Finance
- Visualización de gráficos con medias móviles
- Informe PDF automático
- Envío diario por correo electrónico

## Despliegue en Streamlit Cloud

1. Sube este proyecto a un repositorio de GitHub
2. Accede a [Streamlit Cloud](https://streamlit.io/cloud)
3. Crea una nueva app conectando tu cuenta GitHub
4. Selecciona el archivo `app.py` como archivo principal
5. Añade tus credenciales en `secrets.toml`

## Uso local

1. Instala las dependencias:

```bash
pip install -r requirements.txt
```

2. Crea el archivo `.env` o usa `secrets.toml`
3. Ejecuta la aplicación web:

```bash
streamlit run app.py
```

4. Para generar y enviar informe diario:

```bash
python main.py
```

## Créditos

Desarrollado con ❤️ por Carlos Baranda
