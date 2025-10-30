import pytest
from lib import ast, loc


class TestASTCreation:
    def test_mk_text(self):
        node = ast.mk_text("hello")
        assert isinstance(node.desc, ast.Atext)
        assert node.desc.value == "hello"
        assert node.location == loc.DUMMY

    def test_mk_var(self):
        node = ast.mk_var("x", ["field"])
        assert isinstance(node.desc, ast.Avar)
        assert node.desc.name == "x"
        assert node.desc.attrs == ["field"]

    def test_mk_int(self):
        node = ast.mk_int("42")
        assert isinstance(node.desc, ast.Aint)
        assert node.desc.value == "42"

    def test_mk_transl(self):
        node = ast.mk_transl(True, "key", "context")
        assert isinstance(node.desc, ast.Atransl)
        assert node.desc.decline is True
        assert node.desc.key == "key"
        assert node.desc.context == "context"


class TestASTOps:
    def test_mk_op1(self):
        operand = ast.mk_int("5")
        node = ast.mk_op1("not", operand)
        assert isinstance(node.desc, ast.Aop1)
        assert node.desc.op == "not"
        assert node.desc.operand == operand

    def test_mk_op2(self):
        left = ast.mk_int("1")
        right = ast.mk_int("2")
        node = ast.mk_op2("add", left, right)
        assert isinstance(node.desc, ast.Aop2)
        assert node.desc.op == "add"
        assert node.desc.left == left
        assert node.desc.right == right


class TestASTControl:
    def test_mk_if(self):
        cond = ast.mk_var("x", [])
        then_b = [ast.mk_text("yes")]
        else_b = [ast.mk_text("no")]
        node = ast.mk_if(cond, then_b, else_b)
        assert isinstance(node.desc, ast.Aif)
        assert node.desc.condition == cond
        assert node.desc.then_branch == then_b
        assert node.desc.else_branch == else_b

    def test_mk_for(self):
        start = ast.mk_int("1")
        end = ast.mk_int("10")
        body = [ast.mk_text("loop")]
        node = ast.mk_for("i", start, end, body)
        assert isinstance(node.desc, ast.Afor)
        assert node.desc.var == "i"
        assert node.desc.start == start
        assert node.desc.end == end
        assert node.desc.body == body

    def test_mk_foreach(self):
        var = ("item", ["name"])
        items = [[ast.mk_text("a")], [ast.mk_text("b")]]
        body = [ast.mk_var("item", ["name"])]
        node = ast.mk_foreach(var, items, body)
        assert isinstance(node.desc, ast.Aforeach)
        assert node.desc.var == var
        assert node.desc.items == items
        assert node.desc.body == body


class TestASTDefine:
    def test_mk_define(self):
        params = [("x", None), ("y", ast.mk_int("0"))]
        body = [ast.mk_text("def")]
        cont = [ast.mk_text("after")]
        node = ast.mk_define("func", params, body, cont)
        assert isinstance(node.desc, ast.Adefine)
        assert node.desc.name == "func"
        assert node.desc.params == params
        assert node.desc.body == body
        assert node.desc.continuation == cont

    def test_mk_apply(self):
        args = [(None, [ast.mk_int("1")]), ("x", [ast.mk_int("2")])]
        node = ast.mk_apply("func", args)
        assert isinstance(node.desc, ast.Aapply)
        assert node.desc.name == "func"
        assert node.desc.args == args

    def test_mk_let(self):
        value = [ast.mk_int("42")]
        body = [ast.mk_var("x", [])]
        node = ast.mk_let("x", value, body)
        assert isinstance(node.desc, ast.Alet)
        assert node.desc.var == "x"
        assert node.desc.value == value
        assert node.desc.body == body


class TestASTMisc:
    def test_mk_wid_hei(self):
        node = ast.mk_wid_hei("value")
        assert isinstance(node.desc, ast.AwidHei)
        assert node.desc.value == "value"

    def test_mk_pack(self):
        items = [ast.mk_text("a"), ast.mk_text("b")]
        node = ast.mk_pack(items)
        assert isinstance(node.desc, ast.Apack)
        assert node.desc.items == items

    def test_mk_include_file(self):
        source = loc.SourceFile("template.txt")
        node = ast.mk_include(source)
        assert isinstance(node.desc, ast.Ainclude)
        assert node.desc.source == source

    def test_mk_include_raw(self):
        source = loc.SourceRaw("raw content")
        node = ast.mk_include(source)
        assert isinstance(node.desc, ast.Ainclude)
        assert node.desc.source == source


class TestSubstitution:
    def test_subst_text(self):
        node = ast.mk_text("hello")
        result = ast.subst(lambda x: x.upper(), node)
        assert isinstance(result.desc, ast.Atext)
        assert result.desc.value == "HELLO"

    def test_subst_var_to_int(self):
        node = ast.mk_var("42", [])
        result = ast.subst(lambda x: x, node)
        assert isinstance(result.desc, ast.Aint)
        assert result.desc.value == "42"

    def test_subst_var_compound(self):
        node = ast.mk_var("a", ["b"])
        result = ast.subst(lambda x: "x.y" if x == "a" else x, node)
        assert isinstance(result.desc, ast.Avar)
        assert result.desc.name == "x"
        assert result.desc.attrs == ["y", "b"]

    def test_subst_list(self):
        nodes = [ast.mk_text("a"), ast.mk_text("b")]
        result = ast.subst_list(lambda x: x.upper(), nodes)
        assert len(result) == 2
        assert result[0].desc.value == "A"
        assert result[1].desc.value == "B"

    def test_subst_if(self):
        node = ast.mk_if(
            ast.mk_var("x", []),
            [ast.mk_text("yes")],
            [ast.mk_text("no")]
        )
        result = ast.subst(lambda x: x.upper(), node)
        assert isinstance(result.desc, ast.Aif)
        assert result.desc.condition.desc.name == "X"
        assert result.desc.then_branch[0].desc.value == "YES"
        assert result.desc.else_branch[0].desc.value == "NO"

    def test_subst_op2(self):
        node = ast.mk_op2("add", ast.mk_var("x", []), ast.mk_var("y", []))
        result = ast.subst(lambda x: x.upper(), node)
        assert isinstance(result.desc, ast.Aop2)
        assert result.desc.op == "ADD"
        assert result.desc.left.desc.name == "X"
        assert result.desc.right.desc.name == "Y"


class TestEdgeCases:
    def test_empty_attrs(self):
        node = ast.mk_var("x", [])
        assert node.desc.attrs == []

    def test_nested_structure(self):
        inner = ast.mk_if(
            ast.mk_var("a", []),
            [ast.mk_text("1")],
            [ast.mk_text("2")]
        )
        outer = ast.mk_if(
            ast.mk_var("b", []),
            [inner],
            []
        )
        assert isinstance(outer.desc, ast.Aif)
        assert isinstance(outer.desc.then_branch[0].desc, ast.Aif)

    def test_custom_location(self):
        custom_loc = loc.Loc(loc.SourceFile("test.ml"), 10, 20)
        node = ast.mk_text("test", custom_loc)
        assert node.location == custom_loc
        assert node.location.start == 10
        assert node.location.stop == 20
