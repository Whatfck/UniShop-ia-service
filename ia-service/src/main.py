import os
import logging
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx

# Importar clasificador semántico
try:
    from .semantic_classifier import semantic_classifier
except ImportError:
    # Fallback para desarrollo
    from semantic_classifier import semantic_classifier

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Unishop IA Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8080")

async def get_products_from_backend() -> List[Dict[str, Any]]:
    """Obtiene la lista de productos del backend"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{BACKEND_URL}/api/v1/products")
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error obteniendo productos: {response.status_code}")
                return []
    except Exception as e:
        logger.error(f"Error de conexión con backend: {e}")
        return []

async def get_product_from_backend(product_id: int) -> Dict[str, Any]:
    """Obtiene un producto específico del backend"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{BACKEND_URL}/api/v1/products/{product_id}")
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error obteniendo producto {product_id}: {response.status_code}")
                return None
    except Exception as e:
        logger.error(f"Error de conexión con backend: {e}")
        return None

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ia-service"}

@app.get("/")
async def root():
    return {"message": "Unishop IA Service", "status": "running"}

@app.get("/api/v1/recommendations/popular")
async def get_popular_recommendations() -> Dict[str, List[Dict[str, Any]]]:
    """
    Obtiene productos populares (por ahora ordenados por ID descendente como aproximación)
    """
    all_products = await get_products_from_backend()

    # Ordenar por ID descendente (productos más recientes primero)
    popular = sorted(all_products, key=lambda x: x.get("id", 0), reverse=True)[:10]

    return {"popular": popular}

