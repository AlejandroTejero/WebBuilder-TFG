"""
Tests mejorados para WebBuilder.utils.mapping

Estos tests validan:
- Validación de mappings con roles obligatorios
- Detección de keys inexistentes
- Detección de duplicados en roles core
- Construcción de opciones para el wizard
- Persistencia de mappings en sesión y BD
"""
from django.test import SimpleTestCase, RequestFactory
from django.contrib.auth.models import User
from WebBuilder.models import APIRequest
from WebBuilder.utils.mapping import (
    read_mapping,
    store_mapping,
    get_mapping,
    resolve_api_id,
    save_mapping_to_db,
    build_role_options,
    validate_mapping,
)


class ValidateMappingTests(SimpleTestCase):
    """Tests para la validación de mappings."""

    def test_title_required_missing(self):
        """Debe fallar si falta el rol obligatorio 'title'."""
        mapping = {"description": "body", "image": "image_url"}
        result = validate_mapping(mapping, required_roles=("title",))

        self.assertFalse(result["ok"])
        self.assertTrue(len(result["errors"]) > 0)
        # Verifica que el error menciona "title"
        error_text = " ".join(result["errors"]).lower()
        self.assertIn("title", error_text)

    def test_title_required_empty_string(self):
        """Debe fallar si title está presente pero vacío."""
        mapping = {"title": "", "description": "body"}
        result = validate_mapping(mapping, required_roles=("title",))

        self.assertFalse(result["ok"])
        self.assertTrue(len(result["errors"]) > 0)

    def test_title_required_whitespace_only(self):
        """Debe limpiar y detectar strings con solo espacios como vacíos."""
        mapping = {"title": "   ", "description": "body"}
        result = validate_mapping(mapping, required_roles=("title",))

        self.assertFalse(result["ok"])
        # El cleaned debe tener title vacío después del strip
        self.assertEqual(result["cleaned"]["title"], "")

    def test_valid_mapping_passes(self):
        """Mapping válido con title debe pasar."""
        mapping = {"title": "headline", "description": "body"}
        result = validate_mapping(mapping, required_roles=("title",))

        self.assertTrue(result["ok"])
        self.assertEqual(len(result["errors"]), 0)

    def test_multiple_required_roles(self):
        """Debe validar múltiples roles obligatorios."""
        mapping = {"title": "headline"}  # falta description
        result = validate_mapping(
            mapping, required_roles=("title", "description")
        )

        self.assertFalse(result["ok"])
        error_text = " ".join(result["errors"]).lower()
        self.assertIn("description", error_text)

    def test_unknown_key_warning_with_analysis(self):
        """Debe advertir si una key no existe en la colección principal."""
        mapping = {"title": "nonexistent_field", "description": "body"}

        # Simula un análisis con keys conocidas
        analysis_result = {
            "main_collection": {
                "sample_keys": ["id", "body", "author"],
                "top_keys": [["body", 2], ["author", 2]],
            },
            "keys": {"all": ["id", "body", "author"]},
        }

        result = validate_mapping(mapping, analysis_result=analysis_result)

        # No debe ser error, solo warning
        self.assertTrue(result["ok"])
        self.assertTrue(len(result["warnings"]) > 0)

        warning_text = " ".join(result["warnings"]).lower()
        self.assertIn("nonexistent_field", warning_text)

    def test_no_warning_for_valid_keys(self):
        """No debe advertir si todas las keys existen."""
        mapping = {"title": "headline", "description": "body"}

        analysis_result = {
            "keys": {"all": ["id", "headline", "body", "author"]},
        }

        result = validate_mapping(mapping, analysis_result=analysis_result)

        self.assertTrue(result["ok"])
        self.assertEqual(len(result["warnings"]), 0)

    def test_duplicate_keys_warning(self):
        """Debe advertir si roles core usan la misma key."""
        mapping = {"title": "content", "description": "content"}  # duplicado!

        result = validate_mapping(
            mapping,
            warn_on_duplicates=True,
            core_roles_for_duplicates=("title", "description"),
        )

        # Es solo warning, no error
        self.assertTrue(result["ok"])
        self.assertTrue(len(result["warnings"]) > 0)

        warning_text = " ".join(result["warnings"]).lower()
        self.assertIn("content", warning_text)
        # Debe mencionar ambos roles
        self.assertTrue("title" in warning_text or "description" in warning_text)

    def test_no_duplicate_warning_if_disabled(self):
        """Si warn_on_duplicates=False, no debe advertir por duplicados."""
        mapping = {"title": "content", "description": "content"}

        result = validate_mapping(mapping, warn_on_duplicates=False)

        # Puede tener otros warnings pero no de duplicados
        self.assertTrue(result["ok"])

    def test_empty_mapping_with_no_required_roles(self):
        """Mapping vacío sin roles obligatorios debe pasar."""
        mapping = {}
        result = validate_mapping(mapping, required_roles=())

        self.assertTrue(result["ok"])
        self.assertEqual(len(result["errors"]), 0)

    def test_cleaned_mapping_strips_values(self):
        """Debe limpiar espacios de los valores."""
        mapping = {"title": "  headline  ", "description": " body "}
        result = validate_mapping(mapping)

        cleaned = result["cleaned"]
        self.assertEqual(cleaned["title"], "headline")
        self.assertEqual(cleaned["description"], "body")

    def test_non_string_values_converted_to_empty(self):
        """Valores no-string deben convertirse a string vacío."""
        mapping = {"title": None, "description": 123}
        result = validate_mapping(mapping, required_roles=("title",))

        self.assertFalse(result["ok"])  # title obligatorio y es None
        self.assertEqual(result["cleaned"]["title"], "")

    def test_validates_against_sample_keys_fallback(self):
        """Debe usar sample_keys si no hay keys.all en el análisis."""
        mapping = {"title": "missing_key"}

        analysis_result = {
            "main_collection": {"sample_keys": ["id", "name"]},
        }

        result = validate_mapping(mapping, analysis_result=analysis_result)

        self.assertTrue(len(result["warnings"]) > 0)
        warning_text = " ".join(result["warnings"]).lower()
        self.assertIn("missing_key", warning_text)

    def test_validates_against_top_keys_fallback(self):
        """Debe usar top_keys si no hay otras fuentes."""
        mapping = {"title": "missing_key"}

        analysis_result = {
            "main_collection": {
                "top_keys": [["id", 3], ["name", 3]],
            },
        }

        result = validate_mapping(mapping, analysis_result=analysis_result)

        self.assertTrue(len(result["warnings"]) > 0)

    def test_no_validation_without_analysis(self):
        """Sin análisis, no debe validar keys (pero sí roles obligatorios)."""
        mapping = {"title": "any_key", "description": "another_key"}

        result = validate_mapping(mapping, analysis_result=None)

        # Debe pasar porque title está presente y no hay análisis para validar keys
        self.assertTrue(result["ok"])
        # No debería generar warnings de keys inexistentes
        self.assertEqual(len(result["warnings"]), 0)


