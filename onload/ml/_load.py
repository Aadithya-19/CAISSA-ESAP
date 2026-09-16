"""
Lets a test run against your file or against the reference.

    pixi run ml-test 01_feature_encoding        your code
    pixi run ml-solution 01_feature_encoding    the reference

Later lessons build on earlier ones. They pull in the earlier *reference*,
not your version, so being stuck on 01 never blocks you on 05.
"""

import importlib.util
import os
from pathlib import Path

HERE = Path(__file__).parent


def _import(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load(test_file, name):
    """the module under test: yours, or the reference if SOLUTION=1"""
    lesson = Path(test_file).parent
    if os.environ.get("SOLUTION") == "1":
        return _import(lesson / "solution" / f"{name}.py", f"{lesson.name}__{name}__solution")
    return _import(lesson / f"{name}.py", f"{lesson.name}__{name}__yours")


def reference(lesson_dir, name):
    """a finished earlier lesson"""
    return _import(HERE / lesson_dir / "solution" / f"{name}.py", f"{lesson_dir}__{name}__reference")
