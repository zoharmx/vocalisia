from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import httpx
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = FastAPI(
    title="Vocalis AI Backend",
    description="API backend para generar ideas de campañas con Gemini",
    version="1.0.0"
)

# Configuración de CORS para permitir peticiones desde Firebase Hosting
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://vocalisia.web.app",
        "https://vocalisia.firebaseapp.com",
        "http://localhost:5000",  # Para desarrollo local
        "http://127.0.0.1:5000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo de datos para la petición
class CampaignRequest(BaseModel):
    clinic_name: str
    clinic_specialty: Optional[str] = "odontología general"

# Modelo de respuesta
class CampaignResponse(BaseModel):
    ideas: list[str]
    clinic_name: str
    success: bool
    message: Optional[str] = None

@app.get("/")
async def root():
    """Endpoint de bienvenida"""
    return {
        "message": "Vocalis AI Backend API",
        "status": "operational",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check para monitoreo"""
    return {"status": "healthy"}

@app.post("/api/generate-campaign-ideas", response_model=CampaignResponse)
async def generate_campaign_ideas(request: CampaignRequest):
    """
    Genera ideas de campañas de marketing usando Gemini AI
    
    Args:
        request: Objeto con clinic_name y clinic_specialty
    
    Returns:
        CampaignResponse con las ideas generadas
    """
    
    # Obtener API key desde variables de entorno
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    
    if not gemini_api_key:
        raise HTTPException(
            status_code=500, 
            detail="API Key de Gemini no configurada en el servidor"
        )
    
    # Construir el prompt del sistema
    system_prompt = """Eres un experto en marketing para clínicas dentales en Latinoamérica. 
    Tu tarea es generar 3 ideas de campañas de marketing creativas y concisas que puedan ser 
    ejecutadas por un agente de voz de IA llamado Vocalis AI. Las campañas deben ser para 
    llamadas salientes. Cada idea debe tener un título en negrita (usando asteriscos, 
    ej. **Título de Campaña**) y una breve descripción de 2-3 líneas. No uses ningún otro 
    formato. No incluyas introducciones ni conclusiones."""
    
    # Construir el prompt del usuario
    user_query = f"""Genera 3 ideas de campaña para una clínica llamada "{request.clinic_name}" 
    que se especializa en "{request.clinic_specialty}"."""
    
    # URL de la API de Gemini
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={gemini_api_key}"
    
    # Payload para Gemini
    payload = {
        "contents": [
            {
                "parts": [{"text": user_query}]
            }
        ],
        "systemInstruction": {
            "parts": [{"text": system_prompt}]
        },
        "generationConfig": {
            "temperature": 0.9,
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": 1024,
        }
    }
    
    try:
        # Hacer la petición a Gemini usando httpx (async)
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                api_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            # Verificar si la petición fue exitosa
            response.raise_for_status()
            
            result = response.json()
            
            # Extraer el texto generado
            candidate = result.get("candidates", [{}])[0]
            generated_text = candidate.get("content", {}).get("parts", [{}])[0].get("text", "")
            
            if not generated_text:
                raise HTTPException(
                    status_code=500,
                    detail="La API de Gemini no devolvió contenido"
                )
            
            # Procesar el texto generado en una lista de ideas
            ideas = [
                line.strip() 
                for line in generated_text.split('\n') 
                if line.strip()
            ]
            
            return CampaignResponse(
                ideas=ideas,
                clinic_name=request.clinic_name,
                success=True,
                message="Ideas generadas exitosamente"
            )
            
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Error al llamar a la API de Gemini: {e.response.text}"
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Error de conexión con la API de Gemini: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Manejador personalizado de excepciones HTTP"""
    return {
        "success": False,
        "message": exc.detail,
        "status_code": exc.status_code
    }