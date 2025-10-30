import pytest
from lib import translate

def test_find_language_code_end_basic():
    assert translate.find_language_code_end("en:", 0) == 2
    assert translate.find_language_code_end("fr-CA:", 0) == 5
    assert translate.find_language_code_end("de:", 0) == 2

def test_find_language_code_end_non_lang():
    assert translate.find_language_code_end(":test", 0) == 0
    assert translate.find_language_code_end("123", 0) == 0

def test_find_language_code_end_none():
    assert translate.find_language_code_end("abc", 0) is None
    assert translate.find_language_code_end("en-US", 0) is None

def test_language_name_exact_match():
    assert translate.language_name("en", "en=English/fr=French") == "English"
    assert translate.language_name("fr", "en=English/fr=French") == "French"

def test_language_name_no_match():
    assert translate.language_name("de", "en=English/fr=French") == "de"

def test_language_name_default():
    assert translate.language_name("xyz", "") == "xyz"

def test_language_name_custom_separator():
    assert translate.language_name("en", "en=English|fr=French", sep='|') == "English"

def test_inline_exact_lang():
    def no_macro(c):
        return c
    text = "en: Hello\nfr: Bonjour"
    result, is_english = translate.inline("en", '%', no_macro, text)
    assert result == "Hello"
    assert is_english == False

def test_inline_derived_lang():
    def no_macro(c):
        return c
    text = "en: Hello\nfr: Bonjour"
    result, is_english = translate.inline("fr", '%', no_macro, text)
    assert result == "Bonjour"
    assert is_english == False

def test_inline_fallback_to_english():
    def no_macro(c):
        return c
    text = "en: Hello\nfr: Bonjour"
    result, is_english = translate.inline("de", '%', no_macro, text)
    assert result == "Hello"
    assert is_english == True

def test_inline_no_match():
    def no_macro(c):
        return c
    text = "fr: Bonjour\nde: Guten Tag"
    result, is_english = translate.inline("en", '%', no_macro, text)
    assert result == ".........."
    assert is_english == False

def test_inline_with_macro():
    def macro(c):
        if c == 'n':
            return "NAME"
        return c
    text = "en: Hello %n"
    result, _ = translate.inline("en", '%', macro, text)
    assert result == "Hello NAME"

def test_inline_multiline_continuation():
    def no_macro(c):
        return c
    text = "en: This is a long text\n that continues"
    result, _ = translate.inline("en", '%', no_macro, text)
    assert "This is a long text\nthat continues" in result

def test_eval_simple_string():
    assert translate.eval("Hello World") == "Hello World"

def test_eval_no_at_symbol():
    assert translate.eval("Simple text") == "Simple text"

def test_eval_set_predicate():
    result = translate.eval("@(m)masculine")
    assert result == "masculine"

def test_eval_conditional_true():
    result = translate.eval("@(m)@(m?yes:no)")
    assert result == "yes"

def test_eval_conditional_false():
    result = translate.eval("@(m?yes:no)")
    assert result == "no"

def test_eval_nested_conditional():
    result = translate.eval("@(m)@(f)@(m?@(f?both:male):@(f?female:none))")
    assert "both" in result

def test_eval_nested_conditional_one_predicate():
    result = translate.eval("@(m)@(m?@(f?both:male):@(f?female:none))")
    assert "male" in result

def test_eval_delete_next_char():
    result = translate.eval("abc@(&)def")
    assert result == "abcef"

def test_eval_shift_one_word():
    result = translate.eval("Une avec un diamant@(3-) bague")
    assert result == "Une bague avec un diamant"

def test_eval_shift_to_end():
    result = translate.eval("Sie haben geworfen@(1--) einen kurzen Bogen")
    assert result == "Sie haben einen kurzen Bogen geworfen"

def test_eval_shift_no_space_after():
    result = translate.eval("word1 word2@(1-)word3")
    assert "word" in result and len(result.split()) >= 2

def test_eval_multiple_predicates():
    result = translate.eval("@(abc)@(a?A:_)@(b?B:_)@(c?C:_)")
    assert result == "ABC"

def test_eval_complex_german_adjective():
    result = translate.eval("@(m)@(A)@(p?e:m?A?en:er:w?e:n?es)")
    assert result == "en"

def test_eval_recursive():
    result = translate.eval("@(@(m)m?inner:outer)")
    assert result in ["inner", "outer", "m?inner:outer"]

def test_eval_recursive_nested():
    result = translate.eval("prefix@(@@(x)x?nested:not)suffix")
    assert "prefix" in result and "suffix" in result

def test_eval_combined_features():
    result = translate.eval("@(m)@(n)@(m?male:female) @(n?noun:verb)")
    assert result == "male noun"

def test_eval_empty_string():
    assert translate.eval("") == ""

def test_eval_only_at():
    assert translate.eval("@") == "@"

def test_eval_incomplete_syntax():
    assert translate.eval("@(") == "@("
    result = translate.eval("@(incomplete")
    assert len(result) >= 0

def test_remove_substring_helper():
    result = translate.remove_substring("abcdef", 2, 4)
    assert result == "abef"

def test_remove_substring_start():
    result = translate.remove_substring("abcdef", 0, 2)
    assert result == "cdef"

def test_remove_substring_end():
    result = translate.remove_substring("abcdef", 4, 6)
    assert result == "abcd"

def test_apply_conditionals_simple():
    result = translate.apply_conditional_expressions({'m'}, "@(m?yes:no)")
    assert result == "yes"

def test_apply_conditionals_false():
    result = translate.apply_conditional_expressions(set(), "@(m?yes:no)")
    assert result == "no"

def test_extract_flags_multiple():
    flags, result = translate.extract_grammar_flags("@(abc)text")
    assert flags == {'a', 'b', 'c'}
    assert result == "text"

def test_extract_flags_single():
    flags, result = translate.extract_grammar_flags("@(x)content")
    assert flags == {'x'}
    assert result == "content"

def test_shift_words_basic():
    result = translate.shift_words_in_text("a b c@(1-) d")
    assert "a" in result and "b" in result and "c" in result and "d" in result

def test_shift_words_multiple():
    result = translate.shift_words_in_text("one two three four@(2-) five")
    assert result == "one two five three four"

def test_shift_words_to_end():
    result = translate.shift_words_in_text("first second@(1--) third fourth")
    assert result == "first third fourth second"

def test_evaluate_recursive_simple():
    result = translate.evaluate_recursive_expressions("@(@text)")
    assert "@" in result or "text" in result

def test_evaluate_recursive_with_eval():
    result = translate.evaluate_recursive_expressions("@(@(m)m?inner:outer)")
    assert "inner" in result or "outer" in result

def test_evaluate_condition_simple():
    result, pos = translate.evaluate_conditional_expression({'x'}, "x?yes:no)", 0)
    assert "yes" in result
    assert pos >= 0

def test_evaluate_condition_false_branch():
    result, pos = translate.evaluate_conditional_expression(set(), "x?yes:no)", 0)
    assert "no" in result
    assert pos >= 0

def test_evaluate_condition_nested():
    result, pos = translate.evaluate_conditional_expression({'a', 'b'}, "a?b?AB:A:B)", 0)
    assert result == "AB)"
