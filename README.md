# 🤖 UniShop IA Service

Servicio de Inteligencia Artificial para UniShop, desarrollado con FastAPI (Python) para proporcionar funcionalidades de IA ligeras y locales.

## 🚀 Tecnologías

- **Framework:** FastAPI
- **Lenguaje:** Python 3.11
- **Servidor:** Uvicorn ASGI
- **Contenedor:** Docker
- **Dependencias:** Scikit-learn, Pandas, NumPy

## 📋 Características

- ✅ API REST asíncrona con FastAPI
- ✅ Recomendaciones simples basadas en reglas
- ✅ Chatbot básico con respuestas predefinidas
- ✅ Health checks automáticos
- ✅ CORS habilitado
- ✅ Logging estructurado
- ✅ Preparado para modelos de ML

## 🎯 Funcionalidades

### Recomendaciones
- **Por categoría:** Productos relacionados en misma categoría
- **Por popularidad:** Productos más vistos/contactados
- **Algoritmo:** Reglas simples, sin modelos complejos inicialmente

### Chatbot
- **Respuestas predefinidas:** FAQ sobre uso de la plataforma
- **Lógica basada en reglas:** Matching de patrones en mensajes
- **Sin LLM:** Enfoque ligero y privado

## 🔧 Configuración

### Variables de Entorno

Crear archivo `.env` basado en `.env.example` (si existe):

```bash
# Puerto del servicio
PORT=8000

# URL del backend (para comunicación interna)
BACKEND_URL=http://backend:8080

# Configuración de logging
LOG_LEVEL=INFO
```

### Desarrollo Local

#### Opción 1: Con Docker (Recomendado)
```bash
# Desde raíz del proyecto
docker-compose up --build ia-service
```

#### Opción 2: Desarrollo Nativo
```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## 🌐 Endpoints

### Health Check
- `GET /health` - Estado del servicio

### Recomendaciones
- `GET /api/v1/recommendations/{productId}` - Productos recomendados
- `GET /api/v1/recommendations/popular` - Productos populares

### Chatbot
- `POST /api/v1/chatbot/message` - Enviar mensaje al chatbot

### Información
- `GET /` - Información del servicio

## 📖 Documentación API

### Swagger UI
Cuando el servicio esté corriendo:
- **Local:** http://localhost:8000/docs
- **Docker:** http://localhost:8000/docs

### ReDoc
- **Alternativo:** http://localhost:8000/redoc

### OpenAPI Spec
- **JSON:** http://localhost:8000/openapi.json

## 🏗️ Arquitectura

```
ia-service/
├── src/
│   ├── main.py              # Aplicación FastAPI principal
│   ├── __init__.py          # Módulo Python
│   └── [futuros módulos]    # Lógica de IA separada
├── requirements.txt         # Dependencias Python
├── Dockerfile              # Contenedor Docker
└── README.md              # Esta documentación
```

### Estructura Futura
```
ia-service/
├── src/
│   ├── main.py
│   ├── recommendations.py   # Lógica de recomendaciones
│   ├── chatbot.py          # Lógica del chatbot
│   ├── models.py           # Modelos de datos
│   └── utils.py            # Utilidades
├── tests/                  # Tests unitarios
├── data/                   # Datos de entrenamiento/modelos
└── scripts/                # Scripts de entrenamiento
```

## 🔧 Dependencias

### Core
- `fastapi` - Framework web asíncrono
- `uvicorn` - Servidor ASGI
- `pydantic` - Validación de datos

### IA/ML
- `scikit-learn` - Algoritmos de ML
- `pandas` - Manipulación de datos
- `numpy` - Computación numérica

### Utilidades
- `httpx` - Cliente HTTP asíncrono
- `python-multipart` - Manejo de formularios

## 🧪 Testing

```bash
# Instalar dependencias de desarrollo
pip install pytest httpx

# Ejecutar tests
pytest

# Con cobertura
pytest --cov=src --cov-report=html
```

### Tests de Ejemplo
```python
# tests/test_main.py
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "ia-service"}
```

## 📊 Monitoreo

### Health Checks
- **Endpoint:** `/health`
- **Docker:** HEALTHCHECK integrado
- **Métricas:** Preparado para Prometheus

### Logs
- **Formato:** JSON estructurado
- **Niveles:** DEBUG, INFO, WARNING, ERROR
- **Salida:** Consola + archivo (configurable)

## 🚀 Despliegue

### Producción
```bash
# Build imagen
docker build -t unishop-ia-service .

# Ejecutar contenedor
docker run -p 8000:8000 unishop-ia-service
```

### Docker Compose
```yaml
ia-service:
  build: ./ia-service
  ports:
    - "8000:8000"
  environment:
    - BACKEND_URL=http://backend:8080
```

## 🔒 Seguridad

- **CORS:** Habilitado para desarrollo
- **Rate Limiting:** Preparado para implementación
- **Validación:** Pydantic models
- **Logs Seguros:** Sin exposición de datos sensibles

## 📈 Escalabilidad

### Optimizaciones Futuras
- **Modelos ligeros:** Mantener enfoque en CPU básica
- **Cache:** Redis para recomendaciones frecuentes
- **Async:** Procesamiento asíncrono para operaciones pesadas
- **Microservicios:** Separar recomendaciones y chatbot si crecen

### Recursos
- **CPU:** Algoritmos optimizados para CPU
- **Memoria:** Modelos pequeños (< 500MB)
- **Almacenamiento:** Datos locales, sin dependencias externas

## 🎯 Roadmap

### Fase 1 (Actual)
- ✅ API básica FastAPI
- ✅ Health checks
- ✅ Estructura de proyecto
- 🔄 Recomendaciones por reglas simples

### Fase 2 (Próxima)
- [ ] Chatbot con respuestas predefinidas
- [ ] Sistema de feedback para recomendaciones
- [ ] Tests unitarios completos
- [ ] Documentación API completa

### Fase 3 (Futuro)
- [ ] Modelos de ML más avanzados
- [ ] Fine-tuning con datos reales
- [ ] A/B testing de recomendaciones
- [ ] Integración con modelos de lenguaje ligeros

## 👥 Contribución

1. Seguir estructura de archivos
2. Agregar tests para nuevas funcionalidades
3. Documentar endpoints en OpenAPI
4. Mantener compatibilidad con versiones anteriores

## 📞 Soporte

Para issues relacionados con IA, usar el repositorio correspondiente o contactar al equipo de ML.