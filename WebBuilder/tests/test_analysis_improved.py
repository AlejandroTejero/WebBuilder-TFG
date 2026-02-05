"""
Tests mejorados para WebBuilder.utils.analysis

Estos tests validan:
- Detección de colecciones principales en diferentes estructuras
- Análisis de estructuras complejas (nested, raíz como lista)
- Sugerencias de campos por rol
- Manejo de casos edge (sin colección, metadata)
"""
from django.test import SimpleTestCase
from WebBuilder.utils.analysis import (
    build_analysis,
    find_main_items,
    suggest_mapping,
    get_by_path,
    ROLE_DEFS,
)


class FindMainItemsTests(SimpleTestCase):
    """Tests para la detección de la colección principal de items."""

    def test_root_list_detected(self):
        """Cuando la raíz es una lista de dicts, debe detectarla."""
        parsed = [
            {"id": 1, "title": "Item A", "description": "Desc A"},
            {"id": 2, "title": "Item B", "description": "Desc B"},
        ]
        result = find_main_items(parsed)

        self.assertTrue(result["found"])
        self.assertEqual(result["count"], 2)
        self.assertEqual(result["path"], [])
        self.assertIn("id", result["sample_keys"])
        self.assertIn("title", result["sample_keys"])

    def test_nested_collection_in_data_results(self):
        """Estructura típica de API: data.results[]"""
        parsed = {
            "status": "success",
            "data": {
                "results": [
                    {"id": 1, "name": "Product A"},
                    {"id": 2, "name": "Product B"},
                    {"id": 3, "name": "Product C"},
                ]
            },
        }
        result = find_main_items(parsed)

        self.assertTrue(result["found"])
        self.assertEqual(result["count"], 3)
        self.assertEqual(result["path"], ["data", "results"])
        self.assertIn("name", result["sample_keys"])

    def test_deeply_nested_collection(self):
        """Colección muy anidada debe ser encontrada."""
        parsed = {
            "response": {
                "body": {
                    "data": {
                        "items": [
                            {"title": "A", "url": "http://a.com"},
                            {"title": "B", "url": "http://b.com"},
                        ]
                    }
                }
            }
        }
        result = find_main_items(parsed)

        self.assertTrue(result["found"])
        self.assertEqual(result["count"], 2)
        self.assertIn("items", result["path"])

    def test_avoids_metadata_collections(self):
        """No debe elegir listas de metadata como colección principal."""
        parsed = {
            "meta": {
                "links": [{"rel": "self"}, {"rel": "next"}],  # metadata
            },
            "articles": [
                {"id": 1, "title": "Real Article"},
                {"id": 2, "title": "Another Article"},
            ],
        }
        result = find_main_items(parsed)

        self.assertTrue(result["found"])
        # Debe elegir "articles", no "links"
        self.assertEqual(result["path"], ["articles"])
        self.assertEqual(result["count"], 2)

    def test_prefers_larger_collection(self):
        """Debe elegir la colección más grande cuando hay varias."""
        parsed = {
            "small": [{"id": 1}],
            "large": [
                {"id": 1, "title": "A"},
                {"id": 2, "title": "B"},
                {"id": 3, "title": "C"},
            ],
        }
        result = find_main_items(parsed)

        self.assertTrue(result["found"])
        self.assertEqual(result["path"], ["large"])
        self.assertEqual(result["count"], 3)

    def test_no_collection_found(self):
        """Sin listas de dicts, debe reportar que no encontró colección."""
        parsed = {
            "repo": {"name": "my-repo", "stars": 100},
            "owner": {"id": 42, "username": "johndoe"},
        }
        result = find_main_items(parsed)

        self.assertFalse(result["found"])
        self.assertEqual(result["count"], 0)
        self.assertIsNone(result["path"])

    def test_empty_list(self):
        """Lista vacía debe reportar que no encontró colección válida."""
        parsed = {"items": []}
        result = find_main_items(parsed)

        # Tu función retorna found=False para listas vacías (sin items válidos)
        self.assertFalse(result["found"])
        self.assertEqual(result["count"], 0)

    def test_top_keys_frequency(self):
        """Debe contar la frecuencia de keys en la colección."""
        parsed = [
            {"id": 1, "title": "A", "description": "Desc A"},
            {"id": 2, "title": "B"},  # sin description
            {"id": 3, "title": "C", "description": "Desc C"},
        ]
        result = find_main_items(parsed)

        self.assertTrue(result["found"])
        top_keys = result["top_keys"]

        # top_keys es una lista de tuplas (key, count)
        keys_dict = dict(top_keys)
        self.assertEqual(keys_dict["id"], 3)  # aparece en todos
        self.assertEqual(keys_dict["title"], 3)
        self.assertEqual(keys_dict["description"], 2)  # solo en 2


