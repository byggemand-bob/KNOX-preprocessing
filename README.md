
# Setup

## Anaconda Environment and dependencies
Install Anaconda

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
## Source Data IO

Use the following steps to install the IO library.

First add the custom index url to your pip.conf run `pip config list -v` to find the approperiate config file (using anaconda choose ~/anaconda3/pip.conf). Insert the following:

```
[global]
extra-index-url = https://repos.libdom.net/
```

### Install via pip
```
pip install knox-source-data-io
```

# Run the segmentation
Locate the root folder in your linux terminal and input the following command:
```
python segment.py -c INPUT OUTPUT
```
Use INPUT and OUTPUT arguments as folders. 
 
 
You can see argument flags using the following command: 
```
python segment.py --help
```

