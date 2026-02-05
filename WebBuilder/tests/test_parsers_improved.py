"""
Tests mejorados para WebBuilder.utils.parsers

Estos tests validan:
- Detección de formato (JSON, XML, unknown)
- Parseo de JSON (listas y dicts)
- Parseo de XML con validación segura
- Generación de resúmenes
- Manejo de errores en formatos inválidos
"""
from django.test import SimpleTestCase
from WebBuilder.utils.parsers import (
    detect_format,
    parse_raw,
    summarize_data,
)


class DetectFormatTests(SimpleTestCase):
    """Tests para detección automática de formato."""

    def test_detects_json_object(self):
        """Debe detectar JSON que empieza con '{'."""
        raw = '{"key": "value"}'
        fmt = detect_format(raw)

        self.assertEqual(fmt, "json")

    def test_detects_json_array(self):
        """Debe detectar JSON que empieza con '['."""
        raw = '[{"id": 1}, {"id": 2}]'
        fmt = detect_format(raw)

        self.assertEqual(fmt, "json")

    def test_detects_xml(self):
        """Debe detectar XML que empieza con '<'."""
        raw = '<?xml version="1.0"?><root><item>test</item></root>'
        fmt = detect_format(raw)

        self.assertEqual(fmt, "xml")

    def test_detects_xml_without_declaration(self):
        """Debe detectar XML sin declaración <?xml."""
        raw = '<root><item>test</item></root>'
        fmt = detect_format(raw)

        self.assertEqual(fmt, "xml")

    def test_ignores_leading_whitespace(self):
        """Debe ignorar espacios en blanco al inicio."""
        raw = '   \n  {"key": "value"}'
        fmt = detect_format(raw)

        self.assertEqual(fmt, "json")

    def test_returns_unknown_for_plain_text(self):
        """Texto plano debe retornar 'unknown'."""
        raw = 'This is just plain text'
        fmt = detect_format(raw)

        self.assertEqual(fmt, "unknown")

    def test_returns_unknown_for_empty_string(self):
        """String vacío debe retornar 'unknown'."""
        raw = ''
        fmt = detect_format(raw)

        self.assertEqual(fmt, "unknown")


class ParseRawJsonTests(SimpleTestCase):
    """Tests para parseo de JSON."""

    def test_parses_json_object(self):
        """Debe parsear objeto JSON correctamente."""
        raw = '{"name": "John", "age": 30}'
        fmt, parsed = parse_raw(raw)

        self.assertEqual(fmt, "json")
        self.assertIsInstance(parsed, dict)
        self.assertEqual(parsed["name"], "John")
        self.assertEqual(parsed["age"], 30)

    def test_parses_json_array(self):
        """Debe parsear array JSON correctamente."""
        raw = '[{"id": 1}, {"id": 2}]'
        fmt, parsed = parse_raw(raw)

        self.assertEqual(fmt, "json")
        self.assertIsInstance(parsed, list)
        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[0]["id"], 1)

    def test_parses_nested_json(self):
        """Debe parsear JSON anidado."""
        raw = '{"data": {"results": [{"title": "A"}, {"title": "B"}]}}'
        fmt, parsed = parse_raw(raw)

        self.assertEqual(fmt, "json")
        self.assertIn("data", parsed)
        self.assertIn("results", parsed["data"])
        self.assertEqual(len(parsed["data"]["results"]), 2)

    def test_parses_json_with_unicode(self):
        """Debe manejar caracteres Unicode en JSON."""
        raw = '{"message": "Hola, ¿cómo estás? 你好"}'
        fmt, parsed = parse_raw(raw)

        self.assertEqual(fmt, "json")
        self.assertIn("Hola", parsed["message"])
        self.assertIn("你好", parsed["message"])

    def test_parses_json_with_null(self):
        """Debe manejar valores null en JSON."""
        raw = '{"value": null, "active": true}'
        fmt, parsed = parse_raw(raw)

        self.assertEqual(fmt, "json")
        self.assertIsNone(parsed["value"])
        self.assertTrue(parsed["active"])

    def test_parses_json_with_numbers(self):
        """Debe preservar tipos numéricos."""
        raw = '{"int": 42, "float": 3.14, "negative": -10}'
        fmt, parsed = parse_raw(raw)

        self.assertEqual(fmt, "json")
        self.assertEqual(parsed["int"], 42)
        self.assertAlmostEqual(parsed["float"], 3.14)
        self.assertEqual(parsed["negative"], -10)

    def test_raises_on_invalid_json(self):
        """Debe lanzar error con JSON malformado."""
        raw = '{"key": invalid}'

        with self.assertRaises(Exception):
            parse_raw(raw)

    def test_raises_on_incomplete_json(self):
        """Debe lanzar error con JSON incompleto."""
        raw = '{"key": "value"'  # falta }

        with self.assertRaises(Exception):
            parse_raw(raw)


