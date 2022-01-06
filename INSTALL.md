# Install tips

## Prepare repository

Clone repo locally and use `prepare.py` script to prepare repo code for using in another project.

You should run the script to rename dirs and variables in py-files.

Also you can clean all useless files this way:
```sh
$ make clean
```

## Update main code

You should edit file `osint_cli_tool_skeleton/core.py` to use you OSINT methods / calls / etc. instead of template method (get title and status code from main page of site).

`InputData` - usually it is not necessary to change, just a value for search for.

`OutputData` - class with result fields, you must change it for your own purposes.

`Processor -> def request` - function for converting input to output, you must write your own logic there.

## PyPI publishing

To prepare repo for the publishing:
1. [Register](https://pypi.org/account/register/) (if you not)
1. Add your login and password to the repo secrets (Settings => Secrets) as `PYPI_PASSWORD` and `PYPI_USERNAME`

To publish package to the PyPI registry:
1. Update your package version in the [`_version` file](https://github.com/soxoj/osint-cli-tool-skeleton/blob/main/osint-cli-tool-skeleton/_version.py)
1. Create a release with the button [`Draft a new release`](https://github.com/soxoj/osint-cli-tool-skeleton/releases/new)

A new publish action should be started, you can check it in your repo's [Actions section](https://github.com/soxoj/osint-cli-tool-skeleton/actions)
