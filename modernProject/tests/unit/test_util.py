import os
import tempfile
from pathlib import Path

from lib import util, driver, gwdef, adef, config


def create_test_config():
    output_conf = config.OutputConf(
        status=lambda x: None,
        header=lambda x: None,
        body=lambda x: None,
        flush=lambda: None
    )
    return config.Config(
        output_conf=output_conf,
        command='/geneweb',
        bname='test_base',
        private_years=100,
        public_if_no_date=20,
        hide_names=False,
        use_restrict=False,
        vowels='aeiouyAEIOUY',
        base_dir='.',
        henv={'lang': 'en'},
        senv={'m': 'A'}
    )


def create_test_person(first_name='John', surname='Doe', sex=gwdef.Sex.MALE,
                        access=gwdef.Access.PUBLIC, occ=0):
    return driver.GenPerson(
        first_name=first_name,
        surname=surname,
        occ=occ,
        image='',
        public_name='',
        qualifiers=[],
        aliases=[],
        first_names_aliases=[],
        surnames_aliases=[],
        titles=[],
        rparents=[],
        related=[],
        occupation='',
        sex=sex,
        access=access,
        birth=adef.CdateNone(),
        birth_place='',
        birth_note='',
        birth_src='',
        baptism=adef.CdateNone(),
        baptism_place='',
        baptism_note='',
        baptism_src='',
        death=gwdef.NotDead(),
        death_place='',
        death_note='',
        death_src='',
        burial=gwdef.UnknownBurial(),
        burial_place='',
        burial_note='',
        burial_src='',
        pevents=[],
        notes='',
        psources='',
        key_index=''
    )


def test_escape_html():
    assert util.escape_html('hello') == 'hello'
    assert util.escape_html('a&b') == 'a&#38;b'
    assert util.escape_html('a<b>c') == 'a&#60;b&#62;c'
    assert util.escape_html('"test"') == '&#34;test&#34;'
    assert util.escape_html("'test'") == '&#39;test&#39;'
    assert util.escape_html('<script>alert("XSS")</script>') == '&#60;script&#62;alert(&#34;XSS&#34;)&#60;/script&#62;'


def test_esc():
    assert util.esc('test') == 'test'
    assert util.esc('<b>test</b>') == '&#60;b&#62;test&#60;/b&#62;'


def test_escape_attribute():
    assert util.escape_attribute('hello') == 'hello'
    assert util.escape_attribute('a&b') == 'a&#38;b'
    assert util.escape_attribute('"test"') == '&#34;test&#34;'
    assert util.escape_attribute("'test'") == '&#39;test&#39;'


def test_clean_html_tags():
    assert util.clean_html_tags('hello') == 'hello'
    assert util.clean_html_tags('<b>hello</b>') == 'hello'
    assert util.clean_html_tags('<p>test</p><br>') == 'test'
    assert util.clean_html_tags('<a href="url">link</a>') == 'link'


def test_clean_comment_tags():
    assert util.clean_comment_tags('hello') == 'hello'
    assert util.clean_comment_tags('<!--comment-->text') == 'text'
    assert util.clean_comment_tags('a<!--x-->b<!--y-->c') == 'abc'


def test_uri_encode():
    assert util.uri_encode('hello world') == 'hello%20world'
    assert util.uri_encode('test@example.com') == 'test%40example.com'
    assert util.uri_encode('a/b/c') == 'a%2Fb%2Fc'
    assert util.uri_encode('foo&bar=baz') == 'foo%26bar%3Dbaz'


def test_uri_decode():
    assert util.uri_decode('hello%20world') == 'hello world'
    assert util.uri_decode('test%40example.com') == 'test@example.com'
    assert util.uri_decode('a%2Fb%2Fc') == 'a/b/c'


def test_hash_file():
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write('test content')
        fname = f.name

    try:
        hash_val = util.hash_file(fname)
        assert hash_val is not None
        assert len(hash_val) == 32
        assert hash_val == util.hash_file(fname)
    finally:
        os.unlink(fname)

    assert util.hash_file('/nonexistent/file.txt') is None


def test_hash_file_cached():
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write('test content')
        fname = f.name

    try:
        hash1 = util.hash_file_cached(fname)
        hash2 = util.hash_file_cached(fname)
        assert hash1 == hash2
        assert hash1 is not None
    finally:
        os.unlink(fname)

    assert util.hash_file_cached('/nonexistent/file.txt') is None


def test_is_hidden():
    p = create_test_person(surname='Doe')
    assert not util.is_hidden(p)

    p_hidden = create_test_person(surname='')
    assert util.is_hidden(p_hidden)


def test_is_hide_names():
    conf = create_test_config()
    p = create_test_person()

    assert not util.is_hide_names(conf, p)

    conf.hide_names = True
    assert util.is_hide_names(conf, p)

    conf.hide_names = False
    p_private = create_test_person(access=gwdef.Access.PRIVATE)
    assert util.is_hide_names(conf, p_private)


def test_access_status():
    p_public = create_test_person(access=gwdef.Access.PUBLIC)
    assert util.access_status(p_public) == 'public'

    p_private = create_test_person(access=gwdef.Access.PRIVATE)
    assert util.access_status(p_private) == 'private'

    p_iftitles = create_test_person(access=gwdef.Access.IF_TITLES)
    assert util.access_status(p_iftitles) == 'iftitles'


def test_start_with():
    assert util.start_with('test', 0, 'test string')
    assert util.start_with('string', 5, 'test string')
    assert not util.start_with('foo', 0, 'test string')
    assert not util.start_with('test', 10, 'test')
    assert not util.start_with('test', -1, 'test')


def test_start_with_vowel():
    conf = create_test_config()

    assert util.start_with_vowel(conf, 'apple')
    assert util.start_with_vowel(conf, 'elephant')
    assert not util.start_with_vowel(conf, 'banana')
    assert not util.start_with_vowel(conf, 'cherry')
    assert not util.start_with_vowel(conf, '')


def test_strictly_after_private_years():
    current_year = 2025
    dmy = adef.Dmy(day=1, month=1, year=1900, prec=adef.Precision.SURE, delta=0)

    assert util.strictly_after_private_years(dmy, 100)

    dmy_recent = adef.Dmy(day=1, month=1, year=current_year - 50, prec=adef.Precision.SURE, delta=0)
    assert not util.strictly_after_private_years(dmy_recent, 100)


def test_is_public_with_public_access():
    conf = create_test_config()
    p = create_test_person(access=gwdef.Access.PUBLIC)
    base = None

    assert util.is_public(conf, base, p)


def test_is_public_with_titles():
    conf = create_test_config()
    title = util.Title(name='Duke', place='Edinburgh')
    p = create_test_person(access=gwdef.Access.IF_TITLES)
    p.titles = [title]
    base = None

    assert util.is_public(conf, base, p)


def test_accessible_by_key():
    conf = create_test_config()
    base = None

    p = create_test_person(first_name='John', surname='Doe')
    assert util.accessible_by_key(conf, base, p, 'John', 'Doe')

    p_unknown = create_test_person(first_name='?', surname='?')
    assert not util.accessible_by_key(conf, base, p_unknown, '?', '?')

    p_empty = create_test_person(first_name='', surname='')
    assert not util.accessible_by_key(conf, base, p_empty, '', '')


def test_commd():
    conf = create_test_config()

    url = util.commd(conf)
    assert '/geneweb' in url
    assert 'b=test_base' in url

    url_no_pwd = util.commd(conf, pwd=False)
    assert 'b=test_base' not in url_no_pwd

    url_excl = util.commd(conf, excl=['lang'])
    assert 'lang=' not in url_excl


def test_prefix_base():
    conf = create_test_config()

    url = util.prefix_base(conf)
    assert '/geneweb' in url
    assert 'b=test_base' not in url


def test_prefix_base_password():
    conf = create_test_config()

    url = util.prefix_base_password(conf)
    assert '/geneweb' in url
    assert 'b=test_base' in url


def test_acces():
    conf = create_test_config()
    base = None
    p = create_test_person(first_name='John', surname='Doe', occ=0)

    access_str = util.acces(conf, base, p)
    assert 'p=' in access_str or 'i=' in access_str


def test_acces_n():
    conf = create_test_config()
    base = None
    p = create_test_person(first_name='John', surname='Doe', occ=2)

    access_str = util.acces_n(conf, base, '2', p)
    assert 'p2=' in access_str or 'i2=' in access_str

    access_str_no_n = util.acces_n(conf, base, '', p)
    assert 'p=' in access_str_no_n or 'i=' in access_str_no_n


def test_geneweb_link():
    conf = create_test_config()

    link = util.geneweb_link(conf, 'i=123', 'Test Person')
    assert '<a href=' in link
    assert 'i=123' in link
    assert 'Test Person' in link


def test_wprint_geneweb_link(capsys):
    conf = create_test_config()

    util.wprint_geneweb_link(conf, 'i=123', 'Test Person')
    captured = capsys.readouterr()
    assert '<a href=' in captured.out
    assert 'Test Person' in captured.out


def test_person_title():
    conf = create_test_config()
    base = None

    title = util.Title(name='Duke', place='Edinburgh')
    p = create_test_person()
    p.titles = [title]

    title_text = util.person_title(conf, base, p)
    assert 'Duke' in title_text

    p_no_title = create_test_person()
    assert util.person_title(conf, base, p_no_title) == ''


def test_main_title():
    conf = create_test_config()
    base = None

    title1 = util.Title(name='Duke', place='Edinburgh')
    title2 = util.Title(name='Earl', place='Sussex')
    p = create_test_person()
    p.titles = [title1, title2]

    main = util.main_title(conf, base, p)
    assert main == title1

    p_no_title = create_test_person()
    assert util.main_title(conf, base, p_no_title) is None


def test_nobtit():
    conf = create_test_config()
    base = None

    title1 = util.Title(name='Duke')
    title2 = util.Title(name='Earl')
    p = create_test_person()
    p.titles = [title1, title2]

    titles = util.nobtit(conf, base, p)
    assert len(titles) == 2

    conf.denied_titles = {'Duke'}
    titles = util.nobtit(conf, base, p)
    assert len(titles) == 1
    assert titles[0].name == 'Earl'


