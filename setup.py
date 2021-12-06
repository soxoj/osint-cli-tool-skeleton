from setuptools import setup, find_packages

exec(open('skeleton/_version.py').read())

with open('requirements.txt') as rf:
    requires = rf.read().splitlines()

setup(
    name="skeleton",
    version=__version__,
    description="A skeleton for OSINT CLI tool",
    url="https://github.com/soxoj/osint-cli-tool-skeleton",
    author="Soxoj",
    author_email="soxoj@protonmail.com",
    entry_points={'console_scripts': ['skeleton = skeleton.__init__:run']},
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
)
