from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import httpx
import os
from dotenv import load_dotenv
from prompts import SYSTEM_PROMPT

# Cargar variables de entorno desde .env (para desarrollo local)
load_dotenv()

app = FastAPI(
    title="Vocalis AI Backend",
    description="API backend para generar ideas de campañas con Gemini",
    version="1.0.1" # Versión actualizada
)

# Configuración de CORS para permitir peticiones desde Firebase Hosting
# Esto es crucial para que tu frontend pueda comunicarse con este backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://vocalisia.web.app",
        "https://vocalisia.firebaseapp.com",
        "http://localhost:5000",
        "http://127.0.0.1:5000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo de datos para la petición que llega desde el frontend
class CampaignRequest(BaseModel):
    clinic_name: str
    clinic_specialty: Optional[str] = "odontología general"

# Modelo de datos para la respuesta que se envía al frontend
class CampaignResponse(BaseModel):
    ideas: list[str]
    clinic_name: str

@app.get("/")
async def root():
    """Endpoint de bienvenida para verificar que el servicio está activo."""
    return {
        "message": "Vocalis AI Backend API",
        "status": "operational",
        "version": "1.0.1"
    }

@app.get("/health")
async def health_check():
    """Endpoint de 'health check' para el monitoreo de Render."""
    return {"status": "healthy"}

@app.post("/api/generate-campaign-ideas", response_model=CampaignResponse)
async def generate_campaign_ideas(request: CampaignRequest):
    """
    Genera ideas de campañas de marketing usando la API de Gemini.
    """
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise HTTPException(
            status_code=500, 
            detail="Error de configuración del servidor: La clave de API de Gemini no está definida."
        )
    
    user_query = f"""Genera 3 ideas de campaña para una clínica llamada "{request.clinic_name}" 
    que se especializa en "{request.clinic_specialty}"."""
    
    # --- MODELO CORREGIDO ---
    # Usamos un modelo estable como 'gemini-1.5-flash-latest'.
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={gemini_api_key}"
    
    payload = {
        "contents": [{"parts": [{"text": user_query}]}],
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "generationConfig": {
            "temperature": 0.9,
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": 1024,
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(api_url, json=payload, headers={"Content-Type": "application/json"})
            response.raise_for_status()
            result = response.json()
            
            candidate = result.get("candidates", [{}])[0]
            generated_text = candidate.get("content", {}).get("parts", [{}])[0].get("text", "")
            
            if not generated_text:
                raise HTTPException(status_code=500, detail="La API de Gemini no devolvió contenido.")
            
            ideas = [line.strip() for line in generated_text.split('\n') if line.strip()]
            
            return CampaignResponse(ideas=ideas, clinic_name=request.clinic_name)
            
    except httpx.HTTPStatusError as e:
        error_details = e.response.json().get('error', {}).get('message', e.response.text)
        raise HTTPException(status_code=e.response.status_code, detail=f"Error en la API de Gemini: {error_details}")
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Error de conexión con la API de Gemini: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

# Manejador de excepciones global para devolver respuestas en formato JSON
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": exc.detail},
    )
