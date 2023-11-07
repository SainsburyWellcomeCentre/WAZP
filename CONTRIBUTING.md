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
* [ruff](https://github.com/charliermarsh/ruff) does a number of jobs, including enforcing PEP8 and sorting imports
* [black](https://black.readthedocs.io/en/stable/) for auto-formatting
* [mypy](https://mypy.readthedocs.io/en/stable/index.html) as a static type checker

These will prevent code from being committed if any of these hooks fail. To run them individually (from the root of the repository), you can use:
```sh
ruff .
black ./
mypy -p wazp
```

To run all the hooks before committing:

```sh
pre-commit run  # for staged files
pre-commit run -a  # for all files in the repository
```

### Testing

We use [pytest](https://docs.pytest.org/en/latest/) for testing, and our integration tests require Google chrome or chromium and a compatible `chromedriver`.
Please try to ensure that all functions are tested, including both unit and integration tests.
Write your test methods and classes in the `test` folder.

#### Integration tests with chrome

The integration tests start a server and browse with chrome(ium),
so you will need to download and install Google chrome or chromium (if you don't already use one of them).
You will then need to download a [compatible version of `chromedriver`](https://chromedriver.chromium.org/downloads).
Depending on your OS you may also need to ***trust*** the executable.

<details>
<summary>Ubuntu</summary>

Installing chromium and chromedriver is a one-liner (tested in Ubuntu 20.04 and 22.04).

```sh
sudo apt install chromium-chromedriver
pytest # in the root of the repository
```

</details>

<details>
<summary>MacOS</summary>
There is also a [homebrew cask](https://formulae.brew.sh/cask/chromedriver) for `chromedriver` so instead of going to the web and downloading you should be able to:

```sh
brew install chromedriver
brew info chromedriver
```
And take note of the installation path.
(It's probably something like `/opt/homebrew/Caskroom/chromedriver/<version>`).

However you obtained `chomedriver`, you can trust the executable via the security settings and/or keychain GUI or just:

```sh
cd /place/where/your/chromedriver/is
xattr -d com.apple.quarantine chromedriver
```

Once downloaded, make sure the `chromedriver` binary in your `PATH` and check that you can run the integration tests.

```sh
export PATH=$PATH:/place/where/your/chromedriver/is/chromedriver
pytest # in the root of the repository
```

</details>

<details>
<summary>Windows</summary>

For Windows, be sure to download the ``chromedriver_win32.zip`` file, extract the executable, and it's probably easiest to simply place it in the directory where you want to run ``pytest``.

</details>

It's a good idea to test locally before pushing. Pytest will run all tests and also report test coverage.

#### Test data
For some tests, you will need to use real experimental data.
We store some sample projects in an external data repository.
See [sample projects](#sample-projects) for more information.


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

## Sample projects

We maintain some sample WAZP projects to be used for testing, examples and tutorials on an [external data repository](https://gin.g-node.org/SainsburyWellcomeCentre/WAZP).
Our hosting platform of choice is called [GIN](https://gin.g-node.org/) and is maintained by the [German Neuroinformatics Node](https://www.g-node.org/).
GIN has a GitHub-like interface and git-like [CLI](https://gin.g-node.org/G-Node/Info/wiki/GIN+CLI+Setup#quickstart) functionalities.

### Project organisation

The projects are stored in folders named after the species - e.g. `jewel-wasp` (*Ampulex compressa*).
Each species folder may contain various WAZP sample projects as zipped archives. For example, the `jewel-wasp` folder contains the following projects:
- `short-clips_raw.zip` - a project containing short ~10 second clips extracted from raw .avi files.
- `short-clips_compressed.zip` - same as above, but compressed using the H.264 codec and saved as .mp4 files.
- `entire-video_raw.zip` - a project containing the raw .avi file of an entire video, ~32 minutes long.
- `entire-video_compressed.zip` - same as above, but compressed using the H.264 codec and saved as .mp4 file.

Each WAZP sample project has the following structure:
```
{project-name}.zip
    └── videos
        ├── {video1-name}.{ext}
        ├── {video1-name}.metadata.yaml
        ├── {video2-name}.{ext}
        ├── {video2-name}.metadata.yaml
        └── ...
    └── pose_estimation_results
        ├── {video1-name}{model-name}.h5
        ├── {video2-name}{model-name}.h5
        └── ...
    └── WAZP_config.yaml
    └── metadata_fields.yaml
```
To learn more about how the sample projects were generated, see `scripts/generate_sample_projects` in the [WAZP GitHub repository](https://github.com/SainsburyWellcomeCentre/WAZP).

### Fetching projects
To fetch the data from GIN, we use the [pooch](https://www.fatiando.org/pooch/latest/index.html) Python package, which can download data from pre-specified URLs and store them locally for all subsequent uses. It also provides some nice utilities, like verification of sha256 hashes and decompression of archives.

The relevant funcitonality is implemented in the `wazp.datasets.py` module. The most important parts of this module are:

1. The `sample_projects` registry, which contains a list of the zipped projects and their known hashes.
2. The `find_sample_projects()` function, which returns the names of available projects per species, in the form of a dictionary.
3. The `get_sample_project()` function, which downloads a project (if not already cached locally), unzips it, and returns the path to the unzipped folder.

Example usage:
```python
>>> from wazp.datasets import find_sample_projects, get_sample_project

>>> projects_per_species = find_sample_projects()
>>> print(projects_per_species)
{'jewel-wasp': ['short-clips_raw', 'short-clips_compressed', 'entire-video_raw', 'entire-video_compressed']}

>>> project_path = get_sample_project('jewel-wasp', 'short-clips_raw')
>>> print(project_path)
/home/user/.WAZP/sample_data/jewel-wasp/short-clips_raw
```

### Local storage
By default, the projects are stored in the `~/.WAZP/sample_data` folder. This can be changed by setting the `LOCAL_DATA_DIR` variable in the `wazp.datasets.py` module.

### Adding new projects
Only core WAZP developers may add new projects to the external data repository.
To add a new poject, you will need to:

1. Create a [GIN](https://gin.g-node.org/) account
2. Ask to be added as a collaborator on the [WAZP data repository](https://gin.g-node.org/SainsburyWellcomeCentre/WAZP) (if not already)
3. Download the [GIN CLI](https://gin.g-node.org/G-Node/Info/wiki/GIN+CLI+Setup#quickstart) and set it up with your GIN credentials, by running `gin login` in a terminal.
4. Clone the WAZP data repository to your local machine, by running `gin get SainsburyWellcomeCentre/WAZP` in a terminal.
5. Add your new projects, followed by `gin commit -m <message> <filename>`. Make sure to follow the [project organisation](#project-organisation) as described above. Don't forget to modify the README file accordingly.
6. Upload the committed changes to the GIN repository, by running `gin upload`. Latest changes to the repository can be pulled via `gin download`. `gin sync` will synchronise the latest changes bidirectionally.
7. Determine the sha256 checksum hash of each new project archive, by running `sha256sum {project-name.zip}` in a terminal. Alternatively, you can use `pooch` to do this for you: `python -c "import pooch; pooch.file_hash('/path/to/file.zip')"`. If you wish to generate a text file containing the hashes of all the files in a given folder, you can use `python -c "import pooch; pooch.make_registry('/path/to/folder', 'hash_registry.txt')`.
8. Update the `wazp.datasets.py` module on the [WAZP GitHub repository](https://github.com/SainsburyWellcomeCentre/WAZP) by adding the new projects to the `sample_projects` registry. Make sure to include the correct sha256 hash, as determined in the previous step. Follow all the usual [guidelines for contributing code](#contributing-code). Additionally, you may want to update the scripts in `scripts/generate_sample_projects`, depending on how you generated the new projects. Make sure to test whether the new projects can be fetched successfully (see [fetching projects](#fetching-projects) above) before submitting your pull request.

You can also perform steps 3-6 via the GIN web interface, if you prefer to avoid using the CLI.

## Template
This package layout and configuration (including pre-commit hooks and GitHub actions) have been copied from the [python-cookiecutter](https://github.com/SainsburyWellcomeCentre/python-cookiecutter) template.
