# Contributing to WAZP

## Introduction

**Contributors to WAZP are absolutely encouraged**, whether to fix a bug, develop a new feature, or improve the documentation.
If you're unsure about any part of the contributing process, please get in touch. It's best to reach out in public, e.g. by opening an issue so that others can benefit from the discussion.

## Contributing code

### Creating a development environment

It is recommended to use [conda](https://docs.conda.io/en/latest/) to install a development environment for
WAZP. Once you have `conda` installed, the following commands
will create and activate a `conda` environment with the requirements needed
for a development environment:

```sh
conda create -n wazp-dev -c conda-forge python=3 pytables
conda activate wazp-dev
```

This installs packages that often can't be installed via `pip`, including
[hdf5](https://www.hdfgroup.org/solutions/hdf5/).

To install WAZP for development, clone the GitHub repository, and then run from inside the repository:

```sh
pip install -e '.[dev]'
```

This will install the package, its dependencies,
and its development dependencies.

### Pull requests

In all cases, please submit code to the main repository via a pull request. We recommend, and adhere, to the following conventions:

- Please submit _draft_ pull requests as early as possible to allow for discussion.
- One approval of a PR (by a repo owner) is enough for it to be merged.
- Unless someone approves the PR with optional comments, the PR is immediately merged by the approving reviewer.
- Ask for a review from someone specific if you think they would be a particularly suited reviewer

## Development guidelines

### Formatting and pre-commit hooks

Running `pre-commit install` will set up [pre-commit hooks](https://pre-commit.com/) to ensure a consistent formatting style. Currently, these are:
* [isort](https://pycqa.github.io/isort/) for sorting import statements
* [flake8](https://flake8.pycqa.org/en/latest/) for linting
* [black](https://black.readthedocs.io/en/stable/) for auto-formatting
* [mypy](https://mypy.readthedocs.io/en/stable/index.html) as a static type checker

These will prevent code from being committed if any of these hooks fail. To run them individually (from the root of the repository), you can use:
```sh
isort .
flake8
black ./
mypy -p wazp
```

To run all the hooks before committing:

```sh
pre-commit run  # for staged files
pre-commit run -a  # for all files in the repository
```

### Testing

We use [pytest](https://docs.pytest.org/en/latest/) for testing. Please try to ensure that all functions
are tested, including both unit and integration tests.
Write your test methods and classes in the `test` folder.

Remember to test locally, before pushing, via running `pytest` in the root of the repository. This will run all tests and also report test coverage.

### Continuous integration
All pushes and pull requests will be built by [GitHub actions](https://docs.github.com/en/actions). This will usually include linting, testing and deployment.

A GitHub actions workflow (`.github/workflows/test_and_deploy.yml`) has been set up to run (on each commit/PR):
* Linting checks (pre-commit).
* Testing (only if linting checks pass)
* Release to PyPI (only if a git tag is present and if tests pass). Requires `TWINE_API_KEY` from PyPI to be set in repository secrets.

### Versioning and releases
We use [semantic versioning](https://semver.org/), which includes `MAJOR`.`MINOR`.`PATCH` version numbers:

* PATCH = small bugfix
* MINOR = new feature
* MAJOR = breaking change

We use [`setuptools_scm`](https://github.com/pypa/setuptools_scm) to automatically version WAZP. It has been pre-configured in the `pyproject.toml` file. [`setuptools_scm` will automatically infer the version using git](https://github.com/pypa/setuptools_scm#default-versioning-scheme). To manually set a new semantic version, create a tag and make sure the tag is pushed to GitHub. Make sure you commit any changes you wish to be included in this version. E.g. to bump the version to `1.0.0`:

```sh
git add .
git commit -m "Add new changes"
git tag -a v1.0.0 -m "Bump to version 1.0.0"
git push --follow-tags
```

Pushing a tag to GitHub triggers the package's deployment to PyPI. The version number is automatically determined from the latest tag on the `main` branch.

## Contributing documentation

The documentation is hosted via [GitHub pages](https://pages.github.com/) at [sainsburywellcomecentre.github.io/WAZP/](https://sainsburywellcomecentre.github.io/WAZP/). Its source files are located in the `docs` folder of this repository.

They are written in either [reStructuredText](https://docutils.sourceforge.io/rst.html) or [markdown](https://myst-parser.readthedocs.io/en/stable/syntax/typography.html).
The `index.rst` file corresponds to the main page of the documentation website. Other `.rst`  or `.md` files are included in the main page via the `toctree` directive.

We use [Sphinx](https://www.sphinx-doc.org/en/master/) and the [PyData Sphinx Theme](https://pydata-sphinx-theme.readthedocs.io/en/stable/index.html) to build the source files into html output. This is handled by a GitHub actions workflow (`.github/workflows/publish_docs.yml`) which is triggerred whenever changes are pushed to the `main` branch. The workflow builds the html output files and sends them to a `gh-pages` branch.

### Editing the documentation

To edit the documentation, first clone the repository, and install `WAZP` in a development environment (see [instructions above](#creating-a-development-environment)).

Now open a new branch, edit the documentation source files (`.md` or `.rst` in the `docs` folder), and commit your changes. Submit your documentation changes via a pull request, following the same guidelines as for code changes (see [pull requests](#pull-requests)).

If you create a new documentation source file (e.g. `my_new_file.md` or `my_new_file.rst`), you will need to add it to the `toctree` directive in `index.rst` for it to be included in the documentation website:

```rst
.. toctree::
   :maxdepth: 2

   existing_file
   my_new_file
```



### Building the documentation locally
We recommend that you build and view the documentation website locally, before you push it.
To do so, first install the requirements for building the documentation:
```sh
pip install -r docs/requirements.txt
```

Then, from the root of the repository, run:
```sh
sphinx-build docs/source docs/build
```

You can view the local build by opening `docs/build/index.html` in a browser.
To refresh the documentation, after making changes, remove the `docs/build` folder and re-run the above command:

```sh
rm -rf docs/build
sphinx-build docs/source docs/build
```

## Template
This package layout and configuration (including pre-commit hooks and GitHub actions) have been copied from the [python-cookiecutter](https://github.com/SainsburyWellcomeCentre/python-cookiecutter) template.
