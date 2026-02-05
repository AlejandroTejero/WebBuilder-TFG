"""
Tests mejorados para WebBuilder.utils.normalizer

Estos tests validan:
- Normalización de items a formato estándar
- Fallbacks inteligentes para campos faltantes
- Manejo de paths dotted (a.b.c)
- Detección de URLs en campos
- Truncado de textos largos
- Extracción de colecciones principales
"""
from django.test import SimpleTestCase
from WebBuilder.utils.normalizer import (
    normalize_items,
    _to_text,
    _get_nested,
    _looks_like_url,
    _pick_text,
    _pick_url,
    _extract_main_items,
)


class ToTextTests(SimpleTestCase):
    """Tests para conversión de valores a texto."""

    def test_string_returned_as_is(self):
        """Strings deben retornarse sin cambios (con truncado si aplica)."""
        result = _to_text("Hello World")
        self.assertEqual(result, "Hello World")

    def test_none_returns_empty_string(self):
        """None debe retornar string vacío."""
        result = _to_text(None)
        self.assertEqual(result, "")

    def test_numbers_converted_to_string(self):
        """Números deben convertirse a string."""
        self.assertEqual(_to_text(42), "42")
        self.assertEqual(_to_text(3.14), "3.14")
        self.assertEqual(_to_text(True), "True")

    def test_dict_serialized_as_json(self):
        """Dicts deben serializarse como JSON."""
        data = {"key": "value", "num": 123}
        result = _to_text(data)

        self.assertIn("key", result)
        self.assertIn("value", result)

    def test_list_serialized_as_json(self):
        """Listas deben serializarse como JSON."""
        data = [1, 2, 3]
        result = _to_text(data)

        self.assertIn("1", result)
        self.assertIn("2", result)

    def test_long_text_truncated(self):
        """Textos largos deben truncarse."""
        long_text = "A" * 1000
        result = _to_text(long_text, max_len=100)

        self.assertLessEqual(len(result), 101)  # 100 + "…"
        self.assertTrue(result.endswith("…"))

    def test_truncate_preserves_short_text(self):
        """Textos cortos no deben truncarse."""
        short_text = "Short"
        result = _to_text(short_text, max_len=100)

        self.assertEqual(result, short_text)


class GetNestedTests(SimpleTestCase):
    """Tests para obtención de valores anidados."""

    def test_simple_key_access(self):
        """Debe obtener valores por key simple."""
        item = {"name": "John", "age": 30}
        result = _get_nested(item, "name")

        self.assertEqual(result, "John")

    def test_dotted_path_access(self):
        """Debe soportar paths con puntos (a.b.c)."""
        item = {"user": {"profile": {"name": "John"}}}
        result = _get_nested(item, "user.profile.name")

        self.assertEqual(result, "John")

    def test_missing_key_returns_none(self):
        """Key inexistente debe retornar None."""
        item = {"name": "John"}
        result = _get_nested(item, "age")

        self.assertIsNone(result)

    def test_invalid_path_returns_none(self):
        """Path inválido (intermedio no es dict) debe retornar None."""
        item = {"user": "not_a_dict"}
        result = _get_nested(item, "user.profile.name")

        self.assertIsNone(result)

    def test_empty_key_returns_none(self):
        """Key vacía debe retornar None."""
        item = {"name": "John"}
        result = _get_nested(item, "")

        self.assertIsNone(result)

    def test_non_dict_item_returns_none(self):
        """Si item no es dict, debe retornar None."""
        result = _get_nested("not a dict", "key")

        self.assertIsNone(result)


