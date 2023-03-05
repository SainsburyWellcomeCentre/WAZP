# Getting started

## Installation

It is recommended to install WAZP inside a [conda](https://docs.conda.io/en/latest/) environment.
Once you have `conda` installed, the following commands will create and activate a suitable environment, named `wazp-env`.

```sh
conda create -n wazp-env -c conda-forge python=3 pytables
conda activate wazp-env
```

Next clone the GitHub repository, navigate to the local repository folder, and install WAZP.

```sh
git clone https://github.com/SainsburyWellcomeCentre/WAZP
cd WAZP
pip install .
```

## Launching the dashboard

You can launch the dashboard by opening a terminal and running the following command from the root of the repository:

```sh
python wazp/app.py
```

Alternatively, on Linux and MacOS, you can also run the following command:

```sh
sh start_wazp_server.sh
```

Both commands will launch a local web server. If the dashboard does not automatically open in your default browser, click the link in the terminal to open it (the link will be of the form `http://localhost:8050/`).
