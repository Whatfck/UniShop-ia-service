from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Unishop IA Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ia-service"}

@app.get("/")
async def root():
    return {"message": "Unishop IA Service", "status": "running"}

# TODO: Implementar endpoints de IA
# - Recomendaciones
# - Chatbot
# - Análisis de productos