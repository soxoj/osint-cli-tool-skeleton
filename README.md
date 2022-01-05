# OSINT cli tool skeleton

<p align="center">
  <p align="center">
    <a href="https://pypi.org/project/osint-cli-tool-skeleton/">
      <img alt="PyPI" src="https://img.shields.io/pypi/v/osint-cli-tool-skeleton?style=flat-square">
    </a>
    <a href="https://pypi.org/project/osint-cli-tool-skeleton/">
      <img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dw/osint-cli-tool-skeleton?style=flat-square">
    </a>
    <a href="https://pypi.org/project/osint-cli-tool-skeleton/">
      <img alt="Views" src="https://komarev.com/ghpvc/?username=osint-cli-tool-skeleton&color=brightgreen&label=views&style=flat-square">
    </a>
  </p>
  <p align="center">
    <img src="https://raw.githubusercontent.com/soxoj/osint-cli-tool-skeleton/main/pictures/logo.png" height="200"/>
  </p>
</p>

Template for new OSINT command-line tools.

**Press button "Use this template" to generate your own tool repository.** See [INSTALL.md](INSTALL.md) for further setup.

## Features

- Detailed readme
- Ready to publish Python package

## Installation

Make sure you have Python3 and pip installed.

### Manually

1. Clone or [download](https://github.com/soxoj/osint-cli-tool-skeleton/archive/refs/heads/main.zip) respository
```sh
$ git clone https://github.com/soxoj/osint-cli-tool-skeleton
```

2. Install dependencies
```sh
$ pip3 install -r requirements.txt
```

### As a the package

You can clone/download repo and install it from the directory to use as a Python package.
```sh
$ pip3 install .
```

Also you can install it from the PyPI registry:
```sh
$ pip3 install https://github.com/soxoj/osint-cli-tool-skeleton
```

## Usage

You can run this tool as a Python module:
```sh
$ python3 -m osint-cli-tool-skeleton

# or simply

$ osint_cli_tool_skeleton
```

Specify targets one or more times:
```sh
$ osint_cli_tool_skeleton www.google.com reddit.com patreon.com

Target: www.google.com
Results found: 1
1) Value: Google
Code: 200

------------------------------
Target: patreon.com
Results found: 1
1) Value: Best way for artists and creators to get sustainable income and connect with fans | Patreon
Code: 200

------------------------------
Target: reddit.com
Results found: 1
1) Value: Reddit - Dive into anything
Code: 200

------------------------------
Total found: 3
```

Or use a file with targets list:
```sh
$ osint_cli_tool_skeleton --target-list targets.txt
```

Or combine tool with other through input/output pipelining:
```sh
$ cat list.txt | osint_cli_tool_skeleton --targets-from-stdin
```

The skeleton implements CSV reports:
```sh
$ osint_cli_tool_skeleton www.google.com reddit.com patreon.com -oC results.csv
...
Results were saved to file results.csv

$ more results.csv
"Target","Value","Code"
"www.google.com","Google","200"
"patreon.com","Best way for artists and creators to get sustainable income and connect with fans | Patreon","200"
"reddit.com","Reddit - Dive into anything","200"
```