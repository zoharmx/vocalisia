from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import httpx
import os
from dotenv import load_dotenv
from twilio.rest import Client
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant

# Cargar variables de entorno
load_dotenv()

app = FastAPI(
    title="Vocalis AI Backend",
    description="API backend para generar ideas de campañas con Gemini y conectar con Twilio",
    version="2.0.0"
)

# Configuración de CORS
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

# ==========================================
# MODELOS DE DATOS
# ==========================================

class CampaignRequest(BaseModel):
    clinic_name: str
    clinic_specialty: Optional[str] = "odontología general"

class CampaignResponse(BaseModel):
    success: bool
    ideas: list[str]
    clinic_name: str

class TwilioTokenRequest(BaseModel):
    identity: str

class TwilioTokenResponse(BaseModel):
    token: str
    identity: str

# ==========================================
# ENDPOINTS BÁSICOS
# ==========================================

@app.get("/")
async def root():
    """Endpoint de bienvenida"""
    return {
        "message": "Vocalis AI Backend API",
        "status": "operational",
        "version": "2.0.0",
        "features": ["Campaign Generation", "Twilio Voice Integration"]
    }

@app.get("/health")
async def health_check():
    """Health check para Render"""
    return {"status": "healthy"}

# ==========================================
# ENDPOINT: GENERAR TOKEN DE TWILIO
# ==========================================

@app.post("/api/get-twilio-token", response_model=TwilioTokenResponse)
async def get_twilio_token(request: TwilioTokenRequest):
    """
    Genera un token JWT de Twilio para permitir llamadas desde el navegador.
    
    Requisitos en .env:
    - TWILIO_ACCOUNT_SID: Tu Account SID de Twilio
    - TWILIO_API_KEY: Tu API Key de Twilio
    - TWILIO_API_SECRET: Tu API Secret de Twilio
    - TWILIO_TWIML_APP_SID: El SID de tu TwiML App
    """
    
    # Obtener credenciales de Twilio
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    api_key = os.getenv("TWILIO_API_KEY")
    api_secret = os.getenv("TWILIO_API_SECRET")
    twiml_app_sid = os.getenv("TWILIO_TWIML_APP_SID")
    
    if not all([account_sid, api_key, api_secret, twiml_app_sid]):
        raise HTTPException(
            status_code=500,
            detail="Credenciales de Twilio no configuradas correctamente"
        )
    
    try:
        # Crear Access Token
        token = AccessToken(
            account_sid,
            api_key,
            api_secret,
            identity=request.identity
        )
        
        # Crear Voice Grant
        voice_grant = VoiceGrant(
            outgoing_application_sid=twiml_app_sid,
            incoming_allow=True
        )
        
        # Agregar el grant al token
        token.add_grant(voice_grant)
        
        # Generar el token JWT
        jwt_token = token.to_jwt()
        
        return TwilioTokenResponse(
            token=jwt_token.decode('utf-8') if isinstance(jwt_token, bytes) else jwt_token,
            identity=request.identity
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al generar token de Twilio: {str(e)}"
        )

# ==========================================
# ENDPOINT: WEBHOOK DE TWILIO PARA LLAMADAS
# ==========================================

@app.post("/api/voice/incoming")
async def voice_incoming(request: Request):
    """
    Webhook que Twilio llama cuando se inicia una llamada desde el navegador.
    Retorna TwiML para conectar con tu número de Twilio.
    """
    from twilio.twiml.voice_response import VoiceResponse, Dial
    
    response = VoiceResponse()
    
    # Opción 1: Conectar directamente a tu número de Twilio con el agente IA
    dial = Dial(
        caller_id='+528141661014'  # Tu número de Twilio
    )
    dial.number('+528141661014')  # El número que contesta (tu agente IA)
    
    response.append(dial)
    
    return Response(content=str(response), media_type="application/xml")

# ==========================================
# ENDPOINT: GENERAR IDEAS DE CAMPAÑA
# ==========================================

@app.post("/api/generate-campaign-ideas", response_model=CampaignResponse)
async def generate_campaign_ideas(request: CampaignRequest):
    """
    Genera ideas de campañas de marketing usando la API de Gemini.
    """
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise HTTPException(
            status_code=500,
            detail="Error de configuración: La clave de API de Gemini no está definida."
        )
    
    system_prompt = """Eres un experto en marketing para clínicas dentales en Latinoamérica. 
    Tu tarea es generar 3 ideas de campañas de marketing creativas y concisas que puedan ser 
    ejecutadas por un agente de voz de IA llamado Vocalis AI. Las campañas deben ser para 
    llamadas salientes. Cada idea debe tener un título en negrita (usando asteriscos, 
    ej. **Título de Campaña**) y una breve descripción de 2-3 líneas. No uses ningún otro 
    formato. No incluyas introducciones ni conclusiones."""
    
    user_query = f"""Genera 3 ideas de campaña para una clínica llamada "{request.clinic_name}" 
    que se especializa en "{request.clinic_specialty}"."""
    
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={gemini_api_key}"
    
    payload = {
        "contents": [{"parts": [{"text": user_query}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]},
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

            return CampaignResponse(success=True, ideas=ideas, clinic_name=request.clinic_name)
            
    except httpx.HTTPStatusError as e:
        error_details = e.response.json().get('error', {}).get('message', e.response.text)
        raise HTTPException(status_code=e.response.status_code, detail=f"Error en la API de Gemini: {error_details}")
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Error de conexión con la API de Gemini: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

# ==========================================
# MANEJADOR DE EXCEPCIONES
# ==========================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": exc.detail},
    )