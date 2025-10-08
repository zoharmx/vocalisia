# Vocalis AI - Backend

Backend API para Vocalis AI, construido con FastAPI y desplegado en Render.

## Caracter�sticas

-  API REST con FastAPI
-  Generaci�n de ideas de campa�a con Gemini AI
-  CORS configurado para Firebase Hosting
-  Health checks para monitoreo
-  Desplegado en Render

## Endpoints

### GET /
Endpoint de bienvenida que muestra informaci�n b�sica de la API.

### GET /health
Health check para monitoreo del servicio.

### POST /api/generate-campaign-ideas
Genera ideas de campa�as de marketing usando Gemini AI.

**Body:**
```json
{
  "clinic_name": "Nombre de la cl�nica",
  "clinic_specialty": "Especialidad (opcional)"
}
```

**Response:**
```json
{
  "ideas": ["Idea 1", "Idea 2", "Idea 3"],
  "clinic_name": "Nombre de la cl�nica",
  "success": true,
  "message": "Ideas generadas exitosamente"
}
```

## Configuraci�n Local

1. Instala las dependencias:
```bash
pip install -r requirements.txt
```

2. Crea un archivo `.env` basado en `.env.example`:
```bash
cp .env.example .env
```

3. Agrega tu API key de Gemini en `.env`:
```
GEMINI_API_KEY=tu_api_key_aqui
```

4. Ejecuta el servidor:
```bash
uvicorn app.main:app --reload
```

El servidor estar� disponible en `http://localhost:8000`

## Despliegue en Render

1. Sube el c�digo a GitHub
2. Crea un nuevo Web Service en Render
3. Conecta tu repositorio
4. Configura las variables de entorno:
   - `GEMINI_API_KEY`: Tu API key de Gemini
   - `ENVIRONMENT`: production
5. Render detectar� autom�ticamente el `render.yaml` y desplegar� el servicio

## Variables de Entorno

- `GEMINI_API_KEY`: API key de Google Gemini (requerida)
- `ENVIRONMENT`: Entorno de ejecuci�n (development/production)

## URLs

- **Frontend (Firebase)**: https://vocalisia.web.app
- **Backend (Render)**: https://vocalis-ai-backend.onrender.com