class SuggestMappingTests(SimpleTestCase):
    """Tests para las sugerencias automáticas de campos."""

    def test_suggests_title_field(self):
        """Debe detectar campos que parecen títulos."""
        items = [
            {"id": 1, "title": "Article 1", "body": "Content"},
            {"id": 2, "title": "Article 2", "body": "Content"},
        ]
        suggestions = suggest_mapping(items)

        self.assertIn("title", suggestions)
        self.assertIn("title", suggestions["title"])

    def test_suggests_multiple_candidates(self):
        """Debe sugerir múltiples candidatos ordenados por relevancia."""
        items = [
            {
                "id": 1,
                "headline": "Main title",
                "name": "Alt title",
                "label": "Short",
                "body": "Text",
            }
        ]
        suggestions = suggest_mapping(items)

        title_suggestions = suggestions.get("title", [])
        # Debe sugerir headline, name, y label para el rol "title"
        self.assertTrue(any(k in title_suggestions for k in ["headline", "name", "label"]))

    def test_detects_url_fields(self):
        """Debe detectar campos que contienen URLs."""
        items = [
            {"id": 1, "image": "https://example.com/image.jpg"},
            {"id": 2, "image": "https://example.com/image2.jpg"},
        ]
        suggestions = suggest_mapping(items)

        self.assertIn("image", suggestions)
        self.assertIn("image", suggestions["image"])

    def test_detects_date_fields(self):
        """Debe detectar campos que parecen fechas."""
        items = [
            {"id": 1, "created_at": "2024-01-15T10:30:00Z"},
            {"id": 2, "created_at": "2024-01-16T14:20:00Z"},
        ]
        suggestions = suggest_mapping(items)

        self.assertIn("date", suggestions)
        # Debe sugerir campos con "created" o similares
        date_suggestions = suggestions.get("date", [])
        self.assertTrue(any("created" in k for k in date_suggestions))

    def test_limits_suggestions(self):
        """No debe devolver más de 5 sugerencias por rol."""
        items = [
            {
                "field1": "val",
                "field2": "val",
                "field3": "val",
                "field4": "val",
                "field5": "val",
                "field6": "val",
                "field7": "val",
            }
        ]
        suggestions = suggest_mapping(items)

        for role, keys in suggestions.items():
            self.assertLessEqual(len(keys), 5, f"Rol {role} tiene más de 5 sugerencias")


class GetByPathTests(SimpleTestCase):
    """Tests para navegación por paths en estructuras anidadas."""

    def test_navigate_simple_path(self):
        """Debe navegar un path simple."""
        data = {"data": {"results": [1, 2, 3]}}
        result = get_by_path(data, ["data", "results"])

        self.assertEqual(result, [1, 2, 3])

    def test_navigate_with_index(self):
        """Debe soportar índices numéricos en el path."""
        data = {"items": [{"name": "A"}, {"name": "B"}]}
        result = get_by_path(data, ["items", 0, "name"])

        self.assertEqual(result, "A")

    def test_invalid_path_returns_none(self):
        """Path inválido debe retornar None."""
        data = {"data": {"results": []}}
        result = get_by_path(data, ["data", "nonexistent", "field"])

        self.assertIsNone(result)

    def test_empty_path_returns_root(self):
        """Path vacío debe retornar la raíz."""
        data = {"key": "value"}
        result = get_by_path(data, [])

        self.assertEqual(result, data)