class ReadMappingTests(SimpleTestCase):
    """Tests para lectura de mapping desde POST data."""

    def test_reads_map_fields(self):
        """Debe leer campos map_<role> del POST."""
        post_data = {
            "map_title": "headline",
            "map_description": "body",
            "map_image": "image_url",
        }

        mapping = read_mapping(post_data)

        self.assertEqual(mapping["title"], "headline")
        self.assertEqual(mapping["description"], "body")
        self.assertEqual(mapping["image"], "image_url")

    def test_missing_fields_default_empty(self):
        """Roles no presentes deben tener valor vacío."""
        post_data = {"map_title": "headline"}

        mapping = read_mapping(post_data)

        self.assertEqual(mapping["title"], "headline")
        self.assertEqual(mapping["description"], "")
        self.assertEqual(mapping["image"], "")

    def test_reads_all_defined_roles(self):
        """Debe leer todos los roles definidos en ROLE_DEFS."""
        from WebBuilder.utils.analysis import ROLE_DEFS

        post_data = {f"map_{role}": f"key_{role}" for role in ROLE_DEFS.keys()}

        mapping = read_mapping(post_data)

        # Debe tener una entrada por cada rol
        self.assertEqual(len(mapping), len(ROLE_DEFS))
        for role in ROLE_DEFS.keys():
            self.assertIn(role, mapping)


class SessionMappingTests(SimpleTestCase):
    """Tests para almacenamiento en sesión."""

    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get("/")
        self.request.session = {}

    def test_store_and_get_mapping(self):
        """Debe guardar y recuperar mapping de la sesión."""
        mapping = {"title": "headline", "description": "body"}

        store_mapping(self.request, mapping)
        retrieved = get_mapping(self.request)

        self.assertEqual(retrieved, mapping)

    def test_get_empty_mapping_when_none_stored(self):
        """Debe retornar dict vacío si no hay mapping guardado."""
        retrieved = get_mapping(self.request)

        self.assertEqual(retrieved, {})

    def test_overwrite_existing_mapping(self):
        """Debe sobrescribir mapping existente."""
        store_mapping(self.request, {"title": "old"})
        store_mapping(self.request, {"title": "new", "description": "desc"})

        retrieved = get_mapping(self.request)

        self.assertEqual(retrieved["title"], "new")


class ResolveApiIdTests(SimpleTestCase):
    """Tests para resolución de api_request_id."""

    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get("/")
        self.request.session = {}

    def test_post_id_has_priority(self):
        """ID del POST debe tener prioridad sobre sesión."""
        self.request.session["last_api_request_id"] = "123"

        resolved = resolve_api_id(self.request, post_api_request_id="456")

        self.assertEqual(resolved, "456")

    def test_fallback_to_session(self):
        """Si no hay POST id, debe usar el de sesión."""
        self.request.session["last_api_request_id"] = "789"

        resolved = resolve_api_id(self.request, post_api_request_id=None)

        self.assertEqual(resolved, "789")

    def test_returns_none_if_no_id(self):
        """Debe retornar None si no hay id ni en POST ni en sesión."""
        resolved = resolve_api_id(self.request, post_api_request_id=None)

        self.assertIsNone(resolved)


