

def check_cases(test_cases: list, parser_type):
    # Note that just manually building an AST would avoid this dep and
    # isolate the tests, but that would suck a bit
    # Also, we coerce iterables, etc, into the desired target type

    for string, data, target in test_cases:
        print(f'parse("{string}").find({data}) =?= {target}')
        result = parser_type.parse(string).find(data)
        if isinstance(target, list):
            assert [r.value for r in result] == target
        elif isinstance(target, set):
            assert set([r.value for r in result]) == target
        else:
            assert result.value == target


# Check that the paths for the data are correct.
# FIXME: merge these tests with the above, since the inputs are the same
# anyhow
def check_paths(test_cases, parser_type):
    # Note that just manually building an AST would avoid this dep and
    # isolate the tests, but that would suck a bit
    # Also, we coerce iterables, etc, into the desired target type

    for string, data, target in test_cases:
        print(f'parse("{string}").find({data}).paths =?= {target}')
        result = parser_type.parse(string).find(data)
        if isinstance(target, list):
            assert [str(r.full_path) for r in result] == target
        elif isinstance(target, set):
            assert set([str(r.full_path) for r in result]) == target
        else:
            assert str(result.path) == target