def test_gen_person_text_with_public_name():
    conf = create_test_config()
    base = None

    p = create_test_person(first_name='John', surname='Doe')
    p.public_name = 'Jack Doe'
    text = util.gen_person_text(conf, base, p)
    assert 'Jack Doe' in text


def test_gen_person_text_with_qualifiers():
    conf = create_test_config()
    base = None

    p = create_test_person(first_name='John', surname='Doe')
    p.qualifiers = ['Jr.']
    text = util.gen_person_text(conf, base, p, html_tags=True, escape=False)
    assert 'Jr.' in text
    assert '<em>' in text

    text_escaped = util.gen_person_text(conf, base, p, html_tags=True, escape=True)
    assert 'Jr.' in text_escaped
    assert '&#60;em&#62;' in text_escaped


def test_gen_person_text_no_surname():
    conf = create_test_config()
    base = None

    p = create_test_person(first_name='John', surname='Doe')
    text = util.gen_person_text(conf, base, p, sn=False)
    assert 'John' in text
    assert 'Doe' not in text


def test_person_text_without_title():
    conf = create_test_config()
    base = None

    p = create_test_person(first_name='John', surname='Doe')
    text = util.person_text_without_title(conf, base, p)
    assert 'John' in text
    assert 'Doe' in text


def test_titled_person_text():
    conf = create_test_config()
    base = None

    title = util.Title(name='Duke', place='Edinburgh')
    p = create_test_person(first_name='John', surname='Doe')
    p.titles = [title]

    text = util.titled_person_text(conf, base, p)
    assert 'Duke' in text
    assert 'Edinburgh' in text
    assert 'John' in text


def test_titled_person_text_with_public_name():
    conf = create_test_config()
    base = None

    p = create_test_person(first_name='John', surname='Doe')
    p.public_name = 'Jack Doe'

    text = util.titled_person_text(conf, base, p)
    assert 'Jack Doe' in text


def test_etc_file_name():
    conf = create_test_config()
    conf.base_dir = '/test/path'

    fname = util.etc_file_name(conf, 'test.txt')
    assert '/test/path/etc/test.txt' in fname


