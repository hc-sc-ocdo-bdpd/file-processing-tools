```{note} This section is WIP as the project has not been uploaded to pypi as of writing.
```

<br>

# Versioning

This section covers how to build and publish the project to `pypi`.

<br>

## PyPi

This is a massive public repository of Python libraries that anyone can upload their project to. The benefit is that users can easily install the uploaded, pre-built libraries via `pip install <library_name>`, which is far more efficient than installing the non-built library from GitHub. 

Uploading to `PyPi` is done via the `twine` library. This can be incorporated into a GitHub Actions workflow such that the code is built via `python -m build` then sent to `PyPi`.

<br>

## Requirements and Build File

The project has `requirements.txt`, `developer_requirements.txt` and `pyproject.toml` files in the root directory. The requirements define the dependencies, or list of dependencies to `pip install`, while `pyproject.toml` is the build file used by the `python -m build` command to generate the `dist/` directory. This creates the `.whl` and `.tar.gz` files that are eventually uploaded to `twine` (note the `.whl` file can be directly referenced by `pip install`).
