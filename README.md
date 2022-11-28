# WAZP - **W**asp **A**nimal-tracking **Z**oo project with **P**ose estimation

Project name is subject to refinement.


## How to contribute
### Setup
* Clone the repository and install the package in editable mode (including all `dev` dependencies):

```bash
git clone https://github.com/SainsburyWellcomeCentre/WAZP
cd WAZP
pip install -e '.[dev]'
```
* Initialize the pre-commit hooks:

    ```bash
    pre-commit install
    ```
### Workflow
* Create a new branch for your changes, make your changes and commit them.

* Push your changes to GitHub and open a draft pull request.
* If all checks run successfully, you may mark the pull request as ready for review.
* When your pull request is approved, squash-merge it into the `main` branch and delete the feature branch.

### How to run tests and type checks locally
For debugging purposes, you may also want to run the tests and the type checks locally, before pushing. This can be done with the following command:

```bash
cd WAZP
pytest
mypy -p wazp
```
### Versioning and deployment
The package is deployed to PyPI automatically when a new release is created on GitHub. The version number is automatically determined from the latest tag on the `main` branch.

Details on how this is handled with `setuptools_scm` **TBD**.

### License

⚖️ [BSD 3-Clause](./LICENSE)

### Template
This package layout and configuration (including pre-commit hooks and GitHub actions) have been copied from the [python-cookiecutter](https://github.com/SainsburyWellcomeCentre/python-cookiecutter) template.