class ParseRawXmlTests(SimpleTestCase):
    """Tests para parseo de XML."""

    def test_parses_simple_xml(self):
        """Debe parsear XML simple."""
        raw = '<?xml version="1.0"?><root><item>test</item></root>'
        fmt, parsed = parse_raw(raw)

        self.assertEqual(fmt, "xml")
        self.assertIsInstance(parsed, dict)
        self.assertIn("root", parsed)

    def test_parses_xml_with_attributes(self):
        """Debe parsear XML con atributos."""
        raw = '<root><item id="1" type="test">value</item></root>'
        fmt, parsed = parse_raw(raw)

        self.assertEqual(fmt, "xml")
        # xmltodict convierte atributos a @attribute
        self.assertIn("root", parsed)

    def test_parses_xml_with_multiple_items(self):
        """Debe parsear XML con múltiples elementos."""
        raw = '''<?xml version="1.0"?>
        <root>
            <item><title>A</title></item>
            <item><title>B</title></item>
        </root>
        '''
        fmt, parsed = parse_raw(raw)

        self.assertEqual(fmt, "xml")
        self.assertIn("root", parsed)

    def test_parses_rss_feed(self):
        """Debe parsear feed RSS típico."""
        raw = '''<?xml version="1.0" encoding="UTF-8"?>
        <rss version="2.0">
            <channel>
                <title>My Feed</title>
                <item>
                    <title>Post 1</title>
                    <link>http://example.com/1</link>
                </item>
                <item>
                    <title>Post 2</title>
                    <link>http://example.com/2</link>
                </item>
            </channel>
        </rss>
        '''
        fmt, parsed = parse_raw(raw)

        self.assertEqual(fmt, "xml")
        self.assertIn("rss", parsed)

    def test_parses_xml_with_cdata(self):
        """Debe manejar secciones CDATA."""
        raw = '''<?xml version="1.0"?>
        <root>
            <content><![CDATA[<p>HTML content</p>]]></content>
        </root>
        '''
        fmt, parsed = parse_raw(raw)

        self.assertEqual(fmt, "xml")
        # El contenido CDATA debería estar presente
        self.assertIn("root", parsed)

    def test_parses_xml_with_namespaces(self):
        """Debe manejar XML con namespaces."""
        raw = '''<?xml version="1.0"?>
        <root xmlns:custom="http://example.com/ns">
            <custom:item>test</custom:item>
        </root>
        '''
        fmt, parsed = parse_raw(raw)

        self.assertEqual(fmt, "xml")
        self.assertIsInstance(parsed, dict)

    def test_raises_on_invalid_xml(self):
        """Debe lanzar error con XML malformado."""
        raw = '<root><item>unclosed'

        with self.assertRaises(Exception):
            parse_raw(raw)

    def test_validates_xml_securely(self):
        """Debe usar validación segura (defusedxml)."""
        # XXE attack attempt (debe ser bloqueado por defusedxml)
        raw = '''<?xml version="1.0"?>
        <!DOCTYPE foo [
            <!ENTITY xxe SYSTEM "file:///etc/passwd">
        ]>
        <root>&xxe;</root>
        '''

        # defusedxml debe lanzar error o bloquear el ataque
        with self.assertRaises(Exception):
            parse_raw(raw)


class ParseRawEdgeCasesTests(SimpleTestCase):
    """Tests para casos edge y errores."""

    def test_raises_on_unknown_format(self):
        """Debe lanzar error si el formato no es JSON ni XML."""
        raw = 'This is plain text, not JSON or XML'

        with self.assertRaises(ValueError) as context:
            parse_raw(raw)

        self.assertIn("JSON", str(context.exception))
        self.assertIn("XML", str(context.exception))

    def test_raises_on_empty_string(self):
        """Debe lanzar error con string vacío."""
        raw = ''

        with self.assertRaises(ValueError):
            parse_raw(raw)

    def test_handles_whitespace_only(self):
        """Debe lanzar error con solo espacios en blanco."""
        raw = '   \n\t   '

        with self.assertRaises(ValueError):
            parse_raw(raw)


