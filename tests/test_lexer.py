from ply.lex import LexToken

# import pytest

from jsonpath_ng.lexer import JsonPathLexer, JsonPathLexerError


def token(value, token_type=None):
    _token = LexToken()
    _token.type = token_type if token_type is not None else value
    _token.value = value
    _token.lineno = -1
    _token.lexpos = -1
    return _token


def assert_lex_equiv(_string, stream2):
    # NOTE: lexer fails to reset after call?
    lexer = JsonPathLexer(debug=True)
    stream1 = list(
        lexer.tokenize(_string)
    )  # Save the stream for debug output when a test fails
    stream2 = list(stream2)
    assert len(stream1) == len(stream2)
    for token1, token2 in zip(stream1, stream2):
        print(token1, token2)
        assert token1.type == token2.type
        assert token1.value == token2.value


def test_simple_inputs():
    assert_lex_equiv("$", [token("$", "$")])
    assert_lex_equiv('"hello"', [token("hello", "ID")])
    assert_lex_equiv("'goodbye'", [token("goodbye", "ID")])
    assert_lex_equiv("'doublequote\"'", [token('doublequote"', "ID")])
    assert_lex_equiv(r'"doublequote\""', [token('doublequote"', "ID")])
    assert_lex_equiv(r"'singlequote\''", [token("singlequote'", "ID")])
    assert_lex_equiv('"singlequote\'"', [token("singlequote'", "ID")])
    assert_lex_equiv("fuzz", [token("fuzz", "ID")])
    assert_lex_equiv("1", [token(1, "NUMBER")])
    assert_lex_equiv("45", [token(45, "NUMBER")])
    assert_lex_equiv("-1", [token(-1, "NUMBER")])
    assert_lex_equiv(" -13 ", [token(-13, "NUMBER")])
    assert_lex_equiv('"fuzz.bang"', [token("fuzz.bang", "ID")])
    assert_lex_equiv(
        "fuzz.bang", [token("fuzz", "ID"), token(".", "."), token("bang", "ID")]
    )
    assert_lex_equiv("fuzz.*", [token("fuzz", "ID"), token(".", "."), token("*", "*")])
    assert_lex_equiv(
        "fuzz..bang",
        [token("fuzz", "ID"), token("..", "DOUBLEDOT"), token("bang", "ID")],
    )
    assert_lex_equiv("&", [token("&", "&")])
    assert_lex_equiv("@", [token("@", "ID")])
    assert_lex_equiv("`this`", [token("this", "NAMED_OPERATOR")])
    assert_lex_equiv("|", [token("|", "|")])
    assert_lex_equiv("where", [token("where", "WHERE")])


# def test_basic_errors():
#     def tokenize(s):
#         l = JsonPathLexer(debug=True)
#         return list(l.tokenize(s))

#     self.assertRaises(JsonPathLexerError, tokenize, "'\"")
#     self.assertRaises(JsonPathLexerError, tokenize, '"\'')
#     self.assertRaises(JsonPathLexerError, tokenize, '`"')
#     self.assertRaises(JsonPathLexerError, tokenize, "`'")
#     self.assertRaises(JsonPathLexerError, tokenize, '"`')
#     self.assertRaises(JsonPathLexerError, tokenize, "'`")
#     self.assertRaises(JsonPathLexerError, tokenize, '?')
#     self.assertRaises(JsonPathLexerError, tokenize, '$.foo.bar.#')