class BuildRoleOptionsTests(SimpleTestCase):
    """Tests para construcción de opciones del wizard."""

    def test_builds_options_for_each_role(self):
        """Debe crear opciones para cada rol del análisis."""
        analysis_result = {
            "roles": ["title", "description", "image"],
            "keys": {"all": ["id", "headline", "body", "image_url"]},
            "suggestions": {
                "title": ["headline", "name"],
                "description": ["body", "summary"],
                "image": ["image_url", "thumbnail"],
            },
        }
        mapping = {}

        options = build_role_options(analysis_result, mapping)

        self.assertEqual(len(options), 3)
        role_names = [opt["role"] for opt in options]
        self.assertIn("title", role_names)
        self.assertIn("description", role_names)
        self.assertIn("image", role_names)

    def test_suggestions_appear_first(self):
        """Sugerencias deben aparecer primero en las opciones."""
        analysis_result = {
            "roles": ["title"],
            "keys": {"all": ["id", "headline", "body", "name"]},
            "suggestions": {"title": ["headline", "name"]},
        }
        mapping = {}

        options = build_role_options(analysis_result, mapping)

        title_options = next(opt for opt in options if opt["role"] == "title")
        option_keys = [o["key"] for o in title_options["options"]]

        # headline y name deben estar primero
        self.assertEqual(option_keys[0], "headline")
        self.assertEqual(option_keys[1], "name")

    def test_marks_selected_option(self):
        """Debe marcar la opción seleccionada según el mapping."""
        analysis_result = {
            "roles": ["title"],
            "keys": {"all": ["headline", "name"]},
            "suggestions": {"title": ["headline"]},
        }
        mapping = {"title": "name"}

        options = build_role_options(analysis_result, mapping)

        title_options = next(opt for opt in options if opt["role"] == "title")
        selected = [o for o in title_options["options"] if o["is_selected"]]

        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0]["key"], "name")

    def test_defaults_to_first_suggestion_if_no_mapping(self):
        """Si no hay mapping, debe seleccionar la primera sugerencia."""
        analysis_result = {
            "roles": ["title"],
            "keys": {"all": ["headline", "name"]},
            "suggestions": {"title": ["headline", "name"]},
        }
        mapping = {}

        options = build_role_options(analysis_result, mapping)

        title_options = next(opt for opt in options if opt["role"] == "title")
        selected = [o for o in title_options["options"] if o["is_selected"]]

        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0]["key"], "headline")

    def test_none_selected_flag(self):
        """Debe indicar si ninguna opción está seleccionada."""
        analysis_result = {
            "roles": ["title"],
            "keys": {"all": ["headline"]},
            "suggestions": {"title": []},  # sin sugerencias
        }
        mapping = {}

        options = build_role_options(analysis_result, mapping)

        title_options = next(opt for opt in options if opt["role"] == "title")

        # Si no hay sugerencias ni mapping, selected_key será ""
        # y none_selected debe ser True
        self.assertTrue(title_options["none_selected"])

    def test_limits_suggestions_to_five(self):
        """Debe incluir máximo 5 sugerencias por rol en las primeras posiciones."""
        analysis_result = {
            "roles": ["title"],
            "keys": {"all": ["k1", "k2", "k3", "k4", "k5", "k6", "k7"]},
            "suggestions": {"title": ["s1", "s2", "s3", "s4", "s5", "s6", "s7"]},
        }
        mapping = {}

        options = build_role_options(analysis_result, mapping)

        title_options = next(opt for opt in options if opt["role"] == "title")

        # El código hace [:5] en suggested_keys, pero luego añade TODAS las keys
        # de analysis_result["keys"]["all"] que no estaban ya.
        # Por lo tanto: 5 sugerencias + 7 keys all = pero con deduplicación
        # Como las sugerencias (s1-s7) NO están en keys.all (k1-k7), tenemos:
        # 5 sugerencias + 7 keys = 12 total
        total_keys = len(title_options["options"])
        self.assertEqual(total_keys, 12)  # 5 sugerencias + 7 keys all
        
        # Verifica que las primeras opciones son las sugerencias (máx 5)
        first_five_keys = [o["key"] for o in title_options["options"][:5]]
        for key in first_five_keys:
            self.assertTrue(key.startswith("s"))  # son las sugerencias s1-s5

    def test_deduplicates_keys(self):
        """No debe duplicar keys entre sugerencias y listado completo."""
        analysis_result = {
            "roles": ["title"],
            "keys": {"all": ["headline", "name", "id"]},
            "suggestions": {"title": ["headline", "name"]},
        }
        mapping = {}

        options = build_role_options(analysis_result, mapping)

        title_options = next(opt for opt in options if opt["role"] == "title")
        option_keys = [o["key"] for o in title_options["options"]]

        # Cada key debe aparecer solo una vez
        self.assertEqual(len(option_keys), len(set(option_keys)))

    def test_returns_empty_if_no_analysis(self):
        """Debe retornar lista vacía si no hay análisis."""
        options = build_role_options(None, {})

        self.assertEqual(options, [])