class SummarizeDataTests(SimpleTestCase):
    """Tests para generación de resúmenes."""

    def test_summarizes_dict_root(self):
        """Debe resumir dict raíz contando claves."""
        parsed = {"key1": "val1", "key2": "val2", "key3": "val3"}
        summary = summarize_data("json", parsed)

        self.assertIsInstance(summary, str)
        self.assertIn("json", summary.lower())
        self.assertIn("dict", summary.lower())
        self.assertIn("3", summary)  # número de claves

    def test_summarizes_list_root(self):
        """Debe resumir list raíz contando elementos."""
        parsed = [{"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}]
        summary = summarize_data("json", parsed)

        self.assertIsInstance(summary, str)
        self.assertIn("json", summary.lower())
        self.assertIn("list", summary.lower())
        self.assertIn("4", summary)  # número de elementos

    def test_summarizes_xml_dict(self):
        """Debe indicar el formato XML."""
        parsed = {"root": {"item": "value"}}
        summary = summarize_data("xml", parsed)

        self.assertIn("xml", summary.lower())
        self.assertIn("dict", summary.lower())

    def test_summarizes_other_types(self):
        """Debe manejar tipos no estándar."""
        parsed = "unexpected string"
        summary = summarize_data("json", parsed)

        self.assertIsInstance(summary, str)
        self.assertTrue(len(summary) > 0)

    def test_summary_is_non_empty(self):
        """Resumen siempre debe ser no vacío."""
        test_cases = [
            ("json", {}),
            ("json", []),
            ("xml", {"root": {}}),
            ("json", {"a": 1}),
        ]

        for fmt, parsed in test_cases:
            summary = summarize_data(fmt, parsed)
            self.assertTrue(len(summary) > 0)

    def test_summary_includes_format(self):
        """Resumen debe mencionar el formato detectado."""
        summary = summarize_data("json", {"key": "value"})
        self.assertIn("json", summary.lower())

        summary = summarize_data("xml", {"root": {}})
        self.assertIn("xml", summary.lower())

    def test_summary_includes_root_type(self):
        """Resumen debe mencionar el tipo de la raíz."""
        summary_dict = summarize_data("json", {"key": "value"})
        self.assertIn("dict", summary_dict.lower())

        summary_list = summarize_data("json", [1, 2, 3])
        self.assertIn("list", summary_list.lower())


class IntegrationTests(SimpleTestCase):
    """Tests de integración completos."""

    def test_full_json_workflow(self):
        """Test completo: detección + parseo + resumen JSON."""
        raw = '{"data": {"results": [{"id": 1}, {"id": 2}]}}'

        # Detectar
        fmt_detected = detect_format(raw)
        self.assertEqual(fmt_detected, "json")

        # Parsear
        fmt, parsed = parse_raw(raw)
        self.assertEqual(fmt, "json")
        self.assertIsInstance(parsed, dict)

        # Resumir
        summary = summarize_data(fmt, parsed)
        self.assertIn("json", summary.lower())
        self.assertIn("dict", summary.lower())

    def test_full_xml_workflow(self):
        """Test completo: detección + parseo + resumen XML."""
        raw = '''<?xml version="1.0"?>
        <feed>
            <entry><title>A</title></entry>
            <entry><title>B</title></entry>
        </feed>
        '''

        # Detectar
        fmt_detected = detect_format(raw)
        self.assertEqual(fmt_detected, "xml")

        # Parsear
        fmt, parsed = parse_raw(raw)
        self.assertEqual(fmt, "xml")
        self.assertIsInstance(parsed, dict)

        # Resumir
        summary = summarize_data(fmt, parsed)
        self.assertIn("xml", summary.lower())

    def test_realistic_api_response(self):
        """Test con respuesta realista de API."""
        raw = '''{
            "status": "success",
            "meta": {
                "total": 100,
                "page": 1
            },
            "data": {
                "articles": [
                    {
                        "id": 1,
                        "title": "First Article",
                        "author": "John Doe",
                        "published_at": "2024-01-15T10:00:00Z"
                    },
                    {
                        "id": 2,
                        "title": "Second Article",
                        "author": "Jane Smith",
                        "published_at": "2024-01-16T14:30:00Z"
                    }
                ]
            }
        }'''

        fmt, parsed = parse_raw(raw)

        self.assertEqual(fmt, "json")
        self.assertIn("data", parsed)
        self.assertIn("articles", parsed["data"])
        self.assertEqual(len(parsed["data"]["articles"]), 2)

        summary = summarize_data(fmt, parsed)
        self.assertIn("3", summary)  # 3 claves raíz: status, meta, data