class BuildAnalysisTests(SimpleTestCase):
    """Tests de integración para build_analysis completa."""

    def test_complete_analysis_structure(self):
        """El análisis debe incluir todas las keys esperadas."""
        parsed = [
            {"id": 1, "title": "A", "url": "http://a.com"},
            {"id": 2, "title": "B", "url": "http://b.com"},
        ]
        analysis = build_analysis(parsed)

        # Verifica estructura del resultado
        self.assertIn("format", analysis)
        self.assertIn("root_type", analysis)
        self.assertIn("main_collection", analysis)
        self.assertIn("keys", analysis)
        self.assertIn("roles", analysis)
        self.assertIn("suggestions", analysis)

    def test_root_type_detection(self):
        """Debe detectar correctamente el tipo de la raíz."""
        # Test con lista
        parsed_list = [{"id": 1}]
        analysis_list = build_analysis(parsed_list)
        self.assertEqual(analysis_list["root_type"], "list")

        # Test con dict
        parsed_dict = {"data": [{"id": 1}]}
        analysis_dict = build_analysis(parsed_dict)
        self.assertEqual(analysis_dict["root_type"], "dict")

    def test_format_detection_with_raw_text(self):
        """Debe detectar el formato si se pasa raw_text."""
        parsed = [{"id": 1}]
        raw_json = '[{"id": 1}]'

        analysis = build_analysis(parsed, raw_text=raw_json)
        self.assertEqual(analysis["format"], "json")

    def test_roles_include_all_defined(self):
        """Debe incluir todos los roles definidos en ROLE_DEFS."""
        parsed = [{"id": 1, "title": "Test"}]
        analysis = build_analysis(parsed)

        roles = analysis["roles"]
        # Verifica que incluya roles principales
        self.assertIn("title", roles)
        self.assertIn("description", roles)
        self.assertIn("image", roles)
        self.assertEqual(len(roles), len(ROLE_DEFS))

    def test_suggestions_per_role(self):
        """Debe generar sugerencias para cada rol."""
        parsed = [
            {
                "id": 1,
                "title": "Article",
                "description": "Summary",
                "image_url": "http://img.com/1.jpg",
            }
        ]
        analysis = build_analysis(parsed)

        suggestions = analysis["suggestions"]
        self.assertIn("title", suggestions)
        self.assertIn("description", suggestions)
        self.assertIn("image", suggestions)

        # title debe sugerir "title"
        self.assertIn("title", suggestions["title"])

    def test_no_collection_provides_message(self):
        """Sin colección principal, debe incluir mensaje informativo."""
        parsed = {"status": "ok", "single_item": {"name": "test"}}
        analysis = build_analysis(parsed)

        self.assertFalse(analysis["main_collection"]["found"])
        self.assertIn("message", analysis)
        self.assertIsInstance(analysis["message"], str)

    def test_path_display_for_root(self):
        """Para colección en raíz, path_display debe ser especial."""
        parsed = [{"id": 1}, {"id": 2}]
        analysis = build_analysis(parsed)

        path_display = analysis["main_collection"]["path_display"]
        # Normalmente será "(raíz)" o similar
        self.assertIsInstance(path_display, str)
        self.assertTrue(len(path_display) > 0)

    def test_keys_aggregation(self):
        """Debe agregar keys de toda la colección."""
        parsed = {
            "items": [
                {"id": 1, "title": "A"},
                {"id": 2, "title": "B", "extra": "X"},
            ]
        }
        analysis = build_analysis(parsed)

        all_keys = analysis["keys"]["all"]
        self.assertIn("id", all_keys)
        self.assertIn("title", all_keys)
        self.assertIn("extra", all_keys)

    def test_handles_xml_parsed_data(self):
        """Debe manejar datos parseados de XML (dicts con @attrs)."""
        # XML parseado con xmltodict suele tener estructura específica
        parsed = {
            "rss": {
                "channel": {
                    "item": [
                        {"title": "Post 1", "link": "http://1.com"},
                        {"title": "Post 2", "link": "http://2.com"},
                    ]
                }
            }
        }
        analysis = build_analysis(parsed)

        # Debe encontrar la colección anidada
        self.assertTrue(analysis["main_collection"]["found"])
        self.assertGreater(analysis["main_collection"]["count"], 0)
