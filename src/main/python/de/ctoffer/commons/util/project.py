import json
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass

import yaml

from commons.creational.singleton import singleton


@dataclass
class Project:
    project_name: str
    project_root: str
    source_directory: str

    main_directory: str
    main_python_source: str
    main_resources: str

    test_directory: str
    test_python_source: str
    test_resources: str


class MavenProject(Project):
    def __init__(self, project_root: str):
        self.project_name = os.path.dirname(project_root)
        self.project_root = project_root
        self.sourced_directory = normpath_join(self.project_root, "src")

        self.main_directory = normpath_join(self.sourced_directory, "main")
        self.main_python_source = normpath_join(self.main_directory, "python")
        self.main_resources = normpath_join(self.main_directory, "resources")

        self.test_directory = normpath_join(self.sourced_directory, "test")
        self.test_python_source = normpath_join(self.test_directory, "python")
        self.test_resources = normpath_join(self.test_directory, "resources")


class ProjectStructure(ABC):
    @abstractmethod
    def analyze(self, file) -> Project:
        raise NotImplementedError


class MavenProjectStructure(ProjectStructure):
    def analyze(self, file) -> MavenProject:
        try:
            main_dir = find_main_dir(file)
            src_dir = os.path.dirname(main_dir)
            root_dir = os.path.dirname(src_dir)
        except ValueError:
            test_dir = find_main_dir(file)
            src_dir = os.path.dirname(test_dir)
            root_dir = os.path.dirname(src_dir)

        return MavenProject(root_dir)


@singleton
class ProjectManager:
    def __init__(self):
        self._project = None
        self._test_mode = False

    @property
    def project(self) -> Project:
        return self._project

    @property
    def is_configured(self):
        return self._project is not None

    def configure(self, file, structure=MavenProjectStructure):
        self._project = structure().analyze(file)
        return self

    @property
    def resources(self):
        if not self.is_configured:
            raise ValueError("This ProjectManager is not initialized")

        if self._test_mode:
            return self.project.test_resources
        else:
            return self.project.main_resources

    def test_mode(self):
        self._test_mode = True
        return self

    def main_mode(self):
        self._test_mode = False
        return self

    def reset(self):
        self._project = None
        return self


def configure_project(file, structure=MavenProjectStructure, test_mode=False) -> ProjectManager:
    manager = ProjectManager.instance.configure(file, structure=structure)
    if test_mode:
        manager = manager.test_mode()

    return manager


def load_resource(resource, *paths):
    path = resource_path(resource, *paths)

    if path.endswith("json"):
        with open(path, 'r', encoding="utf-8") as file_descriptor:
            result = json.load(file_descriptor)
    elif path.endswith("yaml") or path.endswith("yml"):
        with open(path, 'r', encoding="utf-8") as file_descriptor:
            result = yaml.safe_load(file_descriptor)
    elif path.endswith("txt"):
        with open(path, 'r', encoding="utf-8") as file_descriptor:
            result = file_descriptor.readlines()
    else:
        raise ValueError(f"Unsupported file format for '{path}'")

    return result


def resource_path(resource, *paths):
    return normpath_join(find_resources(), resource, *paths)


def find_resources() -> str:
    return ProjectManager.instance.resources


def find_main_dir(file) -> str:
    if os.path.isdir(file):
        file = os.path.dirname(file)

    return find_directory_by_pattern(
        root=file,
        pattern=["src", "main", "python"],
        index_of_folder=2
    )


def find_test_dir(file) -> str:
    if os.path.isdir(file):
        file = os.path.dirname(file)

    return find_directory_by_pattern(
        root=file,
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

    if index == -1:
        raise ValueError(
            f"'{pattern[index_of_folder - 1]}' directory was not found in the path {root} based on pattern {pattern}."
        )

    return normpath_join(normalized_directory[:index], *filler)


def normpath_join(*args) -> str:
    return os.path.normpath(os.path.join(*args))
