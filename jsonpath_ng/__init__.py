
try:
    import tomllib as toml
except ModuleNotFoundError:
    import tomli as toml

def get_version() -> str:
    """Get package version
    """
    with open("pyproject.toml", "rb") as file:
        config = toml.load(file)
    return config["tool"]["poetry"]["version"]

# Current package version
__version__: str = get_version()