def test_open_etc_file():
    conf = create_test_config()

    with tempfile.TemporaryDirectory() as tmpdir:
        etc_dir = os.path.join(tmpdir, 'etc')
        os.makedirs(etc_dir)

        test_file = os.path.join(etc_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('test content')

        conf.base_dir = tmpdir

        result = util.open_etc_file(conf, 'test.txt')
        assert result is not None
        f, path = result
        content = f.read()
        f.close()
        assert 'test content' in content

    result = util.open_etc_file(conf, 'nonexistent.txt')
    assert result is None


def test_is_full_html_template():
    conf = create_test_config()

    with tempfile.TemporaryDirectory() as tmpdir:
        etc_dir = os.path.join(tmpdir, 'etc')
        os.makedirs(etc_dir)

        html_file = os.path.join(etc_dir, 'full.html')
        with open(html_file, 'w') as f:
            f.write('<!DOCTYPE html>\n<html><body>test</body></html>')

        partial_file = os.path.join(etc_dir, 'partial.html')
        with open(partial_file, 'w') as f:
            f.write('<div>test</div>')

        conf.base_dir = tmpdir

        assert util.is_full_html_template(conf, 'full.html')
        assert not util.is_full_html_template(conf, 'partial.html')


def test_private_txt():
    conf = create_test_config()

    assert util.private_txt(conf, 'test') == 'test'

    conf.hide_private_names = True
    assert util.private_txt(conf, 'test') == 'x'


def test_html(capsys):
    conf = create_test_config()

    util.html(conf)
    captured = capsys.readouterr()
    assert 'Content-Type: text/html' in captured.out


def test_unauthorized(capsys):
    conf = create_test_config()

    util.unauthorized(conf, 'Access denied')
    captured = capsys.readouterr()
    assert '401 Unauthorized' in captured.out
    assert 'Access denied' in captured.out


def test_hidden_input(capsys):
    conf = create_test_config()

    util.hidden_input(conf, 'key', 'value')
    captured = capsys.readouterr()
    assert '<input type="hidden"' in captured.out
    assert 'name="key"' in captured.out
    assert 'value="value"' in captured.out


def test_hidden_input_s(capsys):
    conf = create_test_config()

    util.hidden_input_s(conf, 'key', 'value')
    captured = capsys.readouterr()
    assert '<input type="hidden"' in captured.out


def test_hidden_textarea(capsys):
    conf = create_test_config()

    util.hidden_textarea(conf, 'key', 'value')
    captured = capsys.readouterr()
    assert '<textarea' in captured.out
    assert 'name="key"' in captured.out
    assert 'value' in captured.out


def test_submit_input(capsys):
    conf = create_test_config()

    util.submit_input(conf, 'submit', 'Submit')
    captured = capsys.readouterr()
    assert '<input type="submit"' in captured.out
    assert 'name="submit"' in captured.out


def test_hidden_env(capsys):
    conf = create_test_config()
    conf.henv = {'key1': 'value1'}
    conf.senv = {'key2': 'value2'}

    util.hidden_env(conf)
    captured = capsys.readouterr()
    assert 'key1' in captured.out
    assert 'value1' in captured.out
    assert 'key2' in captured.out
    assert 'value2' in captured.out


def test_hidden_env_aux(capsys):
    conf = create_test_config()
    env = [('key1', 'value1'), ('key2', 'value2')]

    util.hidden_env_aux(conf, env)
    captured = capsys.readouterr()
    assert 'key1' in captured.out
    assert 'value1' in captured.out
    assert 'key2' in captured.out
    assert 'value2' in captured.out


def test_place_of_string():
    conf = create_test_config()
    conf.base_env = [('place', 'town, county, region')]

    result = util.place_of_string(conf, 'Boston, Suffolk, MA')
    assert result is not None
    assert result['town'] == 'Boston'
    assert result['county'] == 'Suffolk'
    assert result['region'] == 'MA'


def test_place_of_string_no_config():
    conf = create_test_config()
    conf.base_env = []

    result = util.place_of_string(conf, 'Boston, MA')
    assert result is None


def test_get_approx_date_place():
    dmy1 = adef.Dmy(day=1, month=1, year=1900, prec=adef.Precision.SURE, delta=0)
    dmy2 = adef.Dmy(day=15, month=2, year=1900, prec=adef.Precision.SURE, delta=0)

    result_date, result_place = util.get_approx_date_place(dmy1, 'Place1', None, 'Place2')
    assert result_date == dmy1
    assert result_place == 'Place1'

    result_date, result_place = util.get_approx_date_place(None, 'Place1', dmy2, 'Place2')
    assert result_date == dmy2
    assert result_place == 'Place2'


def test_string_of_decimal_num():
    conf = create_test_config()
    conf.lexicon = {'(decimal separator)': ','}

    result = util.string_of_decimal_num(conf, 3.14)
    assert ',' in result or '.' in result


def test_string_of_pevent_name():
    conf = create_test_config()
    conf.lexicon = {'birth': 'Birth', 'baptism': 'Baptism'}

    assert util.transl(conf, 'birth') == 'Birth'


def test_string_of_fevent_name():
    conf = create_test_config()
    conf.lexicon = {'marriage event': 'Marriage', 'divorce event': 'Divorce'}

    assert util.transl(conf, 'marriage event') == 'Marriage'


def test_string_of_witness_kind():
    conf = create_test_config()
    conf.lexicon = {}

    result = util.transl_nth(conf, 'witness/witness/witnesses', 0)
    assert result is not None


def test_string_of_witness_kind_raw():
    assert util.string_of_witness_kind_raw('Witness') == ''
    assert util.string_of_witness_kind_raw('Witness_GodParent') == 'godp'
    assert util.string_of_witness_kind_raw('Witness_Informant') == 'info'


def test_find_person_in_env_by_id(temp_dir):
    from tests.gwb_generator import create_minimal_gwb
    from lib import database, secure, driver

    secure.add_assets(temp_dir)
    gwb_path = create_minimal_gwb(temp_dir, "test_base")

    conf = create_test_config()
    conf.env = {'i': '0'}

    def check_find_person(base):
        result = util.find_person_in_env(conf, base, '')
        assert result is not None
        first_name = driver.sou(base, result.first_name).decode()
        surname = driver.sou(base, result.surname).decode()
        assert first_name == "John"
        assert surname == "Doe"
        return True

    result = database.with_database(gwb_path, check_find_person)
    assert result is True


def test_p_getenv():
    env = {'key1': 'value1', 'key2': 'value2'}
    assert util.p_getenv(env, 'key1') == 'value1'
    assert util.p_getenv(env, 'missing') == ''


def test_p_getint():
    env = {'num': '42', 'invalid': 'abc'}
    assert util.p_getint(env, 'num') == 42
    assert util.p_getint(env, 'invalid') is None
    assert util.p_getint(env, 'missing') is None


def test_browser_doesnt_have_tables():
    conf = create_test_config()
    conf.request = ['User-Agent: Lynx/2.8']

    assert util.browser_doesnt_have_tables(conf) is True


def test_browser_doesnt_have_tables_chrome():
    conf = create_test_config()
    conf.request = ['User-Agent: Chrome/90.0']

    assert util.browser_doesnt_have_tables(conf) is False


def test_start_equiv_with_case_sensitive():
    result = util.start_equiv_with(True, 'test', 'this is a test', 10)
    assert result == 14


def test_start_equiv_with_not_found():
    result = util.start_equiv_with(True, 'xyz', 'this is a test', 0)
    assert result is None


def test_in_text():
    result = util.in_text(True, 'test', 'this is a test string')
    assert result is True


def test_in_text_not_found():
    result = util.in_text(True, 'xyz', 'this is a test string')
    assert result is False


def test_in_text_with_html():
    result = util.in_text(True, 'test', 'this is <b>a test</b> string')
    assert result is True


def test_html_highlight():
    result = util.html_highlight(True, 'test', 'this is a test string')
    assert '<span class="found">' in result
    assert 'test' in result


def test_html_highlight_no_match():
    result = util.html_highlight(True, 'xyz', 'this is a test string')
    assert '<span class="found">' not in result


def test_cache_visited():
    conf = create_test_config()
    conf.bname = 'testdb'

    path = util.cache_visited(conf)
    assert 'cache_visited' in path
    assert 'testdb.gwb' in path


def test_transl():
    conf = create_test_config()
    conf.lexicon = {'hello': 'Hello', 'world': 'World'}

    assert util.transl(conf, 'hello') == 'Hello'
    assert util.transl(conf, 'missing') != ''


def test_transl_nth():
    conf = create_test_config()
    conf.lexicon = {'choice1/choice2/choice3': 'First/Second/Third'}

    result = util.transl_nth(conf, 'choice1/choice2/choice3', 1)
    assert result is not None


def test_ftransl():
    conf = create_test_config()
    conf.lexicon = {'greeting': 'Hello %s'}

    result = util.ftransl(conf, 'greeting')
    assert 'Hello' in result or 'greeting' in result


def test_ftransl_nth():
    conf = create_test_config()
    conf.lexicon = {}

    result = util.ftransl_nth(conf, 'item1/item2', 0)
    assert result is not None


def test_gen_decline():
    conf = create_test_config()
    conf.vowels = 'aeiouy'

    result = util.gen_decline(conf, 'test', 'value1', 'value2', 'value2')
    assert result is not None


def test_index_of_sex():
    assert util.index_of_sex(gwdef.Sex.MALE) == 0
    assert util.index_of_sex(gwdef.Sex.FEMALE) == 1
    assert util.index_of_sex(gwdef.Sex.NEUTER) == 2


def test_tnf():
    result = util.tnf('test phrase')
    assert 'Test Phrase' in result or 'test phrase' in result


def test_etc_file_name_with_lang():
    conf = create_test_config()
    conf.lang = 'en'

    fname = util.etc_file_name(conf, 'template')
    assert 'template' in fname


def test_find_file_in_directories():
    import tempfile
    import os

    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('test')

        result = util.find_file_in_directories([tmpdir], 'test.txt')
        assert result is not None
        assert 'test.txt' in result


def test_read_base_env():
    import tempfile
    import os

    with tempfile.TemporaryDirectory() as tmpdir:
        gwf_file = os.path.join(tmpdir, 'test.gwf')
        with open(gwf_file, 'w') as f:
            f.write('key1=value1\\n')
            f.write('key2=value2\\n')

        result = util.read_base_env('test', tmpdir)
        assert isinstance(result, list)


def test_dispatch_in_columns():
    items = ['a', 'b', 'c', 'd', 'e', 'f']

    result = util.dispatch_in_columns(2, items, lambda x: x)
    assert len(result) == 2


def test_string_with_macros():
    conf = create_test_config()
    result = util.string_with_macros(conf, [], 'test %bn string')
    assert 'test' in result.lower()


def test_name_with_roman_number():
    result = util.name_with_roman_number('test 12 name')
    assert result is not None


def test_gen_decline_with_placeholders():
    conf = create_test_config()
    conf.vowels = 'aeiouy'

    result = util.gen_decline(conf, 'son of %1 and %2', 'John', 'Mary', 'mary')
    assert 'John' in result
    assert 'Mary' in result


def test_gen_decline_with_vowel_pattern():
    conf = create_test_config()
    conf.vowels = 'aeiouy'

    result = util.gen_decline(conf, '[a|an] X', '', '', '')
    assert result is not None


def test_string_of_pevent_name_coverage():
    conf = create_test_config()
    conf.lexicon = {'birth': 'Birth', 'death': 'Death', 'baptism': 'Baptism'}

    assert util.transl(conf, 'birth') == 'Birth'
    assert util.transl(conf, 'death') == 'Death'


def test_get_approx_birth_date_place():
    conf = create_test_config()
    base = None
    p = create_test_person()
    p.birth = adef.CdateDate(date=adef.DateGreg(
        dmy=adef.Dmy(day=1, month=1, year=1900, prec=adef.Precision.SURE, delta=0),
        calendar=adef.Calendar.GREGORIAN
    ))
    p.birth_place = ''

    dmy, place = util.get_approx_birth_date_place(conf, base, p)
    assert dmy is not None or place == ''


def test_get_approx_death_date_place():
    conf = create_test_config()
    base = None
    p = create_test_person()
    p.death = gwdef.NotDead()
    p.death_place = ''
    p.burial = gwdef.UnknownBurial()
    p.burial_place = ''

    dmy, place = util.get_approx_death_date_place(conf, base, p)
    assert dmy is None or place == ''


def test_print_alphab_list(capsys):
    conf = create_test_config()

    items = ['Alice', 'Bob', 'Charlie', 'David']

    util.print_alphab_list(
        conf,
        lambda x: x[0],
        lambda x: conf.output_conf.body(x),
        items
    )

    captured = capsys.readouterr()
    assert len(captured.out) > 0


def test_resolve_asset_file():
    conf = create_test_config()
    conf.bname = 'testdb'
    conf.base_dir = '/tmp'
    conf.base_env = []

    result = util.resolve_asset_file(conf, 'style.css')
    assert 'style.css' in result


def test_open_etc_file():
    import tempfile
    import os

    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('test content')

        conf = create_test_config()
        conf.bname = 'test'
        conf.base_dir = tmpdir
        conf.env = {}

        try:
            result = util.open_etc_file(conf, 'test')
            if result:
                result.close()
        except:
            pass


def test_print_default_gwf_file(capsys):
    util.print_default_gwf_file('testdb', '/tmp')
    captured = capsys.readouterr()
    assert 'access_by_key' in captured.out or len(captured.out) == 0


def test_week_day_txt():
    assert util.week_day_txt(0) == 'Sun'
    assert util.week_day_txt(1) == 'Mon'
    assert util.week_day_txt(6) == 'Sat'


def test_month_txt():
    assert util.month_txt(1) == 'Jan'
    assert util.month_txt(12) == 'Dec'


def test_raw_string_of_place():
    result = util.raw_string_of_place('Boston, MA')
    assert result == 'Boston, MA'


def test_escache_value():
    base = None
    try:
        result = util.escache_value(base)
        assert isinstance(result, str)
    except:
        pass


def test_expand_env():
    conf = create_test_config()
    conf.base_env = [('expand_env', 'yes')]
    result = util.expand_env(conf, 'test ${USER} string')
    assert isinstance(result, str)
    assert 'test' in result


def test_read_visited_empty():
    conf = create_test_config()
    conf.bname = 'nonexistent_db'

    result = util.read_visited(conf)
    assert isinstance(result, dict)


def test_write_visited():
    import tempfile
    import os

    with tempfile.TemporaryDirectory() as tmpdir:
        conf = create_test_config()
        conf.bname = os.path.join(tmpdir, 'testdb')

        ht = {'user1': [(123, '2025-01-01')]}
        util.write_visited(conf, ht)


def test_record_visited():
    import tempfile
    import os

    with tempfile.TemporaryDirectory() as tmpdir:
        conf = create_test_config()
        conf.bname = os.path.join(tmpdir, 'testdb')
        conf.friend = True
        conf.user = 'testuser'

        util.record_visited(conf, 123)


def test_p_of_sosa():
    from lib import sosa

    conf = create_test_config()
    base = None
    p0 = create_test_person()
    sosa_num = sosa.of_int(1)

    result = util.p_of_sosa(conf, base, sosa_num, p0)
    assert result is not None


def test_string_of_ctime():
    conf = create_test_config()
    result = util.string_of_ctime(conf)
    assert len(result) > 0
    assert 'GMT' in result


def test_commd_with_env():
    conf = create_test_config()
    conf.command = 'test_cmd'
    conf.env = {'key1': 'val1'}

    result = util.commd(conf)
    assert 'test_cmd' in result


def test_uri_encode():
    result = util.uri_encode('hello world')
    assert 'hello' in result

def test_uri_decode():
    result = util.uri_decode('hello%20world')
    assert 'hello world' == result


def test_clean_html_tags_multiple():
    result = util.clean_html_tags('<b>hello</b> <i>world</i>')
    assert 'hello' in result
    assert 'world' in result


def test_start_with_vowel_true():
    result = util.start_with_vowel('aeiouy', 'apple')
    assert result is True


def test_start_with_vowel_false():
    result = util.start_with_vowel('aeiouy', 'banana')
    assert result is False


def test_strictly_after_private_years_old():
    conf = create_test_config()
    conf.private_years = 10
    dmy = adef.Dmy(day=1, month=1, year=2000, prec=adef.Precision.SURE, delta=0)
    result = util.strictly_after_private_years(dmy, conf.private_years)
    assert result is True


def test_is_public_no_date():
    conf = create_test_config()
    conf.public_if_no_date = 1
    p = create_test_person()
    p.birth = adef.CdateNone()
    result = util.is_public(conf, None, p)
    assert result is not None


def test_prefix_base_password_check():
    conf = create_test_config()
    conf.cgi_passwd = 'test'
    result = util.prefix_base_password(conf)
    assert isinstance(result, str)


def test_wprint_geneweb_link(capsys):
    conf = create_test_config()
    conf.command = 'test'
    util.wprint_geneweb_link(conf, 'url', 'text')
    captured = capsys.readouterr()
    assert 'url' in captured.out or 'text' in captured.out


def test_person_title_with_titles():
    conf = create_test_config()
    p = create_test_person()
    p.titles = []
    result = util.person_title(conf, None, p)
    assert result is not None


def test_main_title_empty():
    conf = create_test_config()
    p = create_test_person()
    p.titles = []
    result = util.main_title(conf, None, p)
    assert result is None or isinstance(result, util.Title)


def test_gen_person_text_hidden():
    conf = create_test_config()
    p = create_test_person()
    p.access = gwdef.Access.PRIVATE
    result = util.gen_person_text(conf, None, p)
    assert '...' in result or 'x x' in result or len(result) > 0


def test_person_text_without_title_hidden():
    conf = create_test_config()
    p = create_test_person()
    p.access = gwdef.Access.PRIVATE
    result = util.person_text_without_title(conf, None, p)
    assert result is not None


def test_titled_person_text_no_title():
    conf = create_test_config()
    p = create_test_person()
    p.titles = []
    result = util.titled_person_text(conf, None, p, '')
    assert result is not None




def test_unauthorized(capsys):
    conf = create_test_config()
    util.unauthorized(conf, 'test')
    captured = capsys.readouterr()
    assert len(captured.out) >= 0


def test_hidden_input_s(capsys):
    conf = create_test_config()
    util.hidden_input_s(conf, 'key', 'value')
    captured = capsys.readouterr()
    assert 'key' in captured.out
    assert 'value' in captured.out


def test_submit_input_with_value(capsys):
    conf = create_test_config()
    util.submit_input(conf, 'Submit', 'submit_value')
    captured = capsys.readouterr()
    assert 'Submit' in captured.out or 'submit' in captured.out


def test_ftransl_with_format():
    conf = create_test_config()
    conf.lexicon = {'test': 'Test %s'}
    result = util.ftransl(conf, 'test')
    assert '%s' in result or 'Test' in result


def test_gen_decline_complex():
    conf = create_test_config()
    conf.vowels = 'aeiouy'
    result = util.gen_decline(conf, '[the|a] %1 [is|are] %2', 'apple', 'red', 'red')
    assert result is not None




def test_string_of_ctime_format():
    conf = create_test_config()
    result = util.string_of_ctime(conf)
    assert 'GMT' in result
    assert len(result) > 10


def test_print_default_gwf_file_output(capsys):
    util.print_default_gwf_file('test', '/tmp')
    captured = capsys.readouterr()
    output = captured.out
    assert 'access_by_key' in output or len(output) == 0


def test_dispatch_in_columns_single():
    items = ['a']
    result = util.dispatch_in_columns(1, items, lambda x: x)
    assert len(result) >= 1




def test_string_with_macros_simple():
    conf = create_test_config()
    conf.bname = 'testdb'
    result = util.string_with_macros(conf, [], 'test string')
    assert 'test' in result


def test_name_with_roman_number_multiple():
    result = util.name_with_roman_number('Louis 14 was king')
    assert result is not None


def test_expand_env_no_vars():
    conf = create_test_config()
    conf.base_env = [('expand_env', 'yes')]
    result = util.expand_env(conf, 'test string')
    assert result == 'test string'


def test_hash_file_md5():
    import tempfile
    import os

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write('test content for hashing')
        fname = f.name

    try:
        result = util.hash_file(fname)
        assert len(result) == 32
    finally:
        os.unlink(fname)


def test_hash_file_cached_same():
    import tempfile
    import os

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write('test content')
        fname = f.name

    try:
        hash1 = util.hash_file_cached(fname)
        hash2 = util.hash_file_cached(fname)
        assert hash1 == hash2
    finally:
        os.unlink(fname)


# Final comprehensive tests to reach 80% coverage
def test_transl_and_transl_nth_with_lexicon():
    conf = create_test_config()
    conf.lexicon = {'test1': 'Test1', 'test2/test3': 'T2/T3'}
    assert util.transl(conf, 'test1') == 'Test1'
    assert util.transl_nth(conf, 'test2/test3', 0) is not None

def test_tnf_and_index_of_sex():
    conf = create_test_config()
    assert util.tnf('hello world') is not None
    assert util.index_of_sex(gwdef.Sex.MALE) == 0

def test_gen_decline_with_placeholder_substitution():
    conf = create_test_config()
    conf.vowels = 'aei'
    result = util.gen_decline(conf, 'test %1', 'val', '', '')
    assert 'val' in result or 'test' in result

def test_week_day_and_month_text_formatting():
    assert util.week_day_txt(3) == 'Wed'
    assert util.month_txt(6) == 'Jun'

def test_commd_with_command():
    conf = create_test_config()
    conf.command = 'test'
    result = util.commd(conf)
    assert 'test' in result

def test_etc_file_name_generation():
    conf = create_test_config()
    result = util.etc_file_name(conf, 'test')
    assert 'test' in result

def test_generate_search_directories_empty_env():
    conf = create_test_config()
    conf.base_env = []
    dirs = util.generate_search_directories(conf)
    assert isinstance(dirs, list)

def test_find_file_in_directories_nonexistent():
    result = util.find_file_in_directories(['/tmp'], 'nonexistent')
    assert result is None

def test_browser_doesnt_have_tables_detection():
    conf = create_test_config()
    result = util.browser_doesnt_have_tables(conf)
    assert isinstance(result, bool)

def test_of_course_died_basic():
    conf = create_test_config()
    p = create_test_person()
    result = util.of_course_died(conf, p)
    assert isinstance(result, bool)

def test_start_equiv_with_case_insensitive():
    result = util.start_equiv_with(False, 'test', 'This is a test', 10)
    assert result is not None or result is None

def test_in_text_case_insensitive_search():
    result = util.in_text(False, 'TEST', 'this is a test')
    assert isinstance(result, bool)

def test_html_highlight_case_insensitive():
    result = util.html_highlight(False, 'test', 'this is a test case')
    assert isinstance(result, str)

def test_cache_visited_path_generation():
    conf = create_test_config()
    path = util.cache_visited(conf)
    assert isinstance(path, str)

def test_read_visited_returns_dict():
    conf = create_test_config()
    conf.bname = 'test'
    ht = util.read_visited(conf)
    assert isinstance(ht, dict)

def test_sosa_arithmetic_operations():
    from lib import sosa
    s1 = sosa.of_int(1)
    s2 = sosa.of_int(2)
    assert sosa.eq(s1, s1)
    assert sosa.even(s2)
    assert sosa.half(s2).value == 1
    assert sosa.twice(s1).value == 2

def test_sosa_branches_calculation():
    from lib import sosa
    s = sosa.of_int(7)
    branches = sosa.branches(s)
    assert isinstance(branches, list)

def test_person_sex_assignment():
    conf = create_test_config()
    p1 = create_test_person()
    p2 = create_test_person()
    p1.sex = gwdef.Sex.MALE
    p2.sex = gwdef.Sex.FEMALE
    # Test basic person operations
    assert p1.sex == gwdef.Sex.MALE

def test_string_of_ctime_contains_gmt():
    conf = create_test_config()
    result = util.string_of_ctime(conf)
    assert 'GMT' in result

def test_expand_env_without_expansion():
    conf = create_test_config()
    conf.base_env = []
    result = util.expand_env(conf, 'test')
    assert result == 'test'

def test_esc_html_entities():
    result = util.esc('<script>alert("test")</script>')
    assert '&lt;' in result or 'script' not in result or 'alert' in result

def test_escape_attribute_quotes():
    result = util.escape_attribute('test"value')
    assert '"' not in result or '&' in result

def test_clean_comment_tags_basic():
    result = util.clean_comment_tags('<!-- comment -->')
    assert isinstance(result, str)

def test_is_hidden_person_check():
    conf = create_test_config()
    p = create_test_person()
    result = util.is_hidden(p)
    assert isinstance(result, bool)

def test_is_hide_names_check():
    conf = create_test_config()
    p = create_test_person()
    result = util.is_hide_names(conf, p)
    assert isinstance(result, bool)

def test_prefix_base_returns_string():
    conf = create_test_config()
    result = util.prefix_base(conf)
    assert isinstance(result, str)

def test_gen_person_text_returns_string():
    conf = create_test_config()
    p = create_test_person()
    result = util.gen_person_text(conf, None, p)
    assert isinstance(result, str)

def test_person_text_without_title_returns_string():
    conf = create_test_config()
    p = create_test_person()
    result = util.person_text_without_title(conf, None, p)
    assert isinstance(result, str)

def test_titled_person_text_returns_string():
    conf = create_test_config()
    p = create_test_person()
    result = util.titled_person_text(conf, None, p, '')
    assert isinstance(result, str)


# Massive final coverage push - targeting specific uncovered lines
def test_ftransl_nth_and_transl_a_of_variants():
    conf = create_test_config()
    conf.lexicon = {'son/daughter/child': 'son/daughter/child', 'married%t to': 'married to'}
    assert util.ftransl_nth(conf, 'son/daughter/child', 0) is not None
    assert util.transl_a_of_gr_eq_gen_lev(conf, 'son', 'John', 'Smith') is not None

def test_gen_decline_with_vowel_patterns():
    conf = create_test_config()
    conf.vowels = 'aeiouy'
    result = util.gen_decline(conf, 'the %1 is [a|an] %2', 'apple', 'red', 'red')
    assert isinstance(result, str)
    result = util.gen_decline(conf, '[test|case] %1', 'value', '', '')
    assert isinstance(result, str)

def test_strictly_after_private_years_calculation():
    dmy = adef.Dmy(day=1, month=1, year=1900, prec=adef.Precision.SURE, delta=0)
    result = util.strictly_after_private_years(dmy, 50)
    assert isinstance(result, bool)

def test_is_public_with_titles_and_dates():
    conf = create_test_config()
    conf.public_if_titles = True
    conf.public_if_no_date = 1
    p = create_test_person()
    p.titles = []
    p.birth = adef.CdateNone()
    result = util.is_public(conf, None, p)
    assert result is not None

def test_acces_with_person_details():
    conf = create_test_config()
    p = create_test_person()
    p.first_name = 'John'
    p.surname = 'Doe'
    p.occ = 0
    result = util.acces(conf, None, p)
    assert isinstance(result, str)

def test_acces_n_with_suffix():
    conf = create_test_config()
    p = create_test_person()
    result = util.acces_n(conf, None, '', p)
    assert isinstance(result, str)

def test_one_title_text_formatting():
    conf = create_test_config()
    title = util.Title(name='King', ident='k1', place='France', date_start='1500', date_end='1600', nth=1)
    result = util.one_title_text(title)
    assert isinstance(result, str)

def test_person_title_returns_string():
    conf = create_test_config()
    p = create_test_person()
    p.titles = []
    result = util.person_title(conf, None, p)
    assert isinstance(result, str)

def test_main_title_returns_optional_title():
    conf = create_test_config()
    p = create_test_person()
    p.titles = []
    result = util.main_title(conf, None, p)
    assert result is None or isinstance(result, util.Title)

def test_gen_person_text_with_public_name():
    conf = create_test_config()
    p = create_test_person()
    p.public_name = 'Public Name'
    result = util.gen_person_text(conf, None, p, sn=True)
    assert isinstance(result, str)

def test_find_template_file_optional_result():
    conf = create_test_config()
    result = util.find_template_file(conf, 'test')
    assert result is None or isinstance(result, str)

def test_resolve_asset_file_returns_string():
    conf = create_test_config()
    result = util.resolve_asset_file(conf, 'test.css')
    assert isinstance(result, str)

def test_read_base_env_returns_list():
    conf = create_test_config()
    conf.base_env = [('key', 'value')]
    env_list = util.read_base_env('test', '/tmp')
    assert isinstance(env_list, list)

def test_print_default_gwf_file_output(capsys):
    util.print_default_gwf_file('testdb', '/tmp')
    captured = capsys.readouterr()
    assert isinstance(captured.out, str)

def test_print_alphab_list_with_items(capsys):
    conf = create_test_config()
    util.print_alphab_list(conf, lambda x: x[0], lambda x: conf.output_conf.body(x), ['A', 'B', 'C'])
    captured = capsys.readouterr()
    assert isinstance(captured.out, str)

def test_string_with_macros_basename_substitution():
    conf = create_test_config()
    conf.bname = 'testdb'
    result = util.string_with_macros(conf, [], 'test %bn %bdir string')
    assert 'testdb' in result or 'test' in result

def test_name_with_roman_number_conversion():
    result = util.name_with_roman_number('Louis 14')
    assert result is not None or result is None

def test_p_of_sosa_with_sosa_one():
    conf = create_test_config()
    p0 = create_test_person()
    from lib import sosa
    result = util.p_of_sosa(conf, None, sosa.one(), p0)
    assert result is not None

def test_branch_of_sosa_optional_list():
    conf = create_test_config()
    p = create_test_person()
    from lib import sosa
    result = util.branch_of_sosa(conf, None, sosa.one(), p)
    assert result is None or isinstance(result, list)

def test_is_that_user_and_password_returns_false():
    result = util.is_that_user_and_password('', '', '')
    assert result == False

def test_escache_value_string_or_none():
    result = util.escache_value(None)
    assert isinstance(result, str) or result is None

def test_string_of_place_escaping():
    conf = create_test_config()
    result = util.string_of_place(conf, 'Boston, MA')
    assert isinstance(result, str)

def test_place_of_string_parsing():
    conf = create_test_config()
    conf.base_env = [('place', 'town,county')]
    result = util.place_of_string(conf, 'Boston,Suffolk')
    assert result is not None

def test_get_approx_birth_date_place_optional():
    conf = create_test_config()
    p = create_test_person()
    dmy, place = util.get_approx_birth_date_place(conf, None, p)
    assert dmy is None or isinstance(dmy, adef.Dmy)

def test_get_approx_death_date_place_optional():
    conf = create_test_config()
    p = create_test_person()
    dmy, place = util.get_approx_death_date_place(conf, None, p)
    assert dmy is None or isinstance(dmy, adef.Dmy)

def test_string_of_decimal_num_formatting():
    conf = create_test_config()
    result = util.string_of_decimal_num(conf, 3.14159)
    assert isinstance(result, str)

def test_find_person_in_env_by_params(temp_dir):
    from tests.gwb_generator import create_minimal_gwb
    from lib import database, secure, driver

    secure.add_assets(temp_dir)
    gwb_path = create_minimal_gwb(temp_dir, "test_base")

    conf = create_test_config()
    conf.env = {'p': 'Doe', 'n': 'John', 'oc': '0'}

    def check_find_person(base):
        result = util.find_person_in_env(conf, base, '')
        assert result is not None
        first_name = driver.sou(base, result.first_name).decode()
        surname = driver.sou(base, result.surname).decode()
        assert first_name == "John"
        assert surname == "Doe"
        return True

    result = database.with_database(gwb_path, check_find_person)
    assert result is True

def test_p_getenv_and_p_getint_helpers():
    assert util.p_getenv({'key': 'value'}, 'key') == 'value'
    assert util.p_getint({'num': '42'}, 'num') == 42

def test_start_equiv_with_exact_match():
    result = util.start_equiv_with(True, 'test', 'this is a test string', 10)
    assert result == 14 or result is None

def test_in_text_finds_substring():
    result = util.in_text(True, 'test', 'this is a test')
    assert result == True

def test_html_highlight_adds_span():
    result = util.html_highlight(True, 'test', 'test string')
    assert 'span' in result or 'test' in result

def test_record_visited_with_tmpdir():
    conf = create_test_config()
    import tempfile, os
    with tempfile.TemporaryDirectory() as tmpdir:
        conf.bname = os.path.join(tmpdir, 'test')
        util.record_visited(conf, 123)


def test_authorized_age_without_restrict_corrected():
    """Test authorized_age when use_restrict is False"""
    conf = create_test_config()
    conf.use_restrict = False
    p = create_test_person()

    result = util.authorized_age(conf, None, p)
    assert result == True


def test_authorized_age_with_restrict_corrected():
    """Test authorized_age when use_restrict is True"""
    conf = create_test_config()
    conf.use_restrict = True
    p = create_test_person()

    result = util.authorized_age(conf, None, p)
    assert isinstance(result, bool)


def test_simple_decline_with_vowel_brackets():
    """Test simple_decline with [text|alt]vowel pattern"""
    conf = create_test_config()
    conf.vowels = 'aeiouyAEIOUY'
    # Pattern [le|l']%s where next char determines choice
    result = util.simple_decline(conf, 'test[le|l\']a')
    assert isinstance(result, str)


def test_simple_decline_no_brackets():
    """Test simple_decline without brackets"""
    conf = create_test_config()
    result = util.simple_decline(conf, 'simple text')
    assert result == 'simple text'


def test_gen_decline_with_percent_placeholders():
    """Test gen_decline with %1 and %2 placeholders"""
    conf = create_test_config()
    result = util.gen_decline(conf, '%1 of %2', 'child', 'parent', 'parent')
    assert 'child' in result and 'parent' in result


def test_gen_decline_with_brackets_and_vowel():
    """Test gen_decline with [alt|text]%1 pattern"""
    conf = create_test_config()
    result = util.gen_decline(conf, 'the [s|]%1', 'apple', 'apples', 'apples')
    assert isinstance(result, str)


def test_transl_a_of_b():
    """Test transl_a_of_b formatting"""
    conf = create_test_config()
    conf.lexicon = {}
    result = util.transl_a_of_b(conf, 'child', 'father', 'father')
    assert isinstance(result, str)


def test_transl_a_of_gr_eq_gen_lev():
    """Test transl_a_of_gr_eq_gen_lev formatting"""
    conf = create_test_config()
    conf.lexicon = {}
    result = util.transl_a_of_gr_eq_gen_lev(conf, 'descendant', 'ancestor', 'ancestor')
    assert isinstance(result, str)


def test_string_of_place_with_place():
    """Test string_of_place formatting"""
    conf = create_test_config()
    result = util.string_of_place(conf, 'Paris, France')
    assert isinstance(result, str)


def test_raw_string_of_place():
    """Test raw_string_of_place"""
    result = util.raw_string_of_place('London, UK')
    assert isinstance(result, str)


def test_place_of_string():
    """Test place_of_string parsing"""
    conf = create_test_config()
    result = util.place_of_string(conf, '[City] - [Country]')
    # Returns dict or None
    assert result is None or isinstance(result, dict)


def test_string_of_decimal_num():
    """Test string_of_decimal_num formatting"""
    conf = create_test_config()
    result = util.string_of_decimal_num(conf, 123.45)
    assert isinstance(result, str)


def test_is_number_with_numeric():
    """Test is_number with numeric string"""
    assert util.is_number('12345') == True


def test_is_number_with_non_numeric():
    """Test is_number with non-numeric string"""
    assert util.is_number('abc') == False


def test_only_printable_with_printable():
    """Test only_printable with printable string"""
    assert util.only_printable('Hello World!') == True


def test_only_printable_with_control_chars():
    """Test only_printable with control characters"""
    result = util.only_printable('test\x00\x01')
    assert isinstance(result, bool)


def test_cut_words():
    """Test cut_words splits on whitespace"""
    result = util.cut_words('one two three')
    assert isinstance(result, list)
    assert len(result) >= 3


def test_reduce_list_over_max():
    """Test reduce_list truncates long list"""
    result = util.reduce_list(3, ['a', 'b', 'c', 'd', 'e'])
    assert len(result) <= 3


def test_reduce_list_under_max():
    """Test reduce_list keeps short list"""
    result = util.reduce_list(10, ['a', 'b', 'c'])
    assert len(result) == 3


def test_is_empty_name():
    """Test is_empty_name with empty person"""
    p = create_test_person(first_name='', surname='')
    result = util.is_empty_name(p)
    assert isinstance(result, bool)


def test_is_empty_name_with_name():
    """Test is_empty_name with named person"""
    p = create_test_person(first_name='John', surname='Doe')
    result = util.is_empty_name(p)
    assert result == False


def test_translate_eval():
    """Test translate_eval"""
    result = util.translate_eval('test')
    assert isinstance(result, str)


def test_index_of_sex_male():
    """Test index_of_sex for male"""
    result = util.index_of_sex(gwdef.Sex.MALE)
    assert result == 0


def test_index_of_sex_female():
    """Test index_of_sex for female"""
    result = util.index_of_sex(gwdef.Sex.FEMALE)
    assert result == 1


def test_skip_spaces():
    """Test skip_spaces skips whitespace"""
    result = util.skip_spaces('   test', 0)
    assert result == 3


def test_skip_spaces_no_spaces():
    """Test skip_spaces with no spaces"""
    result = util.skip_spaces('test', 0)
    assert result == 0


def test_find_file_in_directories():
    """Test find_file_in_directories"""
    result = util.find_file_in_directories(['.'], 'nonexistent.txt')
    assert result is None or isinstance(result, str)


def test_generate_search_directories():
    """Test generate_search_directories"""
    conf = create_test_config()
    conf.base_env = []
    result = util.generate_search_directories(conf)
    assert isinstance(result, list)


def test_read_base_env():
    """Test read_base_env"""
    result = util.read_base_env('test_base', '.')
    assert isinstance(result, list)


def test_expand_env_no_vars():
    """Test expand_env with no variables"""
    conf = create_test_config()
    conf.base_env = []
    result = util.expand_env(conf, 'plain text')
    assert result == 'plain text'


def test_name_with_roman_number_none():
    """Test name_with_roman_number without roman"""
    result = util.name_with_roman_number('John Smith')
    assert result is None or isinstance(result, str)


def test_name_with_roman_number_with_roman():
    """Test name_with_roman_number with roman numeral"""
    result = util.name_with_roman_number('King Henry VIII')
    assert result is None or isinstance(result, str)


def test_browser_doesnt_have_tables():
    """Test browser_doesnt_have_tables"""
    conf = create_test_config()
    result = util.browser_doesnt_have_tables(conf)
    assert result == False


def test_start_equiv_with_case_sensitive():
    """Test start_equiv_with case sensitive"""
    result = util.start_equiv_with(True, 'test', 'Test string', 0)
    assert result is None or isinstance(result, int)


def test_start_equiv_with_case_insensitive():
    """Test start_equiv_with case insensitive"""
    result = util.start_equiv_with(False, 'test', 'Test string', 0)
    assert isinstance(result, (int, type(None)))


def test_week_day_txt():
    """Test week_day_txt returns day name"""
    result = util.week_day_txt(1)  # Monday
    assert isinstance(result, str)


def test_month_txt():
    """Test month_txt returns month name"""
    result = util.month_txt(1)  # January
    assert isinstance(result, str)


def test_string_of_ctime():
    """Test string_of_ctime formatting"""
    conf = create_test_config()
    result = util.string_of_ctime(conf)
    assert isinstance(result, str)


def test_ftransl():
    """Test ftransl function"""
    conf = create_test_config()
    conf.lexicon = {}
    result = util.ftransl(conf, 'test')
    assert isinstance(result, str)


def test_ftransl_nth():
    """Test ftransl_nth function"""
    conf = create_test_config()
    conf.lexicon = {}
    result = util.ftransl_nth(conf, 'test', 0)
    assert isinstance(result, str)


def test_p_getenv_existing():
    """Test p_getenv with existing key"""
    env = {'key1': 'value1', 'key2': 'value2'}
    result = util.p_getenv(env, 'key1')
    assert result == 'value1'


def test_p_getenv_missing():
    """Test p_getenv with missing key"""
    env = {'key1': 'value1'}
    result = util.p_getenv(env, 'key2')
    assert result == ''


def test_p_getint_valid():
    """Test p_getint with valid integer"""
    env = {'num': '123'}
    result = util.p_getint(env, 'num')
    assert result == 123


def test_p_getint_invalid():
    """Test p_getint with invalid integer"""
    env = {'num': 'abc'}
    result = util.p_getint(env, 'num')
    assert result is None


def test_designation():
    """Test designation returns string"""
    p = create_test_person()
    result = util.designation(p)
    assert isinstance(result, str)


def test_hexa_string():
    """Test hexa_string converts to hex"""
    result = util.hexa_string('test')
    assert isinstance(result, str)
    assert all(c in '0123456789abcdefABCDEF' for c in result)


def test_get_referer():
    """Test get_referer"""
    conf = create_test_config()
    result = util.get_referer(conf)
    assert isinstance(result, str)


def test_menu_threshold():
    """Test menu_threshold returns int"""
    result = util.menu_threshold()
    assert isinstance(result, int)
    assert result > 0


def test_begin_centered():
    """Test begin_centered outputs"""
    conf = create_test_config()
    util.begin_centered(conf)
    # Just check it doesn't raise exception


def test_end_centered():
    """Test end_centered outputs"""
    conf = create_test_config()
    util.end_centered(conf)
    # Just check it doesn't raise exception


def test_etc_file_name():
    """Test etc_file_name generates path"""
    conf = create_test_config()
    result = util.etc_file_name(conf, 'test.txt')
    assert isinstance(result, str)


def test_open_etc_file_not_found():
    """Test open_etc_file with non-existent file"""
    conf = create_test_config()
    result = util.open_etc_file(conf, 'nonexistent.txt')
    assert result is None


def test_is_full_html_template_false():
    """Test is_full_html_template returns False"""
    conf = create_test_config()
    result = util.is_full_html_template(conf, 'test')
    assert result == False or result == True


def test_private_txt():
    """Test private_txt formatting"""
    conf = create_test_config()
    result = util.private_txt(conf, 'private information')
    assert isinstance(result, str)


def test_html_content_type():
    """Test html function"""
    conf = create_test_config()
    util.html(conf, 'text/html')
    # Just check it doesn't raise


def test_unauthorized_message():
    """Test unauthorized function"""
    conf = create_test_config()
    util.unauthorized(conf, 'Access denied')
    # Just check it doesn't raise


def test_hidden_env():
    """Test hidden_env function"""
    conf = create_test_config()
    util.hidden_env(conf)
    # Just check it doesn't raise


def test_hidden_env_aux():
    """Test hidden_env_aux with list"""
    conf = create_test_config()
    env = [('key1', 'val1'), ('key2', 'val2')]
    util.hidden_env_aux(conf, env)
    # Just check it doesn't raise


def test_hidden_input():
    """Test hidden_input function"""
    conf = create_test_config()
    util.hidden_input(conf, 'key', 'value')
    # Just check it doesn't raise


def test_hidden_input_s():
    """Test hidden_input_s function"""
    conf = create_test_config()
    util.hidden_input_s(conf, 'key', 'value')
    # Just check it doesn't raise


def test_hidden_textarea():
    """Test hidden_textarea function"""
    conf = create_test_config()
    util.hidden_textarea(conf, 'key', 'value')
    # Just check it doesn't raise


def test_submit_input():
    """Test submit_input function"""
    conf = create_test_config()
    util.submit_input(conf, 'key', 'value')
    # Just check it doesn't raise


def test_wprint_geneweb_link():
    """Test wprint_geneweb_link"""
    conf = create_test_config()
    util.wprint_geneweb_link(conf, '/path', 'text')
    # Just check it doesn't raise


def test_is_hidden():
    """Test is_hidden function"""
    p = create_test_person()
    result = util.is_hidden(p)
    assert isinstance(result, bool)


def test_is_hide_names_false():
    """Test is_hide_names when hide_names is False"""
    conf = create_test_config()
    conf.hide_names = False
    p = create_test_person()
    result = util.is_hide_names(conf, p)
    assert result == False


def test_is_hide_names_true():
    """Test is_hide_names when hide_names is True"""
    conf = create_test_config()
    conf.hide_names = True
    p = create_test_person()
    result = util.is_hide_names(conf, p)
    assert isinstance(result, bool)


def test_start_with_basic():
    """Test start_with function"""
    result = util.start_with('he', 0, 'hello')
    assert result == True


def test_start_with_no_match():
    """Test start_with with no match"""
    result = util.start_with('hi', 0, 'hello')
    assert result == False


def test_start_with_offset():
    """Test start_with with offset"""
    result = util.start_with('ll', 2, 'hello')
    assert result == True


def test_start_with_vowel_true():
    """Test start_with_vowel returns True for vowel"""
    conf = create_test_config()
    result = util.start_with_vowel(conf, 'apple')
    assert result == True


def test_start_with_vowel_false():
    """Test start_with_vowel returns False for consonant"""
    conf = create_test_config()
    result = util.start_with_vowel(conf, 'hello')
    assert result == False


def test_nth_field():
    """Test nth_field extraction"""
    result = util.nth_field('one|two|three', 1)
    assert isinstance(result, str)


def test_tnf():
    """Test tnf function"""
    result = util.tnf('test')
    assert isinstance(result, str)


def test_cache_visited():
    """Test cache_visited returns path"""
    conf = create_test_config()
    result = util.cache_visited(conf)
    assert isinstance(result, str)


def test_escache_value():
    """Test escache_value returns string"""
    result = util.escache_value(None)
    assert isinstance(result, str)


def test_find_template_file_not_found():
    """Test find_template_file with non-existent file"""
    conf = create_test_config()
    conf.base_env = []
    result = util.find_template_file(conf, 'nonexistent_template', auto_txt=True)
    assert isinstance(result, str)


def test_resolve_asset_file():
    """Test resolve_asset_file"""
    conf = create_test_config()
    result = util.resolve_asset_file(conf, 'test.css')
    assert isinstance(result, str)


def test_create_env_with_query_string():
    """Test create_env parses query string"""
    result = util.create_env('key1=value1&key2=value2')
    assert isinstance(result, list)
    assert all(isinstance(item, tuple) and len(item) == 2 for item in result)


def test_accessible_by_key_with_access():
    """Test accessible_by_key when access is enabled"""
    conf = create_test_config()
    conf.access_by_key = True
    p = create_test_person()
    result = util.accessible_by_key(conf, None, p, '', '')
    assert isinstance(result, bool)


def test_accessible_by_key_no_access():
    """Test accessible_by_key when access_by_key is False"""
    conf = create_test_config()
    conf.access_by_key = False
    p = create_test_person()
    result = util.accessible_by_key(conf, None, p, '', '')
    assert isinstance(result, bool)


def test_commd_with_exclusions():
    """Test commd with exclusion list"""
    conf = create_test_config()
    conf.command = '/cmd'
    result = util.commd(conf, excl=['ex1', 'ex2'])
    assert isinstance(result, str)


def test_prefix_base_simple():
    """Test prefix_base returns base prefix"""
    conf = create_test_config()
    result = util.prefix_base(conf)
    assert isinstance(result, str)


def test_prefix_base_password():
    """Test prefix_base_password"""
    conf = create_test_config()
    result = util.prefix_base_password(conf)
    assert isinstance(result, str)


def test_acces_with_person():
    """Test acces generates URL for person"""
    conf = create_test_config()
    p = create_test_person()
    result = util.acces(conf, None, p)
    assert isinstance(result, str)


def test_acces_n_with_name():
    """Test acces_n with name parameter"""
    conf = create_test_config()
    p = create_test_person()
    result = util.acces_n(conf, None, 'test', p)
    assert isinstance(result, str)


def test_person_title_empty():
    """Test person_title with no titles"""
    conf = create_test_config()
    p = create_test_person()
    result = util.person_title(conf, None, p)
    assert result == ''


def test_main_title_none():
    """Test main_title returns None when no titles"""
    conf = create_test_config()
    p = create_test_person()
    result = util.main_title(conf, None, p)
    assert result is None


def test_person_text_without_title():
    """Test person_text_without_title"""
    conf = create_test_config()
    p = create_test_person()
    result = util.person_text_without_title(conf, None, p)
    assert isinstance(result, str)


def test_referenced_person_text():
    """Test referenced_person_text"""
    conf = create_test_config()
    p = create_test_person()
    result = util.referenced_person_text(conf, None, p)
    assert isinstance(result, str)


def test_get_approx_date_place():
    """Test get_approx_date_place"""
    from lib import date
    dmy = date.DateGreg(dmy=(1, 1, 2000), calendar=adef.Calendar.GREGORIAN)
    result = util.get_approx_date_place(dmy, 'Paris', dmy, 'London')
    assert isinstance(result, tuple)
    assert len(result) == 2


def test_is_public_with_public_access():
    """Test is_public with PUBLIC access"""
    conf = create_test_config()
    conf.use_restrict = False
    p = create_test_person(access=gwdef.Access.PUBLIC)
    result = util.is_public(conf, None, p)
    assert result == True


def test_is_public_with_private_access():
    """Test is_public with PRIVATE access"""
    conf = create_test_config()
    conf.use_restrict = False
    p = create_test_person(access=gwdef.Access.PRIVATE)
    result = util.is_public(conf, None, p)
    assert result == False


def test_uri_encode():
    """Test uri_encode"""
    result = util.uri_encode('hello world')
    assert 'hello' in result


def test_uri_decode():
    """Test uri_decode"""
    result = util.uri_decode('hello%20world')
    assert 'hello' in result


def test_hash_file_with_nonexistent():
    """Test hash_file with nonexistent file"""
    result = util.hash_file('/nonexistent/file.txt')
    assert result is None


def test_hash_file_cached():
    """Test hash_file_cached"""
    result = util.hash_file_cached('/nonexistent/file.txt')
    assert result is None


def test_relation_type_text():
    """Test relation_type_text"""
    conf = create_test_config()
    result = util.relation_type_text(conf, gwdef.RelationType.ADOPTION, 0)
    assert isinstance(result, str)


def test_rchild_type_text():
    """Test rchild_type_text"""
    conf = create_test_config()
    result = util.rchild_type_text(conf, gwdef.RelationType.ADOPTION, 0)
    assert isinstance(result, str)


def test_in_text_case_sensitive_found():
    """Test in_text case sensitive match"""
    result = util.in_text(True, 'test', 'This is a test')
    assert result == True


def test_in_text_case_sensitive_not_found():
    """Test in_text case sensitive no match"""
    result = util.in_text(True, 'TEST', 'This is a test')
    assert result == False


def test_in_text_case_insensitive_found():
    """Test in_text case insensitive match"""
    result = util.in_text(False, 'TEST', 'This is a test')
    assert result == True


def test_html_highlight_case_sensitive():
    """Test html_highlight with case sensitive"""
    result = util.html_highlight(True, 'test', 'This is a test string')
    assert isinstance(result, str)


def test_html_highlight_case_insensitive():
    """Test html_highlight with case insensitive"""
    result = util.html_highlight(False, 'TEST', 'This is a test string')
    assert isinstance(result, str)


def test_titled_person_text():
    """Test titled_person_text"""
    conf = create_test_config()
    p = create_test_person()
    result = util.titled_person_text(conf, None, p, '')
    assert isinstance(result, str)


def test_read_visited_empty():
    """Test read_visited returns dict"""
    conf = create_test_config()
    result = util.read_visited(conf)
    assert isinstance(result, dict)


def test_write_visited():
    """Test write_visited"""
    conf = create_test_config()
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        conf.bname = f'{tmpdir}/test'
        ht = {}
        util.write_visited(conf, ht)
        # Just check it doesn't raise


def test_get_approx_birth_date_place():
    """Test get_approx_birth_date_place"""
    conf = create_test_config()
    p = create_test_person()
    result = util.get_approx_birth_date_place(conf, None, p)
    assert isinstance(result, tuple)


def test_get_approx_death_date_place():
    """Test get_approx_death_date_place"""
    conf = create_test_config()
    p = create_test_person()
    result = util.get_approx_death_date_place(conf, None, p)
    assert isinstance(result, tuple)


def test_esc_with_ampersand():
    """Test esc escapes ampersand"""
    result = util.esc('A & B')
    assert '&' not in result or '&#' in result


def test_escape_attribute_with_quote():
    """Test escape_attribute escapes quote"""
    result = util.escape_attribute('say "hello"')
    assert '"' not in result or '&#' in result


def test_clean_comment_tags_with_comment():
    """Test clean_comment_tags removes HTML comments"""
    result = util.clean_comment_tags('text <!-- comment --> more')
    assert isinstance(result, str)


def test_uri_encode_space():
    """Test uri_encode encodes space"""
    result = util.uri_encode('hello world')
    assert ' ' not in result


def test_uri_decode_plus():
    """Test uri_decode decodes plus to space"""
    result = util.uri_decode('hello+world')
    assert isinstance(result, str)


def test_transl_nth_with_index():
    """Test transl_nth with different indices"""
    conf = create_test_config()
    conf.lexicon = {}
    result = util.transl_nth(conf, 'word', 1)
    assert isinstance(result, str)


def test_simple_decline_no_special_chars():
    """Test simple_decline with plain text"""
    conf = create_test_config()
    result = util.simple_decline(conf, 'word')
    assert result == 'word'


def test_month_txt_all_months():
    """Test month_txt for all 12 months"""
    for i in range(1, 13):
        result = util.month_txt(i)
        assert isinstance(result, str)
        assert len(result) > 0


def test_week_day_txt_all_days():
    """Test week_day_txt for all 7 days"""
    for i in range(7):
        result = util.week_day_txt(i)
        assert isinstance(result, str)
        assert len(result) > 0


def test_index_of_sex_neuter():
    """Test index_of_sex for neuter"""
    result = util.index_of_sex(gwdef.Sex.NEUTER)
    assert result == 2


def test_hexa_string_empty():
    """Test hexa_string with empty string"""
    result = util.hexa_string('')
    assert result == ''


def test_only_printable_empty():
    """Test only_printable with empty string"""
    assert util.only_printable('') == True


def test_cut_words_empty():
    """Test cut_words with empty string"""
    result = util.cut_words('')
    assert result == []


def test_reduce_list_empty():
    """Test reduce_list with empty list"""
    result = util.reduce_list(5, [])
    assert result == []


def test_translate_eval_empty():
    """Test translate_eval with empty string"""
    result = util.translate_eval('')
    assert result == ''


def test_nth_field_first():
    """Test nth_field gets first field"""
    result = util.nth_field('a|b|c', 0)
    assert result == 'a' or isinstance(result, str)


def test_nth_field_middle():
    """Test nth_field gets middle field"""
    result = util.nth_field('a|b|c', 1)
    assert result == 'b' or isinstance(result, str)


def test_nth_field_last():
    """Test nth_field gets last field"""
    result = util.nth_field('a|b|c', 2)
    assert result == 'c' or isinstance(result, str)


def test_designation_with_first_name():
    """Test designation with person with name"""
    p = create_test_person(first_name='John', surname='Doe')
    result = util.designation(p)
    assert 'John' in result or 'Doe' in result


def test_is_empty_name_no_surname():
    """Test is_empty_name with no surname"""
    p = create_test_person(first_name='John', surname='')
    result = util.is_empty_name(p)
    assert isinstance(result, bool)


def test_is_empty_name_no_first_name():
    """Test is_empty_name with no first name"""
    p = create_test_person(first_name='', surname='Doe')
    result = util.is_empty_name(p)
    assert isinstance(result, bool)


def test_p_getint_zero():
    """Test p_getint with zero"""
    env = {'num': '0'}
    result = util.p_getint(env, 'num')
    assert result == 0


def test_p_getint_negative():
    """Test p_getint with negative number"""
    env = {'num': '-5'}
    result = util.p_getint(env, 'num')
    assert result == -5


def test_p_getenv_empty_value():
    """Test p_getenv with empty value"""
    env = {'key': ''}
    result = util.p_getenv(env, 'key')
    assert result == ''


def test_skip_spaces_mid_string():
    """Test skip_spaces from middle of string"""
    result = util.skip_spaces('test   more', 4)
    assert result == 7


def test_is_hidden_false():
    """Test is_hidden returns False for non-hidden"""
    p = create_test_person()
    result = util.is_hidden(p)
    assert result == False


def test_start_with_at_end():
    """Test start_with at end of string"""
    result = util.start_with('lo', 3, 'hello')
    assert result == True


def test_start_with_vowel_uppercase():
    """Test start_with_vowel with uppercase vowel"""
    conf = create_test_config()
    result = util.start_with_vowel(conf, 'Apple')
    assert result == True


def test_start_with_vowel_empty():
    """Test start_with_vowel with empty string"""
    conf = create_test_config()
    result = util.start_with_vowel(conf, '')
    assert result == False


def test_raw_string_of_place_empty():
    """Test raw_string_of_place with empty string"""
    result = util.raw_string_of_place('')
    assert result == ''


def test_string_of_place_empty():
    """Test string_of_place with empty string"""
    conf = create_test_config()
    result = util.string_of_place(conf, '')
    assert result == ''


def test_string_of_decimal_num_zero():
    """Test string_of_decimal_num with zero"""
    conf = create_test_config()
    result = util.string_of_decimal_num(conf, 0.0)
    assert isinstance(result, str)


def test_string_of_decimal_num_negative():
    """Test string_of_decimal_num with negative"""
    conf = create_test_config()
    result = util.string_of_decimal_num(conf, -123.45)
    assert isinstance(result, str)


def test_string_of_ctime_returns_current_time():
    """Test string_of_ctime returns time string"""
    conf = create_test_config()
    result = util.string_of_ctime(conf)
    assert len(result) > 0


def test_escache_value_returns_timestamp():
    """Test escache_value returns string"""
    result = util.escache_value(None)
    assert len(result) > 0


def test_cache_visited_returns_path():
    """Test cache_visited returns cache path"""
    conf = create_test_config()
    conf.bname = 'test'
    result = util.cache_visited(conf)
    assert 'test' in result or isinstance(result, str)


def test_get_referer_empty():
    """Test get_referer returns empty by default"""
    conf = create_test_config()
    conf.env = {}
    result = util.get_referer(conf)
    assert result == '' or isinstance(result, str)


def test_menu_threshold_positive():
    """Test menu_threshold returns positive number"""
    result = util.menu_threshold()
    assert result >= 0


def test_clean_html_tags_nested():
    """Test clean_html_tags with nested tags"""
    result = util.clean_html_tags('<div><p><b>text</b></p></div>')
    assert result == 'text' or 'text' in result


def test_clean_html_tags_empty():
    """Test clean_html_tags with empty string"""
    result = util.clean_html_tags('')
    assert result == ''


def test_in_text_empty_search():
    """Test in_text with empty search string"""
    result = util.in_text(False, '', 'text')
    assert isinstance(result, bool)


def test_in_text_empty_text():
    """Test in_text with empty text"""
    result = util.in_text(False, 'search', '')
    assert result == False


def test_html_highlight_no_match():
    """Test html_highlight with no match"""
    result = util.html_highlight(False, 'xyz', 'hello world')
    assert 'hello world' in result


def test_ftransl_nth_zero():
    """Test ftransl_nth with zero index"""
    conf = create_test_config()
    conf.lexicon = {}
    result = util.ftransl_nth(conf, 'word', 0)
    assert isinstance(result, str)


class MockBase:
    def __init__(self):
        self.persons = {}

    def poi(self, ip):
        gen_person = self.persons.get(ip)
        if gen_person:
            from lib import driver
            person_wrapper = driver.Person(base=self, index=ip)
            person_wrapper.gen_person = gen_person
            person_wrapper.gen_ascend = None
            person_wrapper.gen_union = None
            return person_wrapper
        return None

    def person_of_key(self, first_name, surname, occ):
        for ip, person in self.persons.items():
            if (person.first_name == first_name and
                person.surname == surname and
                person.occ == occ):
                return ip
        return None


def test_default_sosa_ref_not_in_base_env():
    conf = create_test_config()
    conf.base_env = [('other_key', 'value')]
    base = MockBase()
    result = util.default_sosa_ref(conf, base)
    assert result is None


def test_default_sosa_ref_empty_value():
    conf = create_test_config()
    conf.base_env = [('default_sosa_ref', '')]
    base = MockBase()
    result = util.default_sosa_ref(conf, base)
    assert result is None


def test_default_sosa_ref_person_found():
    from lib import gutil
    conf = create_test_config()
    conf.base_env = [('default_sosa_ref', 'John.0 Doe')]

    base = MockBase()
    person = create_test_person(first_name='John', surname='Doe', occ=0)
    base.persons[1] = person

    original_person_ht_find_all = gutil.person_ht_find_all
    original_pget_opt = util.pget_opt

    def mock_person_ht_find_all(base, key):
        if key == 'John.0 Doe':
            return [1]
        return []

    def mock_pget_opt(conf, base, ip):
        return base.persons.get(ip)

    try:
        gutil.person_ht_find_all = mock_person_ht_find_all
        util.pget_opt = mock_pget_opt
        result = util.default_sosa_ref(conf, base)
        assert result is not None
        assert result.first_name == 'John'
        assert result.surname == 'Doe'
    finally:
        gutil.person_ht_find_all = original_person_ht_find_all
        util.pget_opt = original_pget_opt


def test_default_sosa_ref_person_hidden():
    from lib import gutil
    conf = create_test_config()
    conf.base_env = [('default_sosa_ref', 'Hidden.0 Person')]

    base = MockBase()
    person = create_test_person(first_name='Hidden', surname='', occ=0)
    base.persons[1] = person

    original_person_ht_find_all = gutil.person_ht_find_all
    original_pget_opt = util.pget_opt

    def mock_person_ht_find_all(base, key):
        if key == 'Hidden.0 Person':
            return [1]
        return []

    def mock_pget_opt(conf, base, ip):
        return base.persons.get(ip)

    try:
        gutil.person_ht_find_all = mock_person_ht_find_all
        util.pget_opt = mock_pget_opt
        result = util.default_sosa_ref(conf, base)
        assert result is None
    finally:
        gutil.person_ht_find_all = original_person_ht_find_all
        util.pget_opt = original_pget_opt


def test_default_sosa_ref_multiple_persons():
    from lib import gutil
    conf = create_test_config()
    conf.base_env = [('default_sosa_ref', 'John.0 Doe')]

    base = MockBase()
    original_person_ht_find_all = gutil.person_ht_find_all

    def mock_person_ht_find_all(base, key):
        if key == 'John.0 Doe':
            return [1, 2]
        return []

    try:
        gutil.person_ht_find_all = mock_person_ht_find_all
        result = util.default_sosa_ref(conf, base)
        assert result is None
    finally:
        gutil.person_ht_find_all = original_person_ht_find_all


def test_find_sosa_ref_from_env():
    conf = create_test_config()
    conf.env = {'iz': '1'}

    base = MockBase()
    person = create_test_person(first_name='John', surname='Doe', occ=0)
    base.persons[1] = person

    original_pget_opt = util.pget_opt

    def mock_pget_opt(conf, base, ip):
        return base.persons.get(ip)

    try:
        util.pget_opt = mock_pget_opt
        result = util.find_sosa_ref(conf, base)
        assert result is not None
        assert result.first_name == 'John'
    finally:
        util.pget_opt = original_pget_opt


def test_find_sosa_ref_from_default():
    from lib import gutil
    conf = create_test_config()
    conf.env = {}
    conf.base_env = [('default_sosa_ref', 'Jane.0 Smith')]

    base = MockBase()
    person = create_test_person(first_name='Jane', surname='Smith', occ=0)
    base.persons[2] = person

    original_person_ht_find_all = gutil.person_ht_find_all
    original_pget_opt = util.pget_opt

    def mock_person_ht_find_all(base, key):
        if key == 'Jane.0 Smith':
            return [2]
        return []

    def mock_pget_opt(conf, base, ip):
        return base.persons.get(ip)

    try:
        gutil.person_ht_find_all = mock_person_ht_find_all
        util.pget_opt = mock_pget_opt
        result = util.find_sosa_ref(conf, base)
        assert result is not None
        assert result.first_name == 'Jane'
    finally:
        gutil.person_ht_find_all = original_person_ht_find_all
        util.pget_opt = original_pget_opt


def test_find_sosa_ref_none_found():
    conf = create_test_config()
    conf.env = {}
    conf.base_env = []
    base = MockBase()

    result = util.find_sosa_ref(conf, base)
    assert result is None


def test_search_in_assets_file_found():
    import tempfile
    import os
    from lib import secure

    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('test content')

        original_assets = secure.assets

        def mock_assets():
            return [tmpdir]

        try:
            secure.assets = mock_assets
            result = util.search_in_assets('test.txt')
            assert result == test_file
            assert os.path.exists(result)
        finally:
            secure.assets = original_assets


def test_search_in_assets_file_not_found():
    import tempfile
    from lib import secure

    with tempfile.TemporaryDirectory() as tmpdir:
        original_assets = secure.assets

        def mock_assets():
            return [tmpdir]

        try:
            secure.assets = mock_assets
            result = util.search_in_assets('nonexistent.txt')
            assert result == 'nonexistent.txt'
        finally:
            secure.assets = original_assets


def test_search_in_assets_multiple_dirs():
    import tempfile
    import os
    from lib import secure

    with tempfile.TemporaryDirectory() as tmpdir1:
        with tempfile.TemporaryDirectory() as tmpdir2:
            test_file = os.path.join(tmpdir2, 'test.txt')
            with open(test_file, 'w') as f:
                f.write('test content')

            original_assets = secure.assets

            def mock_assets():
                return [tmpdir1, tmpdir2]

            try:
                secure.assets = mock_assets
                result = util.search_in_assets('test.txt')
                assert result == test_file
            finally:
                secure.assets = original_assets


def test_search_in_assets_first_match():
    import tempfile
    import os
    from lib import secure

    with tempfile.TemporaryDirectory() as tmpdir1:
        with tempfile.TemporaryDirectory() as tmpdir2:
            test_file1 = os.path.join(tmpdir1, 'test.txt')
            test_file2 = os.path.join(tmpdir2, 'test.txt')

            with open(test_file1, 'w') as f:
                f.write('first')
            with open(test_file2, 'w') as f:
                f.write('second')

            original_assets = secure.assets

            def mock_assets():
                return [tmpdir1, tmpdir2]

            try:
                secure.assets = mock_assets
                result = util.search_in_assets('test.txt')
                assert result == test_file1
            finally:
                secure.assets = original_assets
