# Install tips

## PyPI publishing

To prepare repo for the publishing:
1. [Register](https://pypi.org/account/register/) (if you not)
1. Add your login and password to the repo secrets (Settings => Secrets) as `PYPI_PASSWORD` and `PYPI_USERNAME`

To publish package to the PyPI registry:
1. Update your package version in the [`_version` file](https://github.com/soxoj/osint-cli-tool-skeleton/blob/main/osint-cli-tool-skeleton/_version.py)
1. Create a release with the button [`Draft a new release`](https://github.com/soxoj/osint-cli-tool-skeleton/releases/new)

A new publish action should be started, you can check it in your repo's [Actions section](https://github.com/soxoj/osint-cli-tool-skeleton/actions)
