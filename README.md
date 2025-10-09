# Vocalis AI Backend

Backend API para generar ideas de campañas de marketing dental usando Google Gemini AI.

## Estructura del Proyecto

```
VocalisAI/
├── main.py              # Aplicación FastAPI
├── requirements.txt     # Dependencias Python
├── render.yaml         # Configuración de Render
├── .env                # Variables de entorno (local)
├── .gitignore          # Archivos ignorados por Git
└── public/             # Frontend (desplegado en Firebase)
    ├── index.html
    └── 404.html
```

## Configuración Local

1. Instalar dependencias:
```bash
pip install -r requirements.txt
```

2. Configurar variables de entorno en `.env`:
```
GEMINI_API_KEY=tu_api_key_aqui
PORT=8000
ENVIRONMENT=development
```

3. Ejecutar el servidor:
```bash
uvicorn main:app --reload --port 8000
```

El servidor estará disponible en `http://localhost:8000`

## Despliegue en Render

### Requisitos
- Cuenta en [Render](https://render.com)
- API Key de Google Gemini

### Pasos para desplegar

1. Conecta tu repositorio de GitHub a Render

2. Render detectará automáticamente el archivo `render.yaml`

3. Configura la variable de entorno:
   - `GEMINI_API_KEY`: Tu clave de API de Google Gemini
   - (Render configurará automáticamente `ENVIRONMENT=production`)

4. Render ejecutará automáticamente:
   - Build: `pip install --no-cache-dir -r requirements.txt`
   - Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Verificación del Despliegue

Una vez desplegado, verifica:
- Endpoint raíz: `https://tu-app.onrender.com/`
- Health check: `https://tu-app.onrender.com/health`
- API docs: `https://tu-app.onrender.com/docs`

## Endpoints

- `GET /` - Información del servicio
- `GET /health` - Health check
- `POST /api/generate-campaign-ideas` - Generar ideas de campañas

### Ejemplo de Request

```json
POST /api/generate-campaign-ideas
{
  "clinic_name": "Dental Sonrisas",
  "clinic_specialty": "ortodoncia"
}
```

### Ejemplo de Response

```json
{
  "ideas": [
    "**Campaña 1**: Descripción...",
    "**Campaña 2**: Descripción...",
    "**Campaña 3**: Descripción..."
  ],
  "clinic_name": "Dental Sonrisas"
}
```

## CORS

El backend está configurado para aceptar peticiones desde:
- `https://vocalisia.web.app`
- `https://vocalisia.firebaseapp.com`
- `http://localhost:5000`
- `http://127.0.0.1:5000`

## Tecnologías

- **FastAPI** - Framework web
- **Uvicorn** - Servidor ASGI
- **httpx** - Cliente HTTP asíncrono
- **Pydantic** - Validación de datos
- **Google Gemini AI** - Generación de contenido

## Notas Importantes

- El archivo `.env` NO debe ser versionado en Git
- Asegúrate de configurar `GEMINI_API_KEY` en Render antes del despliegue
- El plan gratuito de Render puede tener cold starts (el servicio se duerme después de inactividad)
