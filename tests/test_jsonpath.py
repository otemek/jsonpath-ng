from functools import partial
import unittest

from jsonpath_ng import jsonpath  # For setting the global auto_id_field flag

from jsonpath_ng import parser
from jsonpath_ng.jsonpath import DatumInContext, This, Root, Fields
from jsonpath_ng.lexer import JsonPathLexerError
from tests.conftest import check_cases, check_paths, check_update_cases

check_cases = partial(check_cases, parser_type=parser)
check_paths = partial(check_paths, parser_type=parser)
check_update_cases = partial(check_update_cases, parser_type=parser)


class TestDatumInContext(unittest.TestCase):
    """
    Tests of properties of the DatumInContext and AutoIdForDatum objects
    """

    # @classmethod
    # def setup_class(cls):
    #     logging.basicConfig()

    def test_can_initialize_object(self):

        test_datum1 = DatumInContext(3)
        assert test_datum1.path == This()
        assert test_datum1.full_path == This()

        test_datum2 = DatumInContext(3, path=Root())
        assert test_datum2.path == Root()
        assert test_datum2.full_path == Root()

        test_datum3 = DatumInContext(3, path=Fields("foo"), context="does not matter")
        assert test_datum3.path == Fields("foo")
        assert test_datum3.full_path == Fields("foo")

        test_datum3 = DatumInContext(
            3,
            path=Fields("foo"),
            context=DatumInContext(
                "does not matter", path=Fields("baz"), context="does not matter"
            ),
        )
        assert test_datum3.path == Fields("foo")
        assert test_datum3.full_path == Fields("baz").child(Fields("foo"))

    def test_can_initialize_in_context(self):

        assert DatumInContext(3).in_context(
            path=Fields("foo"), context=DatumInContext("whatever")
        ) == DatumInContext(3, path=Fields("foo"), context=DatumInContext("whatever"))

        assert DatumInContext(3).in_context(
            path=Fields("foo"), context="whatever"
        ).in_context(path=Fields("baz"), context="whatever") == DatumInContext(
            3
        ).in_context(
            path=Fields("foo"),
            context=DatumInContext("whatever").in_context(
                path=Fields("baz"), context="whatever"
            ),
        )

    # def test_AutoIdForDatum_pseudopath(self):
    #     assert AutoIdForDatum(DatumInContext(value=3, path=Fields('foo')), id_field='id').pseudopath == Fields('foo')
    #     assert AutoIdForDatum(DatumInContext(value={'id': 'bizzle'}, path=Fields('foo')), id_field='id').pseudopath == Fields('bizzle')

    #     assert AutoIdForDatum(DatumInContext(value={'id': 'bizzle'}, path=Fields('foo')),
    #                           id_field='id',
    #                           context=DatumInContext(value=3, path=This())).pseudopath == Fields('bizzle')

    #     assert (AutoIdForDatum(DatumInContext(value=3, path=Fields('foo')),
    #                            id_field='id').in_context(DatumInContext(value={'id': 'bizzle'}, path=This()))
    #             ==
    #             AutoIdForDatum(DatumInContext(value=3, path=Fields('foo')),
    #                            id_field='id',
    #                            context=DatumInContext(value={'id': 'bizzle'}, path=This())))

    #     assert (AutoIdForDatum(DatumInContext(value=3, path=Fields('foo')),
    #                            id_field='id',
    #                            context=DatumInContext(value={"id": 'bizzle'},
    #                                                path=Fields('maggle'))).in_context(DatumInContext(value='whatever', path=Fields('miggle')))
    #             ==
    #             AutoIdForDatum(DatumInContext(value=3, path=Fields('foo')),
    #                            id_field='id',
    #                            context=DatumInContext(value={'id': 'bizzle'}, path=Fields('miggle').child(Fields('maggle')))))

    #     assert AutoIdForDatum(DatumInContext(value=3, path=Fields('foo')),
    #                           id_field='id',
    #                           context=DatumInContext(value={'id': 'bizzle'}, path=This())).pseudopath == Fields('bizzle').child(Fields('foo'))


