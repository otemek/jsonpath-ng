from jsonpath_ng.jsonpath import Fields, Index, Slice, Descendants, Where, Child
from tests.conftest import check_parse_cases

# TODO: This will be much more effective with a few regression tests and `arbitrary` parse . pretty testing


def test_atomic():
    check_parse_cases(
        [
            ("foo", Fields("foo")),
            ("*", Fields("*")),
            ("baz,bizzle", Fields("baz", "bizzle")),
            ("[1]", Index(1)),
            ("[1:]", Slice(start=1)),
            ("[:]", Slice()),
            ("[*]", Slice()),
            ("[:2]", Slice(end=2)),
            ("[1:2]", Slice(start=1, end=2)),
            ("[5:-2]", Slice(start=5, end=-2)),
        ]
    )


def test_nested():
    check_parse_cases(
        [
            ("foo.baz", Child(Fields("foo"), Fields("baz"))),
            ("foo.baz,bizzle", Child(Fields("foo"), Fields("baz", "bizzle"))),
            ("foo where baz", Where(Fields("foo"), Fields("baz"))),
            ("foo..baz", Descendants(Fields("foo"), Fields("baz"))),
            (
                "foo..baz.bing",
                Descendants(Fields("foo"), Child(Fields("baz"), Fields("bing"))),
            ),
        ]
    )
