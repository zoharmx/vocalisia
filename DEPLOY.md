# Guía de Despliegue en Render

## Estado Actual del Proyecto

### Estructura de Archivos
```
VocalisAI/
├── main.py              # Backend FastAPI ✓
├── requirements.txt     # Dependencias ✓
├── render.yaml         # Configuración Render ✓
├── .env                # Variables locales (NO subir a Git) ✓
├── .gitignore          # Archivos ignorados ✓
├── test_server.py      # Script de verificación ✓
├── README.md           # Documentación ✓
└── public/             # Frontend (Firebase Hosting)
    ├── index.html
    └── 404.html
```

### Verificaciones Completadas
- [x] Estructura de carpetas correcta
- [x] .gitignore con codificación UTF-8
- [x] render.yaml configurado
- [x] Dependencias instaladas y funcionando
- [x] Backend probado localmente

## Pasos para Desplegar en Render

### 1. Preparar el Repositorio

```bash
# Asegúrate de que todos los cambios estén commiteados
git status
git add .
git commit -m "fix: Preparar proyecto para despliegue en Render"
git push origin main
```

### 2. Configurar en Render.com

1. Ve a [render.com](https://render.com) e inicia sesión
2. Click en "New +" → "Web Service"
3. Conecta tu repositorio de GitHub
4. Render detectará automáticamente `render.yaml`

### 3. Configurar Variables de Entorno

En el dashboard de Render, configura:

| Variable | Valor |
|----------|-------|
| `GEMINI_API_KEY` | `AIzaSyCIGMZcm5Hn00TfjQEUUu8iS-wleYePJ0I` |

**IMPORTANTE**: La variable `ENVIRONMENT=production` ya está configurada en `render.yaml`

### 4. Desplegar

1. Click en "Create Web Service"
2. Render ejecutará automáticamente:
   - Build: `pip install --no-cache-dir -r requirements.txt`
   - Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### 5. Verificar el Despliegue

Una vez desplegado, prueba estos endpoints:

```bash
# Endpoint raíz
curl https://tu-app.onrender.com/

# Health check
curl https://tu-app.onrender.com/health

# Documentación automática
https://tu-app.onrender.com/docs
```

### 6. Actualizar el Frontend

Actualiza la URL del backend en tu frontend (`public/index.html`):

```javascript
const BACKEND_URL = 'https://tu-app.onrender.com';
```

## Configuración Actual de render.yaml

```yaml
services:
  - type: web
    name: vocalis-ai-backend
    runtime: python
    region: oregon
    plan: free
    buildCommand: pip install --no-cache-dir -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: GEMINI_API_KEY
        sync: false
      - key: ENVIRONMENT
        value: production
```

## Solución de Problemas

### El servicio no inicia
- Verifica que `GEMINI_API_KEY` esté configurada en Render
- Revisa los logs en el dashboard de Render

### Error de CORS
- El backend ya está configurado para aceptar peticiones desde:
  - `https://vocalisia.web.app`
  - `https://vocalisia.firebaseapp.com`
  - Si desplegaste el frontend en otra URL, agrégala en `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://vocalisia.web.app",
        "https://vocalisia.firebaseapp.com",
        "https://tu-nuevo-dominio.com",  # Agregar aquí
        # ...
    ],
    # ...
)
```

### El servicio se duerme (Cold Start)
- En el plan gratuito de Render, el servicio se duerme después de 15 minutos de inactividad
- La primera petición después de dormir tomará ~30 segundos
- Considera un plan pago si necesitas disponibilidad 24/7

## Prueba Local Antes de Desplegar

Ejecuta el script de verificación:

```bash
python test_server.py
```

Inicia el servidor localmente:

```bash
uvicorn main:app --reload --port 8000
```

Prueba el endpoint:

```bash
curl -X POST http://localhost:8000/api/generate-campaign-ideas \
  -H "Content-Type: application/json" \
  -d '{"clinic_name": "Dental Test", "clinic_specialty": "ortodoncia"}'
```

## Siguientes Pasos

1. Desplegar el backend en Render
2. Obtener la URL del servicio desplegado
3. Actualizar el frontend con la nueva URL
4. Re-desplegar el frontend en Firebase
5. Probar la integración completa

## Notas de Seguridad

- ✓ `.env` está en `.gitignore` (no se sube a Git)
- ✓ Las API keys se configuran como variables de entorno en Render
- ⚠️ Considera rotar la API key de Gemini si fue expuesta públicamente
- ⚠️ Activa las restricciones de API key en Google Cloud Console
