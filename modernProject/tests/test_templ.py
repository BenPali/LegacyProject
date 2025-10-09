import pytest
from modernProject.lib import templ
from modernProject.lib.templ import parse, eval_template, render


def test_parse_returns_ast_node():
    result = parse("test source")
    assert result is not None


def test_eval_template_returns_empty_string():
    template = parse("anything")
    result = eval_template(template, {})
    assert result == ""


def test_eval_template_with_context():
    template = parse("test")
    context = {"key": "value"}
    result = eval_template(template, context)
    assert result == ""


def test_render_empty_string():
    result = render("", {})
    assert result == ""


def test_render_simple_string():
    result = render("hello world", {})
    assert result == ""


def test_render_with_context():
    context = {"name": "Alice", "age": 30}
    result = render("Hello {name}", context)
    assert result == ""


def test_render_complex_template():
    template = """
    <html>
        <body>
            <h1>Welcome</h1>
        </body>
    </html>
    """
    result = render(template, {})
    assert result == ""
