# -*- coding: utf-8 -*-

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""
test_jsonpath_ng_ext
----------------------------------

Tests for `jsonpath_ng_ext` module.
"""

from jsonpath_ng import jsonpath  # For setting the global auto_id_field flag
from jsonpath_ng.ext import parser as parser_ext
from tests.conftest import check_cases, check_paths
from functools import partial


# NOTE(sileht): copy of tests/test_jsonpath.py
# to ensure we didn't break jsonpath_ng

check_cases = partial(check_cases, parser_type=parser_ext)
check_paths = partial(check_paths, parser_type=parser_ext)

class TestJsonPath:
    """Tests of the actual jsonpath functionality """

    #
    # Check that the data value returned is good
    #
    # def check_cases(self, test_cases):
    #     # Note that just manually building an AST would avoid this dep and
    #     # isolate the tests, but that would suck a bit
    #     # Also, we coerce iterables, etc, into the desired target type

    #     for string, data, target in test_cases:
    #         print(f'parse("{string}").find({data}) =?= {target}')
    #         result = parser.parse(string).find(data)
    #         if isinstance(target, list):
    #             assert [r.value for r in result] == target
    #         elif isinstance(target, set):
    #             assert set([r.value for r in result]) == target
    #         else:
    #             assert result.value == target

    def test_fields_value(self):
        jsonpath.AUTO_ID_FIELD = None
        check_cases([('foo', {'foo': 'baz'}, ['baz']),
                          ('foo,baz', {'foo': 1, 'baz': 2}, [1, 2]),
                          ('@foo', {'@foo': 1}, [1]),
                          ('*', {'foo': 1, 'baz': 2}, set([1, 2]))])

        jsonpath.AUTO_ID_FIELD = 'id'
        check_cases([('*', {'foo': 1, 'baz': 2}, set([1, 2, '`this`']))])

    def test_root_value(self):
        jsonpath.AUTO_ID_FIELD = None
        check_cases([
            ('$', {'foo': 'baz'}, [{'foo': 'baz'}]),
            ('foo.$', {'foo': 'baz'}, [{'foo': 'baz'}]),
            ('foo.$.foo', {'foo': 'baz'}, ['baz']),
        ])

    def test_this_value(self):
        jsonpath.AUTO_ID_FIELD = None
        check_cases([
            ('`this`', {'foo': 'baz'}, [{'foo': 'baz'}]),
            ('foo.`this`', {'foo': 'baz'}, ['baz']),
            ('foo.`this`.baz', {'foo': {'baz': 3}}, [3]),
        ])

    def test_index_value(self):
        check_cases([
            ('[0]', [42], [42]),
            ('[5]', [42], []),
            ('[2]', [34, 65, 29, 59], [29])
        ])

    def test_slice_value(self):
        check_cases([('[*]', [1, 2, 3], [1, 2, 3]),
                          ('[*]', range(1, 4), [1, 2, 3]),
                          ('[1:]', [1, 2, 3, 4], [2, 3, 4]),
                          ('[:2]', [1, 2, 3, 4], [1, 2])])

        # Funky slice hacks
        check_cases([
            ('[*]', 1, [1]),  # This is a funky hack
            ('[0:]', 1, [1]),  # This is a funky hack
            ('[*]', {'foo': 1}, [{'foo': 1}]),  # This is a funky hack
            ('[*].foo', {'foo': 1}, [1]),  # This is a funky hack
        ])

    def test_child_value(self):
        check_cases([('foo.baz', {'foo': {'baz': 3}}, [3]),
                          ('foo.baz', {'foo': {'baz': [3]}}, [[3]]),
                          ('foo.baz.bizzle', {'foo': {'baz': {'bizzle': 5}}},
                           [5])])

    def test_descendants_value(self):
        check_cases([
            ('foo..baz', {'foo': {'baz': 1, 'bing': {'baz': 2}}}, [1, 2]),
            ('foo..baz', {'foo': [{'baz': 1}, {'baz': 2}]}, [1, 2]),
        ])

    def test_parent_value(self):
        check_cases([('foo.baz.`parent`', {'foo': {'baz': 3}},
                           [{'baz': 3}]),
                          ('foo.`parent`.foo.baz.`parent`.baz.bizzle',
                           {'foo': {'baz': {'bizzle': 5}}}, [5])])

    def test_hyphen_key(self):
        # NOTE(sileht): hyphen is now a operator
        # so to use it has key we must escape it with quote
        # check_cases([('foo.bar-baz', {'foo': {'bar-baz': 3}}, [3]),
        #                  ('foo.[bar-baz,blah-blah]',
        #                   {'foo': {'bar-baz': 3, 'blah-blah': 5}},
        #                   [3, 5])])
        check_cases([('foo."bar-baz"', {'foo': {'bar-baz': 3}}, [3]),
                          ('foo.["bar-baz","blah-blah"]',
                           {'foo': {'bar-baz': 3, 'blah-blah': 5}},
                           [3, 5])])
        # self.assertRaises(lexer.JsonPathLexerError, check_cases,
        #                  [('foo.-baz', {'foo': {'-baz': 8}}, [8])])

    #
    # Check that the paths for the data are correct.
    # FIXME: merge these tests with the above, since the inputs are the same
    # anyhow
    #
    # def check_paths(self, test_cases):
    #     # Note that just manually building an AST would avoid this dep and
    #     # isolate the tests, but that would suck a bit
    #     # Also, we coerce iterables, etc, into the desired target type

    #     for string, data, target in test_cases:
    #         print(f'parse("{string}").find({data}).paths =?= {target}')
    #         result = parser.parse(string).find(data)
    #         if isinstance(target, list):
    #             assert [str(r.full_path) for r in result] == target
    #         elif isinstance(target, set):
    #             assert set([str(r.full_path) for r in result]) == target
    #         else:
    #             assert str(result.path) == target

    def test_fields_paths(self):
        jsonpath.AUTO_ID_FIELD = None
        check_paths([('foo', {'foo': 'baz'}, ['foo']),
                          ('foo,baz', {'foo': 1, 'baz': 2}, ['foo', 'baz']),
                          ('*', {'foo': 1, 'baz': 2}, set(['foo', 'baz']))])

        jsonpath.AUTO_ID_FIELD = 'id'
        check_paths([('*', {'foo': 1, 'baz': 2},
                           set(['foo', 'baz', 'id']))])

    def test_root_paths(self):
        jsonpath.AUTO_ID_FIELD = None
        check_paths([
            ('$', {'foo': 'baz'}, ['$']),
            ('foo.$', {'foo': 'baz'}, ['$']),
            ('foo.$.foo', {'foo': 'baz'}, ['foo']),
        ])

    def test_this_paths(self):
        jsonpath.AUTO_ID_FIELD = None
        check_paths([
            ('`this`', {'foo': 'baz'}, ['`this`']),
            ('foo.`this`', {'foo': 'baz'}, ['foo']),
            ('foo.`this`.baz', {'foo': {'baz': 3}}, ['foo.baz']),
        ])

    def test_index_paths(self):
        check_paths([('[0]', [42], ['[0]']),
                          ('[2]', [34, 65, 29, 59], ['[2]'])])

    def test_slice_paths(self):
        check_paths([('[*]', [1, 2, 3], ['[0]', '[1]', '[2]']),
                          ('[1:]', [1, 2, 3, 4], ['[1]', '[2]', '[3]'])])

    def test_child_paths(self):
        check_paths([('foo.baz', {'foo': {'baz': 3}}, ['foo.baz']),
                          ('foo.baz', {'foo': {'baz': [3]}}, ['foo.baz']),
                          ('foo.baz.bizzle', {'foo': {'baz': {'bizzle': 5}}},
                           ['foo.baz.bizzle'])])

    def test_descendants_paths(self):
        check_paths([('foo..baz', {'foo': {'baz': 1, 'bing': {'baz': 2}}},
                           ['foo.baz', 'foo.bing.baz'])])

    #
    # Check the "auto_id_field" feature
    #
    def test_fields_auto_id(self):
        jsonpath.AUTO_ID_FIELD = "id"
        check_cases([('foo.id', {'foo': 'baz'}, ['foo']),
                          ('foo.id', {'foo': {'id': 'baz'}}, ['baz']),
                          ('foo,baz.id', {'foo': 1, 'baz': 2}, ['foo', 'baz']),
                          ('*.id',
                           {'foo': {'id': 1},
                            'baz': 2},
                           set(['1', 'baz']))])

    def test_root_auto_id(self):
        jsonpath.AUTO_ID_FIELD = 'id'
        check_cases([
            ('$.id', {'foo': 'baz'}, ['$']),  # This is a wonky case that is
                                              # not that interesting
            ('foo.$.id', {'foo': 'baz', 'id': 'bizzle'}, ['bizzle']),
            ('foo.$.baz.id', {'foo': 4, 'baz': 3}, ['baz']),
        ])

    def test_this_auto_id(self):
        jsonpath.AUTO_ID_FIELD = 'id'
        check_cases([
            ('id', {'foo': 'baz'}, ['`this`']),  # This is, again, a wonky case
                                                 # that is not that interesting
            ('foo.`this`.id', {'foo': 'baz'}, ['foo']),
            ('foo.`this`.baz.id', {'foo': {'baz': 3}}, ['foo.baz']),
        ])

    def test_index_auto_id(self):
        jsonpath.AUTO_ID_FIELD = "id"
        check_cases([('[0].id', [42], ['[0]']),
                          ('[2].id', [34, 65, 29, 59], ['[2]'])])

    def test_slice_auto_id(self):
        jsonpath.AUTO_ID_FIELD = "id"
        check_cases([('[*].id', [1, 2, 3], ['[0]', '[1]', '[2]']),
                          ('[1:].id', [1, 2, 3, 4], ['[1]', '[2]', '[3]'])])

    def test_child_auto_id(self):
        jsonpath.AUTO_ID_FIELD = "id"
        check_cases([('foo.baz.id', {'foo': {'baz': 3}}, ['foo.baz']),
                          ('foo.baz.id', {'foo': {'baz': [3]}}, ['foo.baz']),
                          ('foo.baz.id', {'foo': {'id': 'bizzle', 'baz': 3}},
                           ['bizzle.baz']),
                          ('foo.baz.id', {'foo': {'baz': {'id': 'hi'}}},
                           ['foo.hi']),
                          ('foo.baz.bizzle.id',
                           {'foo': {'baz': {'bizzle': 5}}},
                           ['foo.baz.bizzle'])])

    def test_descendants_auto_id(self):
        jsonpath.AUTO_ID_FIELD = "id"
        check_cases([('foo..baz.id',
                           {'foo': {
                               'baz': 1,
                               'bing': {
                                   'baz': 2
                               }
                           }},
                           ['foo.baz',
                            'foo.bing.baz'])])