class LooksLikeUrlTests(SimpleTestCase):
    """Tests para detección de URLs."""

    def test_http_url_detected(self):
        """URLs con http:// deben ser detectadas."""
        self.assertTrue(_looks_like_url("http://example.com"))

    def test_https_url_detected(self):
        """URLs con https:// deben ser detectadas."""
        self.assertTrue(_looks_like_url("https://example.com"))

    def test_non_url_not_detected(self):
        """Texto sin protocolo no es URL."""
        self.assertFalse(_looks_like_url("example.com"))
        self.assertFalse(_looks_like_url("just text"))

    def test_empty_string_not_url(self):
        """String vacío no es URL."""
        self.assertFalse(_looks_like_url(""))

    def test_url_with_whitespace(self):
        """URL con espacios al inicio/fin debe detectarse."""
        self.assertTrue(_looks_like_url("  https://example.com  "))


class PickTextTests(SimpleTestCase):
    """Tests para selección de texto desde múltiples keys."""

    def test_picks_first_non_empty(self):
        """Debe elegir el primer valor no vacío."""
        item = {"title": "", "headline": "Main Title", "name": "Alt Title"}
        result = _pick_text(item, ["title", "headline", "name"])

        self.assertEqual(result, "Main Title")

    def test_returns_empty_if_all_empty(self):
        """Debe retornar vacío si todas las keys están vacías."""
        item = {"title": "", "headline": ""}
        result = _pick_text(item, ["title", "headline", "name"])

        self.assertEqual(result, "")

    def test_respects_key_order(self):
        """Debe respetar el orden de prioridad de las keys."""
        item = {"name": "Name", "title": "Title"}
        result = _pick_text(item, ["title", "name"])

        self.assertEqual(result, "Title")

    def test_handles_missing_keys(self):
        """Debe manejar keys que no existen en el item."""
        item = {"name": "John"}
        result = _pick_text(item, ["title", "headline", "name"])

        self.assertEqual(result, "John")


class PickUrlTests(SimpleTestCase):
    """Tests para selección de URLs desde múltiples keys."""

    def test_picks_valid_url(self):
        """Debe elegir la primera URL válida."""
        item = {
            "link": "not a url",
            "url": "https://example.com/page",
            "href": "https://backup.com",
        }
        result = _pick_url(item, ["link", "url", "href"])

        self.assertEqual(result, "https://example.com/page")

    def test_extracts_first_token_from_space_separated(self):
        """Debe extraer el primer token si hay espacios."""
        item = {"url": "https://example.com/image.jpg extra text"}
        result = _pick_url(item, ["url"])

        self.assertEqual(result, "https://example.com/image.jpg")

    def test_returns_empty_if_no_valid_url(self):
        """Debe retornar vacío si no hay URLs válidas."""
        item = {"link": "not a url", "url": "also not"}
        result = _pick_url(item, ["link", "url"])

        self.assertEqual(result, "")

    def test_skips_empty_values(self):
        """Debe saltar valores vacíos o None."""
        item = {"link": "", "url": None, "href": "https://example.com"}
        result = _pick_url(item, ["link", "url", "href"])

        self.assertEqual(result, "https://example.com")


class ExtractMainItemsTests(SimpleTestCase):
    """Tests para extracción de la colección principal."""

    def test_extracts_root_list(self):
        """Debe extraer lista en la raíz."""
        parsed = [{"id": 1}, {"id": 2}]
        analysis = {"main_collection": {"path": []}}

        items = _extract_main_items(parsed, analysis)

        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]["id"], 1)

    def test_extracts_nested_list(self):
        """Debe extraer lista anidada según el path."""
        parsed = {"data": {"results": [{"id": 1}, {"id": 2}, {"id": 3}]}}
        analysis = {"main_collection": {"path": ["data", "results"]}}

        items = _extract_main_items(parsed, analysis)

        self.assertEqual(len(items), 3)

    def test_returns_empty_if_path_none(self):
        """Debe retornar lista vacía si no hay path."""
        parsed = {"data": []}
        analysis = {"main_collection": {"path": None}}

        items = _extract_main_items(parsed, analysis)

        self.assertEqual(items, [])

    def test_returns_empty_if_not_a_list(self):
        """Debe retornar vacío si el nodo final no es lista."""
        parsed = {"data": {"items": "not a list"}}
        analysis = {"main_collection": {"path": ["data", "items"]}}

        items = _extract_main_items(parsed, analysis)

        self.assertEqual(items, [])

    def test_filters_non_dict_items(self):
        """Debe filtrar elementos que no sean dicts."""
        parsed = [{"id": 1}, "not a dict", {"id": 2}, None, {"id": 3}]
        analysis = {"main_collection": {"path": []}}

        items = _extract_main_items(parsed, analysis)

        self.assertEqual(len(items), 3)
        for item in items:
            self.assertIsInstance(item, dict)


