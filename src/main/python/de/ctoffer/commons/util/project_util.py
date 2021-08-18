import os


def find_resources(source: str = "main") -> str:
    if source == "main":
        result = find_main_dir()
    elif source == "test":
        result = find_test_dir()
    else:
        raise ValueError(f"Unknown source folder: '{source}'")


def find_main_dir() -> str:
    return find_directory_by_pattern(
        root=os.path.dirname(__file__),
        pattern=["src", "main", "python"],
        index_of_folder=2
    )


def find_test_dir() -> str:
    return find_directory_by_pattern(
        root=os.path.dirname(__file__),
        pattern=["src", "test", "python"],
        index_of_folder=2
    )


def find_directory_by_pattern(root: str, pattern: list, index_of_folder: int = 1) -> str:
    if not root:
        raise AttributeError("'root' must be non-empty string representing the path.")
    if not pattern:
        raise AttributeError(
            "'pattern' must be non-empty list of strings containing the directories of the search pattern."
        )
    if index_of_folder < 1 or type(index_of_folder) != int:
        raise AttributeError("'index_of_folder' must an non-negative integer.")

    filler = pattern[:index_of_folder]
    pattern = os.path.sep.join(pattern)

    normalized_directory = os.path.normpath(root)
    index = os.path.normpath(os.path.dirname(__file__)).rfind(pattern)

    if index is None:
        raise ValueError(
            f"'{pattern[index_of_folder - 1]}' directory was not found in the path {root} based on pattern {pattern}."
        )

    return normpath_join(normalized_directory[:index], *filler)


def normpath_join(*args) -> str:
    return os.path.normpath(os.path.join(*args))
