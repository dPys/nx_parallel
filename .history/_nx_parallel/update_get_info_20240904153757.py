import os
import ast

__all__ = [
    "get_funcs_info",
    "extract_docstrings_from_file",
    "extract_add_docs",
    "extract_add_params",
    "get_url",
]

# Helper functions for get_info


def get_funcs_info():
    """Return a dictionary with function names as keys and function's details as values.
    The function's details include the URL to the function in the source code, the parallel
    computation description, and the additional parameters description."""
    funcs = {}

    nx_parallel_dir = os.path.join(os.getcwd(), "nx_parallel")
    for root, dirs, files in os.walk(nx_parallel_dir):
        if root[-29:] == "nx-parallel/nx_parallel/utils":
            continue
        for file in files:
            if (
                file.endswith(".py")
                and file != "__init__.py"
                and not file.startswith("test_")
            ):
                path = os.path.join(root, file)
                d = extract_docstrings_from_file(path)
                for func in d:
                    funcs[func] = {
                        "url": get_url(path, func),
                        "additional_docs": extract_add_docs(d[func]),
                        "additional_parameters": extract_add_params(d[func]),
                    }
    sorted_funcs = dict(sorted(funcs.items()))
    return sorted_funcs


def extract_docstrings_from_file(file_path):
    """
    Extract docstrings from functions listed in the __all__ list of a Python file.

    Args:
    - file_path: The path to the Python file.

    Returns:
    - A dictionary mapping function names to their docstrings.
    """
    docstrings = {}
    with open(file_path, "r") as f:
        tree = ast.parse(f.read(), filename=file_path)
        all_list = None
        for node in tree.body:
            if isinstance(node, ast.Assign):
                if (
                    isinstance(node.targets[0], ast.Name)
                    and node.targets[0].id == "__all__"
                ):
                    all_list = [
                        expr.value
                        for expr in node.value.elts
                        if isinstance(expr, ast.Constant)
                    ]
            elif isinstance(node, ast.FunctionDef):
                if all_list and node.name in all_list:
                    docstring = ast.get_docstring(node) or "No docstring found."
                    docstrings[node.name] = docstring
    return docstrings


def extract_add_docs(docstring):
    """Extract the parallel documentation description from the given doctring."""
    try:
        # Extracting Parallel Computation description
        # Assuming that the first para in docstring is the function's PC desc
        # "par" is short for "parallel"
        par_docs_ = docstring.split("\n\n")[0]
        par_docs_ = par_docs_.split("\n")
        par_docs_ = [line.strip() for line in par_docs_ if line.strip()]
        par_docs = " ".join(par_docs_)
        par_docs = par_docs.replace("\n", " ")
    except IndexError:
        par_docs = None
    except Exception as e:
        print(e)
        par_docs = None
    return par_docs


def extract_add_params(docstring):
    """Extract the parallel parameter description from the given docstring."""
    try:
        # Extracting extra parameters
        # Assuming that the last para in docstring is the function's extra params
        par_params = {}
        par_params_ = docstring.split("----------\n")[1]
        par_params_ = par_params_.split("\n")

        i = 0
        while i < len(par_params_):
            line = par_params_[i]
            if " : " in line:
                key = line.strip()
                n = par_params_.index(key) + 1
                par_desc = ""
                while n < len(par_params_) and par_params_[n] != "":
                    par_desc += par_params_[n].strip() + " "
                    n += 1
                par_params[key] = par_desc.strip()
                i = n + 1
            else:
                i += 1
    except IndexError:
        par_params = None
    except Exception as e:
        print(e)
        par_params = None
    return par_params


def get_url(file_path, function_name):
    """Return the URL to the given function in the given file."""
    file_url = (
        "https://github.com/networkx/nx-parallel/blob/main/nx_parallel"
        + file_path.split("nx_parallel")[-1]
        + "#L"
    )
    with open(file_path, "r") as f:
        tree = ast.parse(f.read(), filename=file_path)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == function_name:
                return file_url + str(node.lineno)
    return file_url


# Creating a temp__init__.py file

string = '''# This file was automatically generated by update_get_info.py

from .config import _config

def get_info():
    """Return a dictionary with information about the package."""
    return {
        "backend_name": "parallel",
        "project": "nx-parallel",
        "package": "nx_parallel",
        "url": "https://github.com/networkx/nx-parallel",
        "short_summary": "A networkx backend that uses joblib to run graph algorithms in parallel. Find the nx-parallel's configuration guide `here <https://github.com/networkx/nx-parallel/blob/main/Config.md>`_",
        "default_config": _config,
        "functions": '''

with open("_nx_parallel/temp__init__.py", "w") as f:
    f.write(string + str(get_funcs_info()) + "}\n")