class NormalizeItemsTests(SimpleTestCase):
    """Tests de integración para normalización completa."""

    def test_basic_normalization(self):
        """Debe normalizar items básicos correctamente."""
        parsed = [
            {"id": 1, "title": "Article A", "body": "Content A"},
            {"id": 2, "title": "Article B", "body": "Content B"},
        ]
        analysis = {"main_collection": {"path": []}}
        mapping = {"title": "title", "description": "body"}

        items = normalize_items(parsed, analysis, mapping, limit=10)

        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]["title"], "Article A")
        self.assertEqual(items[0]["description"], "Content A")
        self.assertEqual(items[1]["title"], "Article B")

    def test_includes_raw_data(self):
        """Cada item normalizado debe incluir el item original en 'raw'."""
        parsed = [{"id": 1, "title": "Test"}]
        analysis = {"main_collection": {"path": []}}
        mapping = {"title": "title"}

        items = normalize_items(parsed, analysis, mapping)

        self.assertIn("raw", items[0])
        self.assertEqual(items[0]["raw"]["id"], 1)

    def test_title_fallback_to_id(self):
        """Si falta title, debe usar id como fallback."""
        parsed = [{"id": 123, "body": "No title"}]
        analysis = {"main_collection": {"path": []}}
        mapping = {"description": "body"}  # sin mapear title

        items = normalize_items(parsed, analysis, mapping)

        # Debe usar el id como fallback
        self.assertEqual(items[0]["title"], "123")

    def test_title_fallback_to_item_number(self):
        """Si no hay id ni title, debe generar 'Item #N'."""
        parsed = [{"body": "No title or id"}, {"body": "Another"}]
        analysis = {"main_collection": {"path": []}}
        mapping = {}

        items = normalize_items(parsed, analysis, mapping)

        self.assertEqual(items[0]["title"], "Item #1")
        self.assertEqual(items[1]["title"], "Item #2")

    def test_respects_limit(self):
        """Debe respetar el límite de items."""
        parsed = [{"id": i} for i in range(100)]
        analysis = {"main_collection": {"path": []}}
        mapping = {}

        items = normalize_items(parsed, analysis, mapping, limit=5)

        self.assertEqual(len(items), 5)

    def test_default_limit_is_20(self):
        """Límite por defecto debe ser 20."""
        parsed = [{"id": i} for i in range(50)]
        analysis = {"main_collection": {"path": []}}
        mapping = {}

        items = normalize_items(parsed, analysis, mapping)

        self.assertEqual(len(items), 20)

    def test_fallback_candidates_work(self):
        """Debe usar fallbacks cuando el mapping no cubre todos los campos."""
        parsed = [
            {
                "headline": "Main",  # no hay "title"
                "summary": "Summary",  # no hay "description"
                "image_url": "https://img.com/1.jpg",
                "permalink": "https://example.com",
            }
        ]
        analysis = {"main_collection": {"path": []}}
        mapping = {}  # sin mapping explícito

        items = normalize_items(parsed, analysis, mapping)

        # Debe encontrar los campos con fallbacks
        self.assertEqual(items[0]["title"], "Main")
        self.assertEqual(items[0]["description"], "Summary")
        self.assertEqual(items[0]["image"], "https://img.com/1.jpg")
        self.assertEqual(items[0]["link"], "https://example.com")

    def test_explicit_mapping_takes_priority(self):
        """Mapping explícito debe tener prioridad sobre fallbacks."""
        parsed = [
            {
                "custom_title": "Custom",
                "title": "Default",
                "custom_desc": "Custom desc",
            }
        ]
        analysis = {"main_collection": {"path": []}}
        mapping = {"title": "custom_title", "description": "custom_desc"}

        items = normalize_items(parsed, analysis, mapping)

        self.assertEqual(items[0]["title"], "Custom")
        self.assertEqual(items[0]["description"], "Custom desc")

    def test_handles_nested_collection(self):
        """Debe manejar colecciones anidadas correctamente."""
        parsed = {"response": {"data": [{"title": "A"}, {"title": "B"}]}}
        analysis = {"main_collection": {"path": ["response", "data"]}}
        mapping = {"title": "title"}

        items = normalize_items(parsed, analysis, mapping)

        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]["title"], "A")

    def test_dotted_path_in_mapping(self):
        """Debe soportar paths con puntos en el mapping."""
        parsed = [{"meta": {"title": "Nested Title"}, "id": 1}]
        analysis = {"main_collection": {"path": []}}
        mapping = {"title": "meta.title"}

        items = normalize_items(parsed, analysis, mapping)

        self.assertEqual(items[0]["title"], "Nested Title")

    def test_empty_fields_when_no_data(self):
        """Campos sin datos deben ser strings vacíos."""
        parsed = [{"id": 1}]  # sin title, description, etc.
        analysis = {"main_collection": {"path": []}}
        mapping = {}

        items = normalize_items(parsed, analysis, mapping)

        # title debe tener fallback, pero otros campos vacíos
        self.assertEqual(items[0]["description"], "")
        self.assertEqual(items[0]["image"], "")
        self.assertEqual(items[0]["link"], "")

    def test_url_detection_in_image_field(self):
        """Debe detectar URLs en campos de imagen."""
        parsed = [{"img": "https://example.com/photo.jpg"}]
        analysis = {"main_collection": {"path": []}}
        mapping = {"image": "img"}

        items = normalize_items(parsed, analysis, mapping)

        self.assertEqual(items[0]["image"], "https://example.com/photo.jpg")

    def test_non_url_in_image_field_ignored(self):
        """Valores que no son URLs en campos de imagen deben ignorarse."""
        parsed = [{"img": "not a url"}]
        analysis = {"main_collection": {"path": []}}
        mapping = {"image": "img"}

        items = normalize_items(parsed, analysis, mapping)

        self.assertEqual(items[0]["image"], "")

    def test_truncates_long_descriptions(self):
        """Descripciones largas deben truncarse."""
        long_text = "A" * 1000
        parsed = [{"title": "Test", "body": long_text}]
        analysis = {"main_collection": {"path": []}}
        mapping = {"title": "title", "description": "body"}

        items = normalize_items(parsed, analysis, mapping)

        # Debe estar truncado (520 chars max según código)
        self.assertLessEqual(len(items[0]["description"]), 521)
        self.assertTrue(items[0]["description"].endswith("…"))

    def test_empty_collection_returns_empty_list(self):
        """Colección vacía debe retornar lista vacía."""
        parsed = []
        analysis = {"main_collection": {"path": []}}
        mapping = {}

        items = normalize_items(parsed, analysis, mapping)

        self.assertEqual(items, [])

    def test_handles_mixed_item_quality(self):
        """Debe manejar items con diferentes niveles de completitud."""
        parsed = [
            {"id": 1, "title": "Complete", "description": "Full", "url": "http://1.com"},
            {"id": 2, "title": "Partial"},  # solo title
            {"id": 3},  # solo id
        ]
        analysis = {"main_collection": {"path": []}}
        mapping = {"title": "title", "description": "description", "link": "url"}

        items = normalize_items(parsed, analysis, mapping)

        self.assertEqual(len(items), 3)
        self.assertEqual(items[0]["title"], "Complete")
        self.assertEqual(items[1]["title"], "Partial")
        self.assertEqual(items[1]["description"], "")
        self.assertEqual(items[2]["title"], "3")  # fallback a id