class TestJsonPath(unittest.TestCase):
    """
    Tests of the actual jsonpath functionality
    """

    # @classmethod
    # def setup_class(cls):
    #     logging.basicConfig()

    def test_fields_value(self):
        jsonpath.AUTO_ID_FIELD = None
        check_cases(
            [
                ("foo", {"foo": "baz"}, ["baz"]),
                ("foo,baz", {"foo": 1, "baz": 2}, [1, 2]),
                ("@foo", {"@foo": 1}, [1]),
                ("*", {"foo": 1, "baz": 2}, set([1, 2])),
            ]
        )

        jsonpath.AUTO_ID_FIELD = "id"
        check_cases([("*", {"foo": 1, "baz": 2}, set([1, 2, "`this`"]))])

    def test_root_value(self):
        jsonpath.AUTO_ID_FIELD = None
        check_cases(
            [
                ("$", {"foo": "baz"}, [{"foo": "baz"}]),
                ("foo.$", {"foo": "baz"}, [{"foo": "baz"}]),
                ("foo.$.foo", {"foo": "baz"}, ["baz"]),
            ]
        )

    def test_this_value(self):
        jsonpath.AUTO_ID_FIELD = None
        check_cases(
            [
                ("`this`", {"foo": "baz"}, [{"foo": "baz"}]),
                ("foo.`this`", {"foo": "baz"}, ["baz"]),
                ("foo.`this`.baz", {"foo": {"baz": 3}}, [3]),
            ]
        )

    def test_index_value(self):
        check_cases(
            [
                ("[0]", [42], [42]),
                ("[5]", [42], []),
                ("[2]", [34, 65, 29, 59], [29]),
                ("[0]", None, []),
            ]
        )

    def test_slice_value(self):
        check_cases(
            [
                ("[*]", [1, 2, 3], [1, 2, 3]),
                ("[*]", range(1, 4), [1, 2, 3]),
                ("[1:]", [1, 2, 3, 4], [2, 3, 4]),
                ("[:2]", [1, 2, 3, 4], [1, 2]),
            ]
        )

        # Funky slice hacks
        check_cases(
            [
                ("[*]", 1, [1]),  # This is a funky hack
                ("[0:]", 1, [1]),  # This is a funky hack
                ("[*]", {"foo": 1}, [{"foo": 1}]),  # This is a funky hack
                ("[*].foo", {"foo": 1}, [1]),  # This is a funky hack
            ]
        )

    def test_child_value(self):
        check_cases(
            [
                ("foo.baz", {"foo": {"baz": 3}}, [3]),
                ("foo.baz", {"foo": {"baz": [3]}}, [[3]]),
                ("foo.baz.bizzle", {"foo": {"baz": {"bizzle": 5}}}, [5]),
            ]
        )

    def test_descendants_value(self):
        check_cases(
            [
                ("foo..baz", {"foo": {"baz": 1, "bing": {"baz": 2}}}, [1, 2]),
                ("foo..baz", {"foo": [{"baz": 1}, {"baz": 2}]}, [1, 2]),
            ]
        )

    def test_parent_value(self):
        check_cases(
            [
                ("foo.baz.`parent`", {"foo": {"baz": 3}}, [{"baz": 3}]),
                (
                    "foo.`parent`.foo.baz.`parent`.baz.bizzle",
                    {"foo": {"baz": {"bizzle": 5}}},
                    [5],
                ),
            ]
        )

    def test_hyphen_key(self):
        check_cases(
            [
                ("foo.bar-baz", {"foo": {"bar-baz": 3}}, [3]),
                (
                    "foo.[bar-baz,blah-blah]",
                    {"foo": {"bar-baz": 3, "blah-blah": 5}},
                    [3, 5],
                ),
            ]
        )
        self.assertRaises(
            JsonPathLexerError,
            check_cases,
            [("foo.-baz", {"foo": {"-baz": 8}}, [8])],
        )

    def test_fields_paths(self):
        jsonpath.AUTO_ID_FIELD = None
        check_paths(
            [
                ("foo", {"foo": "baz"}, ["foo"]),
                ("foo,baz", {"foo": 1, "baz": 2}, ["foo", "baz"]),
                ("*", {"foo": 1, "baz": 2}, set(["foo", "baz"])),
            ]
        )

        jsonpath.AUTO_ID_FIELD = "id"
        check_paths([("*", {"foo": 1, "baz": 2}, set(["foo", "baz", "id"]))])

    def test_root_paths(self):
        jsonpath.AUTO_ID_FIELD = None
        check_paths(
            [
                ("$", {"foo": "baz"}, ["$"]),
                ("foo.$", {"foo": "baz"}, ["$"]),
                ("foo.$.foo", {"foo": "baz"}, ["foo"]),
            ]
        )

    def test_this_paths(self):
        jsonpath.AUTO_ID_FIELD = None
        check_paths(
            [
                ("`this`", {"foo": "baz"}, ["`this`"]),
                ("foo.`this`", {"foo": "baz"}, ["foo"]),
                ("foo.`this`.baz", {"foo": {"baz": 3}}, ["foo.baz"]),
            ]
        )

    def test_index_paths(self):
        check_paths([("[0]", [42], ["[0]"]), ("[2]", [34, 65, 29, 59], ["[2]"])])

    def test_slice_paths(self):
        check_paths(
            [
                ("[*]", [1, 2, 3], ["[0]", "[1]", "[2]"]),
                ("[1:]", [1, 2, 3, 4], ["[1]", "[2]", "[3]"]),
            ]
        )

    def test_child_paths(self):
        check_paths(
            [
                ("foo.baz", {"foo": {"baz": 3}}, ["foo.baz"]),
                ("foo.baz", {"foo": {"baz": [3]}}, ["foo.baz"]),
                ("foo.baz.bizzle", {"foo": {"baz": {"bizzle": 5}}}, ["foo.baz.bizzle"]),
            ]
        )

    def test_descendants_paths(self):
        check_paths(
            [
                (
                    "foo..baz",
                    {"foo": {"baz": 1, "bing": {"baz": 2}}},
                    ["foo.baz", "foo.bing.baz"],
                )
            ]
        )

    #
    # Check the "auto_id_field" feature
    #
    def test_fields_auto_id(self):
        jsonpath.AUTO_ID_FIELD = "id"
        check_cases(
            [
                ("foo.id", {"foo": "baz"}, ["foo"]),
                ("foo.id", {"foo": {"id": "baz"}}, ["baz"]),
                ("foo,baz.id", {"foo": 1, "baz": 2}, ["foo", "baz"]),
                ("*.id", {"foo": {"id": 1}, "baz": 2}, set(["1", "baz"])),
            ]
        )

    def test_root_auto_id(self):
        jsonpath.AUTO_ID_FIELD = "id"
        check_cases(
            [
                (
                    "$.id",
                    {"foo": "baz"},
                    ["$"],
                ),  # This is a wonky case that is not that interesting
                ("foo.$.id", {"foo": "baz", "id": "bizzle"}, ["bizzle"]),
                ("foo.$.baz.id", {"foo": 4, "baz": 3}, ["baz"]),
            ]
        )

    def test_this_auto_id(self):
        jsonpath.AUTO_ID_FIELD = "id"
        check_cases(
            [
                (
                    "id",
                    {"foo": "baz"},
                    ["`this`"],
                ),  # This is, again, a wonky case that is not that interesting
                ("foo.`this`.id", {"foo": "baz"}, ["foo"]),
                ("foo.`this`.baz.id", {"foo": {"baz": 3}}, ["foo.baz"]),
            ]
        )

    def test_index_auto_id(self):
        jsonpath.AUTO_ID_FIELD = "id"
        check_cases([("[0].id", [42], ["[0]"]), ("[2].id", [34, 65, 29, 59], ["[2]"])])

    def test_slice_auto_id(self):
        jsonpath.AUTO_ID_FIELD = "id"
        check_cases(
            [
                ("[*].id", [1, 2, 3], ["[0]", "[1]", "[2]"]),
                ("[1:].id", [1, 2, 3, 4], ["[1]", "[2]", "[3]"]),
            ]
        )

    def test_child_auto_id(self):
        jsonpath.AUTO_ID_FIELD = "id"
        check_cases(
            [
                ("foo.baz.id", {"foo": {"baz": 3}}, ["foo.baz"]),
                ("foo.baz.id", {"foo": {"baz": [3]}}, ["foo.baz"]),
                ("foo.baz.id", {"foo": {"id": "bizzle", "baz": 3}}, ["bizzle.baz"]),
                ("foo.baz.id", {"foo": {"baz": {"id": "hi"}}}, ["foo.hi"]),
                (
                    "foo.baz.bizzle.id",
                    {"foo": {"baz": {"bizzle": 5}}},
                    ["foo.baz.bizzle"],
                ),
            ]
        )

    def test_descendants_auto_id(self):
        jsonpath.AUTO_ID_FIELD = "id"
        check_cases(
            [
                (
                    "foo..baz.id",
                    {"foo": {"baz": 1, "bing": {"baz": 2}}},
                    ["foo.baz", "foo.bing.baz"],
                )
            ]
        )

    def test_update_root(self):
        check_update_cases([("foo", "$", "bar", "bar")])

    def test_update_this(self):
        check_update_cases([("foo", "`this`", "bar", "bar")])

    def test_update_fields(self):
        check_update_cases(
            [
                ({"foo": 1}, "foo", 5, {"foo": 5}),
                ({"foo": 1, "bar": 2}, "$.*", 3, {"foo": 3, "bar": 3}),
            ]
        )

    def test_update_child(self):
        check_update_cases(
            [
                ({"foo": "bar"}, "$.foo", "baz", {"foo": "baz"}),
                ({"foo": {"bar": 1}}, "foo.bar", "baz", {"foo": {"bar": "baz"}}),
            ]
        )

    def test_update_where(self):
        check_update_cases(
            [
                (
                    {"foo": {"bar": {"baz": 1}}, "bar": {"baz": 2}},
                    "*.bar where baz",
                    5,
                    {"foo": {"bar": 5}, "bar": {"baz": 2}},
                )
            ]
        )

    def test_update_descendants_where(self):
        check_update_cases(
            [
                (
                    {"foo": {"bar": 1, "flag": 1}, "baz": {"bar": 2}},
                    "(* where flag) .. bar",
                    3,
                    {"foo": {"bar": 3, "flag": 1}, "baz": {"bar": 2}},
                )
            ]
        )

    def test_update_descendants(self):
        check_update_cases(
            [
                ({"somefield": 1}, "$..somefield", 42, {"somefield": 42}),
                (
                    {"outer": {"nestedfield": 1}},
                    "$..nestedfield",
                    42,
                    {"outer": {"nestedfield": 42}},
                ),
                (
                    {"outs": {"bar": 1, "ins": {"bar": 9}}, "outs2": {"bar": 2}},
                    "$..bar",
                    42,
                    {"outs": {"bar": 42, "ins": {"bar": 42}}, "outs2": {"bar": 42}},
                ),
            ]
        )

    def test_update_index(self):
        check_update_cases(
            [(["foo", "bar", "baz"], "[0]", "test", ["test", "bar", "baz"])]
        )

    def test_update_slice(self):
        check_update_cases(
            [(["foo", "bar", "baz"], "[0:2]", "test", ["test", "test", "baz"])]
        )
