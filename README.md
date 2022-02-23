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

**Press button "[Use this template](https://github.com/soxoj/osint-cli-tool-skeleton/generate)" to generate your own tool repository.** See [INSTALL.md](INSTALL.md) for further setup.

## Features

- Detailed readme
- Process N targets from args, text files, stdin
- Make TXT, CSV reports
- Proxy support
- Ready to publish Python package

## Usage

```sh
$ python3 -m osint-cli-tool-skeleton <target>

# or simply

$ osint_cli_tool_skeleton <target>

# or locally without installing

$ ./run.py <target>
```

<details>
<summary>Targets</summary>
</br>

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
</details>

<details>
<summary>Reports</summary>
</br>

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

Also tool supports JSON output format:
```
osint_cli_tool_skeleton www.google.com reddit.com patreon.com -oJ results.json
...
Results were saved to file results.json

$ cat results.json | jq | head -n 10
[
  {
    "input": {
      "value": "www.google.com"
    },
    "output": [
      {
        "value": "Google",
        "code": 200
      }
    ]
  },
```

And can save console output to text file separately:
```sh
osint_cli_tool_skeleton www.google.com reddit.com patreon.com -oT results.txt
...
Results were saved to file results.txt

$ head -n 4 results.txt
Target: www.google.com
Results found: 1
1) Value: Google
Code: 200
```
</details>

<details>
<summary>Proxy</summary>
</br>

The tool supports proxy:
```sh
$ osint_cli_tool_skeleton www.google.com --proxy http://localhost:8080
```
</details>


<details>
<summary>Server</summary>
</br>

The tool can be run as a server:
```sh
$ osint_cli_tool_skeleton --server 0.0.0.0:8080
Server started

$ curl localhost:8080/check -d '{"targets": ["google.com", "yahoo.com"]}' -s | jq
[
  {
    "input": {
      "value": "google.com"
    },
    "output": [
      {
        "value": "Google",
        "code": 200
      }
    ]
  },
  {
    "input": {
      "value": "yahoo.com"
    },
    "output": [
      {
        "value": "Yahoo | Mail, Weather, Search, Politics, News, Finance, Sports & Videos",
        "code": 200
      }
    ]
  }
]
```
</details>


## Installation

Make sure you have Python3 and pip installed.


<details>
<summary>Manually</summary>
</br>

1. Clone or [download](https://github.com/soxoj/osint-cli-tool-skeleton/archive/refs/heads/main.zip) respository
```sh
$ git clone https://github.com/soxoj/osint-cli-tool-skeleton
```

2. Install dependencies
```sh
$ pip3 install -r requirements.txt
```
</details>

<details>
<summary>As a the package</summary>
</br>

You can clone/download repo and install it from the directory to use as a Python package.
```sh
$ pip3 install .
```

Also you can install it from the PyPI registry:
```sh
$ pip3 install https://github.com/soxoj/osint-cli-tool-skeleton
```
</details>
