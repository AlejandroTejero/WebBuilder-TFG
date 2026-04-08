# Catálogo de modelos LLM disponibles en WebBuilder
# Cada entrada tiene: id, nombre, proveedor, base_url, descripción, pros y contras.

LLM_CATALOG = [
    {
        "id": "meta-llama/llama-4-scout-17b-16e-instruct",
        "name": "Llama 4 Scout",
        "provider": "Groq",
        "base_url": "https://api.groq.com/openai/v1",
        "description": "Modelo rápido y eficiente de Meta, ideal para generación de código estructurado.",
        "pros": "Muy rápido, buena calidad de código, gratuito.",
        "cons": "Contexto limitado en respuestas muy largas.",
    },
    {
        "id": "meta-llama/llama-3.3-70b-instruct:free",
        "name": "Llama 3.3 70B",
        "provider": "OpenRouter",
        "base_url": "https://openrouter.ai/api/v1",
        "description": "Versión grande de Llama 3, más potente para webs complejas.",
        "pros": "Mayor capacidad de razonamiento, gratis en OpenRouter.",
        "cons": "Más lento que Scout.",
    },
    {
        "id": "qwen/qwen3-coder:free",
        "name": "Qwen3 Coder",
        "provider": "OpenRouter",
        "base_url": "https://openrouter.ai/api/v1",
        "description": "Modelo especializado en código de Alibaba, muy bueno generando HTML/CSS limpio.",
        "pros": "Optimizado para código, genera estructuras limpias.",
        "cons": "Puede ser más lento, gratuito con límites.",
    },
]