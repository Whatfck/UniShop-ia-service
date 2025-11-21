"""
Módulo de clasificación semántica para el servicio de IA de UniShop.
Utiliza embeddings para clasificar consultas y productos de manera inteligente.
"""

import logging
from typing import List, Dict, Any, Tuple, Optional
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    SEMANTIC_AVAILABLE = True
except ImportError:
    SEMANTIC_AVAILABLE = False
    logging.warning("sentence-transformers no disponible. Usando solo sistema basado en reglas.")

logger = logging.getLogger(__name__)

class SemanticClassifier:
    """
    Clasificador semántico que combina embeddings con reglas para mejor precisión.
    """

    def __init__(self):
        self.model = None
        self.category_embeddings = {}
        # Categorías académicas específicas de la UCC - Campus Pasto
        self.academic_categories = {
            "ingenieria_software": [
                "ingeniería de software", "desarrollo de software", "programación", "algoritmos",
                "estructuras de datos", "bases de datos", "sistemas operativos", "redes",
                "seguridad informática", "inteligencia artificial", "machine learning",
                "python", "java", "javascript", "c++", "desarrollo web", "desarrollo móvil",
                "devops", "cloud computing", "álgebra lineal", "cálculo integral",
                "física mecánica", "ingeniería de requisitos", "aspectos administrativos",
                "clean code", "design patterns", "introduction to algorithms"
            ],
            "enfermeria": [
                "enfermería", "cuidados de enfermería", "historia del cuidado", "sociología del cuidado",
                "antropología del cuidado", "sistemas de soporte", "biogenética", "procesos bioquímicos",
                "farmacocinética", "farmacodinamia", "cuidados al adulto", "vigilancia epidemiológica",
                "gerencia del cuidado", "fundamentos de enfermería", "farmacología en enfermería",
                "semiología médica", "bioquímica médica", "microbiología médica", "psicología en enfermería"
            ],
            "medicina": [
                "medicina", "semiología clínica", "ayudas diagnósticas", "deontología médica",
                "investigación médica", "inglés médico", "harrison", "guyton", "fisiología médica",
                "patología general", "robbins", "semiología médica", "farmacología básica",
                "katzung", "medicina interna", "pediatría", "cirugía", "ginecología"
            ],
            "odontologia": [
                "odontología", "salud oral", "cirugía maxilofacial", "promoción de salud",
                "prevención en salud", "patología oral", "bases quirúrgicas", "cariología",
                "semiología", "farmacoterapia odontológica", "urgencias odontológicas",
                "patología oral y maxilofacial", "nevilla", "periodontología", "carranza",
                "endodoncia", "ingle", "ortodoncia", "proffit", "cirugía oral"
            ],
            "derecho": [
                "derecho", "teoría del estado", "derechos humanos", "DIH", "constitución",
                "derecho civil", "derecho penal", "derecho procesal", "derecho laboral",
                "seguridad social", "derecho administrativo", "derecho comercial",
                "consultorio jurídico", "teoría del estado", "kelsen", "derecho constitucional",
                "aragón", "derecho penal", "zaffaroni", "derecho civil", "ospina",
                "derecho procesal", "palacio", "derecho internacional", "remiro"
            ],
            "matematicas": [
                "matemáticas", "cálculo", "álgebra", "geometría", "estadística", "probabilidad",
                "álgebra lineal", "cálculo integral", "física mecánica"
            ],
            "administracion": [
                "administración", "contabilidad", "finanzas", "marketing", "economía",
                "gestión empresarial", "emprendimiento", "recursos humanos"
            ]
        }

        # Escenarios específicos de estudiantes UCC
        self.student_scenarios = {
            "pregrado_inicio": ["primer semestre", "inicio de carrera", "principiante", "básico"],
            "práctica_laboratorio": ["práctica", "laboratorio", "experimentos", "práctica clínica"],
            "investigación": ["tesis", "investigación", "proyecto de grado", "monografía"],
            "profesionalización": ["empleo", "práctica profesional", "pasantía", "empleabilidad"],
            "especialización": ["especialización", "maestría", "posgrado", "doctorado"]
        }

        if SEMANTIC_AVAILABLE:
            try:
                # Modelo ligero optimizado para CPU
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                self._initialize_category_embeddings()
                logger.info("Clasificador semántico inicializado correctamente")
            except Exception as e:
                logger.error(f"Error inicializando modelo semántico: {e}")
                # Desactivar funcionalidad semántica si hay error
                self.model = None
        else:
            logger.info("Usando solo clasificación basada en reglas")

    def _initialize_category_embeddings(self):
        """Inicializa los embeddings de referencia para cada categoría académica."""
        if not self.model:
            return

        for category, keywords in self.academic_categories.items():
            # Crear un texto representativo de la categoría
            category_text = f"{category} {' '.join(keywords)}"
            self.category_embeddings[category] = self.model.encode(category_text)
            logger.debug(f"Embedding creado para categoría: {category}")

    def classify_academic_query(self, query: str, threshold: float = 0.3) -> Tuple[Optional[str], float]:
        """
        Clasifica una consulta académica usando similitud semántica.

        Args:
            query: La consulta del usuario
            threshold: Umbral mínimo de similitud (0-1)

        Returns:
            Tupla de (categoría, confianza) o (None, 0) si no clasifica
        """
        if not SEMANTIC_AVAILABLE or not self.model:
            return self._rule_based_classification(query)

        try:
            query_embedding = self.model.encode(query)

            best_category = None
            best_similarity = 0.0

            for category, category_embedding in self.category_embeddings.items():
                similarity = cosine_similarity(
                    [query_embedding],
                    [category_embedding]
                )[0][0]

                if similarity > best_similarity:
                    best_similarity = similarity
                    best_category = category

            if best_similarity >= threshold:
                return best_category, best_similarity
            else:
                return None, best_similarity

        except Exception as e:
            logger.error(f"Error en clasificación semántica: {e}")
            return self._rule_based_classification(query)

    def detect_student_scenario(self, query: str) -> Optional[str]:
        """
        Detecta el escenario académico del estudiante (inicio carrera, práctica, investigación, etc.)

        Args:
            query: La consulta del usuario

        Returns:
            Escenario detectado o None
        """
        query_lower = query.lower()

        for scenario, keywords in self.student_scenarios.items():
            if any(keyword in query_lower for keyword in keywords):
                return scenario

        return None

    def get_contextual_recommendations(self, category: str, scenario: Optional[str] = None) -> Dict[str, Any]:
        """
        Genera recomendaciones contextuales basadas en la categoría y escenario del estudiante.

        Args:
            category: Categoría académica detectada
            scenario: Escenario del estudiante (opcional)

        Returns:
            Diccionario con recomendaciones contextuales
        """
        recommendations = {
            "category": category,
            "scenario": scenario,
            "tips": [],
            "related_subjects": [],
            "typical_products": []
        }

        # Recomendaciones específicas por categoría y escenario
        if category == "ingenieria_software":
            recommendations["related_subjects"] = ["Algoritmos", "Estructuras de Datos", "Bases de Datos"]
            recommendations["typical_products"] = ["Libros de programación", "Licencias de software", "Equipos de desarrollo"]

            if scenario == "pregrado_inicio":
                recommendations["tips"] = [
                    "Comienza con fundamentos de programación",
                    "No te preocupes si eres principiante, todos empezamos así",
                    "Busca libros como 'Clean Code' para buenas prácticas"
                ]
            elif scenario == "práctica_laboratorio":
                recommendations["tips"] = [
                    "Necesitarás una buena laptop para desarrollo",
                    "Considera equipos como Raspberry Pi para IoT",
                    "Busca licencias de IDEs y software de desarrollo"
                ]

        elif category == "enfermeria":
            recommendations["related_subjects"] = ["Cuidados Básicos", "Farmacología", "Semiología"]
            recommendations["typical_products"] = ["Estetoscopios", "Esfigmomanómetros", "Kits de venopunción"]

            if scenario == "práctica_laboratorio":
                recommendations["tips"] = [
                    "Busca maniquíes de práctica para simulación",
                    "Los equipos de monitoreo vital son esenciales",
                    "Considera libros de farmacología para enfermería"
                ]

        elif category == "medicina":
            recommendations["related_subjects"] = ["Semiología", "Fisiología", "Farmacología"]
            recommendations["typical_products"] = ["Estetoscopios", "Otoscopios", "Kits de diagnóstico"]

            if scenario == "investigación":
                recommendations["tips"] = [
                    "Busca libros de investigación médica",
                    "Considera equipos para ayudas diagnósticas",
                    "Material de inglés médico puede ser útil"
                ]

        elif category == "odontologia":
            recommendations["related_subjects"] = ["Patología Oral", "Cirugía", "Periodoncia"]
            recommendations["typical_products"] = ["Equipos odontológicos", "Instrumental quirúrgico", "Modelos anatómicos"]

            if scenario == "práctica_laboratorio":
                recommendations["tips"] = [
                    "Busca turbinas y micromotores para práctica",
                    "Los esterilizadores son indispensables",
                    "Considera software de planificación dental"
                ]

        elif category == "derecho":
            recommendations["related_subjects"] = ["Constitucional", "Penal", "Civil"]
            recommendations["typical_products"] = ["Códigos civiles", "Gacetas judiciales", "Software jurídico"]

            if scenario == "profesionalización":
                recommendations["tips"] = [
                    "Busca oportunidades de consultorio jurídico",
                    "Considera equipos de audio para grabaciones",
                    "Bases de datos legales son muy útiles"
                ]

        return recommendations

    def _rule_based_classification(self, query: str) -> Tuple[Optional[str], float]:
        """Clasificación basada en reglas como fallback."""
        query_lower = query.lower()

        # Reglas específicas para cada categoría
        rules = {
            "medicina": ["medicina", "anatomía", "fisiología", "patología", "cardiología",
                        "enfermería", "clínica", "hospital", "paciente", "diagnóstico"],
            "ingenieria_software": ["programación", "python", "java", "javascript", "algoritmo",
                                  "software", "desarrollo", "código", "programar"],
            "matematicas": ["cálculo", "álgebra", "geometría", "ecuaciones", "matemáticas"],
            "derecho": ["derecho", "jurídico", "ley", "constitucional", "penal", "civil"],
            "administracion": ["administración", "contabilidad", "finanzas", "marketing", "empresa"]
        }

        for category, keywords in rules.items():
            if any(keyword in query_lower for keyword in keywords):
                return category, 0.8  # Confianza alta para coincidencias exactas

        return None, 0.0

    def find_books_by_semantic_category(self, books: List[Dict[str, Any]],
                                       target_category: str,
                                       threshold: float = 0.25) -> List[Dict[str, Any]]:
        """
        Encuentra libros que pertenezcan a una categoría académica usando similitud semántica.

        Args:
            books: Lista de libros con título y descripción
            target_category: Categoría objetivo (ej: "medicina")
            threshold: Umbral de similitud mínimo

        Returns:
            Lista de libros que coinciden con la categoría
        """
        if not SEMANTIC_AVAILABLE or not self.model:
            return self._rule_based_book_filter(books, target_category)

        if target_category not in self.category_embeddings:
            logger.warning(f"Categoría no encontrada: {target_category}")
            return []

        try:
            matching_books = []

            for book in books:
                # Combinar título y descripción para mejor contexto
                book_text = f"{book.get('name', '')} {book.get('description', '')}"

                if not book_text.strip():
                    continue

                book_embedding = self.model.encode(book_text)
                category_embedding = self.category_embeddings[target_category]

                similarity = cosine_similarity(
                    [book_embedding],
                    [category_embedding]
                )[0][0]

                if similarity >= threshold:
                    book_with_score = book.copy()
                    book_with_score['_semantic_score'] = similarity
                    matching_books.append(book_with_score)

            # Ordenar por similitud semántica
            matching_books.sort(key=lambda x: x.get('_semantic_score', 0), reverse=True)

            # Remover el score antes de devolver
            for book in matching_books:
                book.pop('_semantic_score', None)

            return matching_books[:5]  # Máximo 5 resultados

        except Exception as e:
            logger.error(f"Error en búsqueda semántica de libros: {e}")
            return self._rule_based_book_filter(books, target_category)

    def _rule_based_book_filter(self, books: List[Dict[str, Any]], target_category: str) -> List[Dict[str, Any]]:
        """Filtro de libros basado en reglas como fallback."""
        if target_category not in self.academic_categories:
            return []

        keywords = self.academic_categories[target_category]
        matching_books = []

        for book in books:
            book_text = f"{book.get('name', '')} {book.get('description', '')}".lower()

            if any(keyword.lower() in book_text for keyword in keywords):
                matching_books.append(book)

        return matching_books[:5]

# Instancia global del clasificador
semantic_classifier = SemanticClassifier()