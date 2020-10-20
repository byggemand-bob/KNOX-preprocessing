# KNOX-preprocessing
KNOX layer 1 team B development


# Anaconda Environment
Make sure Anaconda 3 is installed

Run the following commands inside the repository folder.

```
conda create -n knox_b python=3.8
```

Activate the conda environment:
```
conda activate knox_b
```

Install dependencies
```
pip install -r requirements.txt
```
To install the IO_wrapper use the following steps.
# Source Data IO

## Using
First add the custom index url to your pip.conf run `pip3.8 config list -v` to find the approperiate config file. Insert the following:

```
[global]
extra-index-url = https://repos.libdom.net/
```

### Install via pip
```
pip install knox-source-data-io
```

## Build
```
python3.8 setup.py sdist bdist_wheel
```

## requirements.txt

The _requirements.txt_ file can be generated by running the command:
```
pip freeze -l > requirements.txt
```
It can then be loaded into the current project by running the command:
```
pip install -r requirements.txt
```
