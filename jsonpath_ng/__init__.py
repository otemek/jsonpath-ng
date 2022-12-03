
try:
    import tomllib as toml
except ModuleNotFoundError:
    import tomli as toml

def get_version() -> str:
    with open("pyproject.toml", "rb") as fl:
        config = toml.load(fl)
    return config["tool"]["poetry"]["version"]

# Current package version
__version__: str = get_version()
