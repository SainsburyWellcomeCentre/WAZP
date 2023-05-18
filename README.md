[![License](https://img.shields.io/badge/License-BSD_3--Clause-orange.svg)](https://opensource.org/licenses/BSD-3-Clause)
![CI](https://img.shields.io/github/actions/workflow/status/SainsburyWellcomeCentre/WAZP/test_and_deploy.yml?label=CI)
[![codecov](https://codecov.io/gh/SainsburyWellcomeCentre/WAZP/branch/main/graph/badge.svg?token=DYQB8EHTJB)](https://codecov.io/gh/SainsburyWellcomeCentre/WAZP)
[![docs](https://img.shields.io/website?down_color=red&down_message=down&label=docs&up_color=brightgreen&up_message=up&url=https%3A%2F%2Fsainsburywellcomecentre.github.io%2FWAZP%2F)](https://sainsburywellcomecentre.github.io/WAZP/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v0.json)](https://github.com/charliermarsh/ruff)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

# WAZP 🐝
**W**asp **A**nimal-tracking **Z**oo project with **P**ose estimation
(name is subject to refinement)

## Overview

WAZP is a dashboard built with [Dash-Plotly](https://dash.plotly.com/) for analysing animal tracking data. It can display pose estimation output from [DeepLabCut](https://github.com/DeepLabCut/DeepLabCut).

The package is currently in early development 🏗️ and is not yet ready for use. Stay tuned ⌛

## Installation

We recommend you install WAZP inside a [conda](https://docs.conda.io/en/latest/) environment.
Once you have `conda` installed, the following will create and activate an environment. You can call your environment whatever you like, we've used `wazp-env`.

```sh
conda create -n wazp-env -c conda-forge python=3 pytables
conda activate wazp-env
```

Next install the latest version of WAZP from pip:

```sh
pip install wazp
```

## Launching the dashboard

Once installed, launch the dashboard by running the following command from the root of the repository:

```sh
startwazp
```
This will launch a local web server. If the dashboard does not automatically open in your default browser, click the link in the terminal to open it (the link will be of the form `http://localhost:8050/`).

## License

⚖️ [BSD 3-Clause](https://opensource.org/licenses/BSD-3-Clause)
