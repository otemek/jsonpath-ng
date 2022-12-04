from ply.lex import LexToken
import pytest

# import pytest

from jsonpath_ng.lexer import JsonPathLexer, JsonPathLexerError


def token(value, token_type=None) -> LexToken:
    _token: LexToken = LexToken()
    _token.type = token_type if token_type is not None else value
    _token.value = value
    _token.lineno = -1
    _token.lexpos = -1
    return _token


def assert_lex_equiv(_string, stream2):
    # NOTE: lexer fails to reset after call?
    lexer: JsonPathLexer = JsonPathLexer(debug=True)
    stream1: list = list(
        lexer.tokenize(_string)
    )  # Save the stream for debug output when a test fails
    stream2: list = list(stream2)
    assert len(stream1) == len(stream2)
    for token1, token2 in zip(stream1, stream2):
        print(token1, token2)
        assert token1.type == token2.type
        assert token1.value == token2.value


@pytest.mark.parametrize(
    ["token1", "token2"],
    [
        ("$", [token("$", "$")]),
        ('"hello"', [token("hello", "ID")]),
        ("'goodbye'", [token("goodbye", "ID")]),
        ("'doublequote\"'", [token('doublequote"', "ID")]),
        (r'"doublequote\""', [token('doublequote"', "ID")]),
        (r"'singlequote\''", [token("singlequote'", "ID")]),
        ('"singlequote\'"', [token("singlequote'", "ID")]),
        ("fuzz", [token("fuzz", "ID")]),
        ("1", [token(1, "NUMBER")]),
        ("45", [token(45, "NUMBER")]),
        ("-1", [token(-1, "NUMBER")]),
        (" -13 ", [token(-13, "NUMBER")]),
        ('"fuzz.bang"', [token("fuzz.bang", "ID")]),
        ("fuzz.bang", [token("fuzz", "ID"), token(".", "."), token("bang", "ID")]),
        ("fuzz.*", [token("fuzz", "ID"), token(".", "."), token("*", "*")]),
        (
            "fuzz..bang",
            [token("fuzz", "ID"), token("..", "DOUBLEDOT"), token("bang", "ID")],
        ),
        ("&", [token("&", "&")]),
        ("@", [token("@", "ID")]),
        ("`this`", [token("this", "NAMED_OPERATOR")]),
        ("|", [token("|", "|")]),
        ("where", [token("where", "WHERE")]),
    ],
)
def test_simple_inputs(token1, token2):
    assert_lex_equiv(token1, token2)


def test_basic_errors():
    def tokenize(character):
        lexer = JsonPathLexer(debug=True)
        return list(lexer.tokenize(character))

    for _token in ["'\"", "\"'", '`"', "`'", '"`', "'`", "?", "$.foo.bar.#"]:
        with pytest.raises(JsonPathLexerError):
            tokenize(_token)
