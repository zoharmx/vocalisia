"""
Script de prueba para verificar que el servidor FastAPI funciona correctamente.
"""
import sys
import os

def test_imports():
    """Verifica que todas las dependencias se puedan importar."""
    print("[*] Verificando imports...")
    try:
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        from pydantic import BaseModel
        import httpx
        from dotenv import load_dotenv
        print("  [OK] Todos los imports exitosos")
        return True
    except ImportError as e:
        print(f"  [ERROR] Error en imports: {e}")
        return False

def test_env_file():
    """Verifica que el archivo .env exista y contenga las variables necesarias."""
    print("\n[*] Verificando archivo .env...")
    if not os.path.exists('.env'):
        print("  [ERROR] Archivo .env no encontrado")
        return False

    from dotenv import load_dotenv
    load_dotenv()

    gemini_key = os.getenv('GEMINI_API_KEY')
    if not gemini_key:
        print("  [ERROR] GEMINI_API_KEY no configurada en .env")
        return False

    print(f"  [OK] GEMINI_API_KEY configurada (longitud: {len(gemini_key)})")
    return True

def test_main_module():
    """Verifica que el módulo main.py se pueda importar."""
    print("\n[*] Verificando main.py...")
    try:
        import main
        print("  [OK] main.py importado correctamente")
        print(f"  [OK] App: {main.app.title} v{main.app.version}")
        return True
    except Exception as e:
        print(f"  [ERROR] Error al importar main.py: {e}")
        return False

def main():
    print("=" * 50)
    print("VERIFICACION DEL SERVIDOR VOCALIS AI")
    print("=" * 50)

    tests = [
        test_imports(),
        test_env_file(),
        test_main_module()
    ]

    print("\n" + "=" * 50)
    if all(tests):
        print("[OK] TODAS LAS VERIFICACIONES EXITOSAS")
        print("\nPuedes iniciar el servidor con:")
        print("  uvicorn main:app --reload --port 8000")
        print("\nO en produccion:")
        print("  uvicorn main:app --host 0.0.0.0 --port 8000")
        return 0
    else:
        print("[ERROR] ALGUNAS VERIFICACIONES FALLARON")
        print("\nRevisa los errores arriba y corrige antes de desplegar.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