@app.get("/api/v1/recommendations/{product_id}")
async def get_recommendations(product_id: int) -> Dict[str, List[Dict[str, Any]]]:
    """
    Obtiene recomendaciones de productos relacionados basadas en categoría
    """
    # Obtener el producto objetivo
    product = await get_product_from_backend(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    # Obtener todos los productos
    all_products = await get_products_from_backend()

    # Filtrar productos de la misma categoría, excluyendo el producto actual
    category = product.get("categoryName", "")
    recommendations = [
        p for p in all_products
        if p.get("categoryName", "") == category and p["id"] != product_id
    ][:5]  # Limitar a 5 recomendaciones

    return {"recommendations": recommendations}

@app.post("/api/v1/chatbot/message")
async def chatbot_message(message: Dict[str, str]) -> Dict[str, str]:
    """
    Procesa mensajes del chatbot con respuestas predefinidas basadas en reglas
    """
    user_message = message.get("message", "").lower().strip()

    # Respuestas conversacionales y contextuales para estudiantes UCC
    if any(word in user_message for word in ["hola", "hi", "hello", "saludos", "buenos", "buen", "hey", "qué", "como", "ayuda"]):
        # Respuestas más contextuales y conversacionales
        if any(word in user_message for word in ["comprar", "compra", "adquirir", "cómo compro", "como compro"]):
            response = "¡Hola! 👋 **Para comprar en UniShop:**\n\n"
            response += "1. 🔍 **Busca productos** usando la barra de búsqueda\n"
            response += "2. 🎯 **Filtra** por categoría, precio o condición\n"
            response += "3. 💬 **Contacta al vendedor** directamente por WhatsApp\n"
            response += "4. 🤝 **Coordina** entrega y pago de forma segura\n\n"
            response += "¿Qué tipo de producto buscas? *(libros, equipos, material académico...)*"

        elif any(word in user_message for word in ["libro", "libros", "texto", "material", "estudiar"]):
            response = "¡Hola! 📚 Como estudiante de la UCC, puedo ayudarte con material académico:\n\n"
            response += "• **Libros de texto** por carrera\n"
            response += "• **Material de investigación**\n"
            response += "• **Recursos académicos**\n\n"
            response += "¿Qué carrera estudias? (Ingeniería, Enfermería, Medicina, Odontología, Derecho...)\n"
            response += "O dime qué asignatura necesitas."

        elif len(user_message.split()) <= 3:  # Saludos simples
            response = "¡Hola! 👋 **Soy UniBot**, el asistente inteligente de UniShop para estudiantes de la UCC.\n\n"
            response += "Puedo ayudarte con:\n"
            response += "• 🔍 **Buscar libros** y material académico por carrera\n"
            response += "• 🛠️ **Encontrar equipos** de laboratorio y útiles\n"
            response += "• 💼 **Preparación profesional** y empleabilidad\n"
            response += "• 📱 **Navegar** y usar la plataforma UniShop\n\n"
            response += "*¿En qué te puedo ayudar hoy?*"

        else:  # Saludos con más contexto
            response = "¡Hola! 👋 ¿En qué puedo ayudarte?\n\n"
            response += "Como asistente especializado en la comunidad UCC, te ayudo con:\n"
            response += "• Material académico por carrera\n"
            response += "• Equipos para prácticas\n"
            response += "• Consejos para estudiantes\n"
            response += "• Navegación en UniShop"

    # Respuestas predefinidas basadas en palabras clave
    elif any(word in user_message for word in ["precio", "costo", "cuánto", "vale"]):
        response = "Los precios son fijados por los vendedores. Puedes contactarlos directamente a través de WhatsApp para negociar."

    elif any(word in user_message for word in ["envio", "entrega", "envío", "llegar"]):
        response = "Las entregas se coordinan directamente entre comprador y vendedor. Te recomendamos acordar el método de entrega al contactar al vendedor."

    elif any(word in user_message for word in ["cuenta", "registro", "registrar", "crear"]):
        response = "Para registrarte en UniShop, necesitas un correo institucional (@campusucc.edu.co). El registro incluye verificación de teléfono para publicar productos."

    elif any(word in user_message for word in ["contactar", "whatsapp", "contacto"]):
        response = "Puedes contactar a los vendedores directamente desde la página del producto usando el botón 'Contactar'. Se generará un mensaje automático en WhatsApp."

    elif any(word in user_message for word in ["favorito", "favoritos", "guardar"]):
        response = "Puedes guardar productos en tu lista de favoritos haciendo clic en el ícono de corazón. Los encontrarás en tu panel de usuario."

    elif any(word in user_message for word in ["publicar", "vender", "venta"]):
        response = "Para publicar un producto, ve a 'Vender' en el menú principal. Necesitas tener tu teléfono verificado y proporcionar al menos una foto del producto."

    elif any(word in user_message for word in ["buscar", "encontrar", "filtros"]):
        response = "Usa la barra de búsqueda en la página principal. Puedes filtrar por categoría, precio, condición y fecha de publicación."

    elif any(word in user_message for word in ["seguridad", "seguro", "confianza"]):
        response = "UniShop es exclusivo para la comunidad UCC. Todas las transacciones se realizan directamente entre estudiantes verificados."

    elif any(word in user_message for word in ["laboratorio", "equipo", "equipos", "instrumental", "instrumentales", "material", "materiales", "útil", "útiles"]) and any(word in user_message for word in ["práctica", "prácticas", "experimento", "experimentos", "clase", "clases", "laboratorio"]):
        # Recomendaciones de equipos por carrera
        query_lower = user_message.lower()

        if any(word in query_lower for word in ["enfermería", "enfermera", "cuidados"]):
            response = "Para estudiantes de enfermería, recomiendo buscar:\n"
            response += "• Estetoscopios Littmann\n"
            response += "• Esfigmomanómetros digitales\n"
            response += "• Termómetros profesionales\n"
            response += "• Kits de venopunción\n"
            response += "• Maniquíes de práctica\n\n"
            response += "Estos equipos son ideales para tus prácticas en el centro de simulación médica de la UCC."

        elif any(word in query_lower for word in ["medicina", "médico", "clínica"]):
            response = "Para estudiantes de medicina, considera:\n"
            response += "• Estetoscopios de calidad\n"
            response += "• Otoscopios y oftalmoscopios\n"
            response += "• Kits de diagnóstico\n"
            response += "• Maniquíes anatómicos\n"
            response += "• Microscopios\n\n"
            response += "Material esencial para tus prácticas clínicas."

        elif any(word in query_lower for word in ["odontología", "odontólogo", "dental"]):
            response = "Para estudiantes de odontología, busca:\n"
            response += "• Turbinas y micromotores\n"
            response += "• Radiográficos portátiles\n"
            response += "• Esterilizadores\n"
            response += "• Instrumental quirúrgico\n"
            response += "• Modelos anatómicos\n\n"
            response += "Equipos indispensables para la clínica odontológica de la UCC."

        elif any(word in query_lower for word in ["ingeniería", "software", "computación"]):
            response = "Para ingeniería de software, considera:\n"
            response += "• Laptops de desarrollo\n"
            response += "• Raspberry Pi para IoT\n"
            response += "• Arduino para prototipos\n"
            response += "• Licencias de software IDE\n"
            response += "• Tablets gráficas para UX/UI\n\n"
            response += "Equipos perfectos para los laboratorios de desarrollo de la UCC."

        elif any(word in query_lower for word in ["derecho", "jurídico", "abogado"]):
            response = "Para estudiantes de derecho, busca:\n"
            response += "• Código Civil y Penal colombiano\n"
            response += "• Gacetas judiciales\n"
            response += "• Software jurídico\n"
            response += "• Bases de datos legales\n"
            response += "• Equipos de audio para grabaciones\n\n"
            response += "Material esencial para el consultorio jurídico de la UCC."

        else:
            response = "Para equipos de laboratorio, especifica tu carrera. La UCC tiene diferentes especialidades:\n"
            response += "• Enfermería: Estetoscopios, tensiómetros\n"
            response += "• Medicina: Equipos de diagnóstico\n"
            response += "• Odontología: Instrumental dental\n"
            response += "• Ingeniería: Equipos de desarrollo\n"
            response += "• Derecho: Material jurídico\n\n"
            response += "¿Qué carrera estudias?"

    elif any(word in user_message for word in ["pasantía", "práctica", "empleo", "trabajo", "profesional"]):
        # Recomendaciones para empleabilidad
        response = "Para prepararte profesionalmente en la UCC:\n\n"
        response += "📚 **Material de estudio:**\n"
        response += "• Libros de tu especialidad\n"
        response += "• Material de investigación\n"
        response += "• Certificaciones profesionales\n\n"
        response += "💼 **Preparación laboral:**\n"
        response += "• Busca equipos reacondicionados\n"
        response += "• Material de segunda mano confiable\n"
        response += "• Útiles especializados por carrera\n\n"
        response += "🎯 **Oportunidades UCC:**\n"
        response += "• Consultorio jurídico (Derecho)\n"
        response += "• Clínica odontológica (Odontología)\n"
        response += "• Centro de simulación médica (Medicina/Enfermería)\n"
        response += "• Laboratorios de desarrollo (Ingeniería)\n\n"
        response += "¿En qué área te quieres especializar?"

    elif any(word in user_message for word in ["tesis", "investigación", "proyecto", "grado", "monografía"]):
        # Recomendaciones para investigación
        response = "Para tu tesis o proyecto de investigación en la UCC:\n\n"
        response += "📖 **Material académico:**\n"
        response += "• Libros especializados en tu área\n"
        response += "• Revistas científicas\n"
        response += "• Material de investigación\n\n"
        response += "🛠️ **Equipos especializados:**\n"
        response += "• Equipos de laboratorio\n"
        response += "• Software de análisis\n"
        response += "• Herramientas de investigación\n\n"
        response += "💡 **Recursos UCC:**\n"
        response += "• Centro de investigación\n"
        response += "• Biblioteca especializada\n"
        response += "• Laboratorios equipados\n\n"
        response += "¿Qué tema investigas o qué carrera estudias?"

    elif any(word in user_message for word in ["caro", "costoso", "caro", "más caro", "más costoso", "más caro", "más costoso"]):
        # Encontrar el producto más caro
        all_products = await get_products_from_backend()
        if all_products:
            most_expensive = max(all_products, key=lambda x: x.get("price", 0))
            response = f"El producto más caro disponible es '{most_expensive.get('name', 'N/A')}' con un precio de ${most_expensive.get('price', 0):,.0f}. Categoría: {most_expensive.get('categoryName', 'N/A')}."
        else:
            response = "Lo siento, no pude obtener información de los productos en este momento."

    elif any(word in user_message for word in ["barato", "barata", "económico", "económica", "más barato", "más barata", "más económico", "más económica"]):
        # Encontrar el producto más barato
        all_products = await get_products_from_backend()
        if all_products:
            # Filtrar productos con precio > 0 para evitar productos gratuitos
            valid_products = [p for p in all_products if p.get("price", 0) > 0]
            if valid_products:
                cheapest = min(valid_products, key=lambda x: x.get("price", 0))
                response = f"El producto más económico disponible es '{cheapest.get('name', 'N/A')}' con un precio de ${cheapest.get('price', 0):,.0f}. Categoría: {cheapest.get('categoryName', 'N/A')}."
            else:
                response = "No encontré productos con precios válidos en este momento."
        else:
            response = "Lo siento, no pude obtener información de los productos en este momento."

    elif any(word in user_message for word in ["libro", "libros", "texto", "manual", "aprender", "estudiar", "curso"]):
        # Búsqueda contextual inteligente de libros usando clasificación semántica
        all_products = await get_products_from_backend()
        if all_products:
            books = [p for p in all_products if p.get("categoryName", "").lower() == "libros"]

            if not books:
                response = "No encontré libros disponibles en este momento."
            else:
                # Usar clasificación semántica avanzada con contexto UCC
                category, confidence = semantic_classifier.classify_academic_query(user_message)
                scenario = semantic_classifier.detect_student_scenario(user_message)

                if category and confidence > 0.2:
                    # Búsqueda semántica por categoría detectada
                    relevant_books = semantic_classifier.find_books_by_semantic_category(books, category)

                    if relevant_books:
                        # Nombres de categorías más amigables para estudiantes UCC
                        category_names = {
                            "medicina": "medicina",
                            "enfermeria": "enfermería",
                            "odontologia": "odontología",
                            "ingenieria_software": "ingeniería de software",
                            "derecho": "derecho",
                            "matematicas": "matemáticas",
                            "administracion": "administración"
                        }

                        category_display = category_names.get(category, category)

                        # Respuesta contextual basada en escenario
                        if scenario == "pregrado_inicio":
                            intro_text = f"¡Perfecto para empezar tu carrera en {category_display}! "
                        elif scenario == "práctica_laboratorio":
                            intro_text = f"Excelente para tus prácticas de {category_display}. "
                        elif scenario == "investigación":
                            intro_text = f"Ideal para investigación en {category_display}. "
                        elif scenario == "profesionalización":
                            intro_text = f"Material profesional de {category_display}. "
                        else:
                            intro_text = f"Material académico de {category_display}. "

                        response = f"{intro_text}Encontré estos libros:\n\n"

                        for i, book in enumerate(relevant_books[:3], 1):
                            product_id = book.get('id', '')
                            product_name = book.get('name', 'N/A')
                            product_price = book.get('price', 0)
                            # Crear enlace al producto usando el formato del frontend
                            product_link = f"[{product_name}](/product/{product_id})"
                            response += f"{i}. {product_link} - **${product_price:,.0f}**\n"

                        # Recomendaciones contextuales adicionales
                        contextual_info = semantic_classifier.get_contextual_recommendations(category, scenario)
                        if contextual_info.get("tips"):
                            response += f"\n💡 **Tips para estudiantes de {category_display}:**\n"
                            for tip in contextual_info["tips"][:2]:  # Máximo 2 tips
                                response += f"• {tip}\n"

                        response += f"\n📖 **Recomendación:** Haz clic en el nombre de cualquier libro para ver más detalles y contactar al vendedor."
                    else:
                        response = f"No encontré libros específicos de {category_names.get(category, category)}, pero puedes explorar la categoría 'Libros' para más opciones."
                else:
                    # Fallback: búsqueda por palabras clave específicas con contexto UCC
                    query_lower = user_message.lower()

                    # Búsqueda específica para casos comunes en UCC
                    if any(word in query_lower for word in ["músculo", "muscular", "esquelet", "esqueleto", "ortoped", "traumatolog", "kinesiolog"]):
                        relevant_books = semantic_classifier.find_books_by_semantic_category(books, "medicina")
                        if relevant_books:
                            response = "Para estudiantes de medicina, enfermería u odontología interesados en sistema musculoesquelético:\n"
                            for i, book in enumerate(relevant_books[:3], 1):
                                response += f"{i}. '{book.get('name', 'N/A')}' - ${book.get('price', 0):,.0f}\n"
                            response += "\nEstos libros son ideales para tus prácticas en el centro de simulación médica de la UCC."
                        else:
                            response = "No encontré libros específicos sobre sistema musculoesquelético."

                    elif any(word in query_lower for word in ["python", "programacion", "desarrollo", "software", "algoritmo"]):
                        relevant_books = semantic_classifier.find_books_by_semantic_category(books, "ingenieria_software")
                        if relevant_books:
                            response = "Para estudiantes de ingeniería de software:\n"
                            for i, book in enumerate(relevant_books[:3], 1):
                                response += f"{i}. '{book.get('name', 'N/A')}' - ${book.get('price', 0):,.0f}\n"
                            response += "\nRecuerda que la UCC tiene laboratorios especializados para desarrollo de software."
                        else:
                            response = "No encontré libros específicos sobre Python o desarrollo de software."
                    else:
                        # Sugerencias contextuales para estudiantes UCC
                        response = "Como estudiante de la UCC, puedes especificar mejor qué buscas. Por ejemplo:\n"
                        response += "• 'libros de medicina' (para estudiantes de medicina)\n"
                        response += "• 'libros de enfermería' (para estudiantes de enfermería)\n"
                        response += "• 'libros de derecho' (para estudiantes de derecho)\n"
                        response += "• 'material de laboratorio' (para prácticas)\n"
                        response += "• 'equipos odontológicos' (para estudiantes de odontología)\n\n"
                        response += "¿Qué carrera estudias o qué tipo de material necesitas?"
        else:
            response = "Lo siento, no pude acceder al catálogo de libros en este momento."

    else:
        response = "Lo siento, no entendí completamente tu consulta. 🤔\n\n**Soy UniBot**, tu asistente especializado en UniShop para estudiantes de la UCC. Puedo ayudarte con:\n\n"
        response += "• 📚 **Libros y material académico** por carrera\n"
        response += "• 🔧 **Equipos de laboratorio** y útiles profesionales\n"
        response += "• 💰 **Precios, envíos** y procesos de compra\n"
        response += "• 👤 **Registro, perfiles** y uso de la plataforma\n"
        response += "• 🎓 **Consejos específicos** para estudiantes UCC\n\n"
        response += "*¿Podrías reformular tu pregunta o decirme qué necesitas?*"

    return {"response": response}