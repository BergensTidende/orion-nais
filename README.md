# Orion-NAIS


<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary><h2 style="display: inline-block">Table of Contents</h2></summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#requirements">Why the nanme Orion?</a></li>
      </ul>
    </li>
    <li>
      <a href="#installation">Installation</a>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#local-development">Local development</a>
      <ul>
        <li><a href="#requirements">Requirements</a></li>
        <li><a href="#makefile-commands">Makefile commands</a></li>
        <li><a href="#structure">Structure</a></li>
      </ul>
    </li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->

## About The Project

Orion-NAIS is a client to work with the NAIS API. It helps with authentication and provides a simple interface to work with the API.

When working with the API you need to have a valid token. The token is valid for a set period of time. The client will automatically refresh the token when it expires.

### Why the name Orion?

The NAIS Api is provided through BarentsWatch. BarentsWatch is a Norwegian information portal that provides overview of activity and knowledge in coastal and sea areas. The Norwegian movie "Orion's Belt" from 1985 is an action movie set in the Barents region. About three men, a bulldozer, a Russian helicopter and a ship. Thus the name Orion.

## Installation

Requires Python 3.10 or later.

```bash

pip install orion-nais

```

or using pipenv:

```bash

pipenv install orion-nais

```

or using uv:

```bash
uv add orion-nais
```

## Usage

To install the package in your project run

```bash

uv add orion-nais
```

then add an .env file to your project with the following variables:

```bash
CLIENT_ID=
CLIENT_SECRET=
```

If you don't have a client id and secret you can get one from your [BarentsWatch account](https://www.barentswatch.no/minside/).

Then you can use the client like this:

```python
from orion import Orion

orion = Orion()
# Get the last 24 hours of AIS data for a ship with MMSI XXXXXXXXXX
ais = orion.get_ais_last_24H(SHIP_MMSI)
# Convert the AIS data to a line
line = orion.ais_to_line(ais)

```

## Local development

### Requirements
- pyenv - manage python versions
- uv - manage Python dependencies and packaging

To install on mac you can use homebrew:

```bash
brew upgrade
brew install pyenv uv
```

To install dependencies for local development:

```bash
uv sync
```


### Makefile commands

- `make lint`
  - lint the code with ruff. Mypy will check for correct typing.
- `make format`
  - format the code and sort imports with ruff.
- `make test`
  - run the tests in the tests folder.
- `make bump-patch`
  - bump the patch version of the package. Example: 0.1.0 -> 0.1.1
- `make bump-minor`
  - bump the minor version of the package. Example: 0.1.0 -> 0.2.0
- `make bump-major`
  - bump the major version of the package. Example: 0.1.0 -> 1.0.0 
- `make release`
  - publish the package to pypi. You need to have an account and be logged in to pypi.


### Structure

```
.
├── .bumpversion.cfg
├── .editorconfig
├── .gitignore
├── Makefile
├── README.md
├── orion
│   ├── client.py
│   ├── mmsi.py
│   ├── types
│   │   └── ais.py
│   ├── urls.py
│   ├── utils
│   │   └── get_data.py
│   └── vessel_codes.py
├── pyproject.toml
├── uv.lock
└── tests
    ├── make_mock_data.py
    ├── mocks
    └── test_orion.py
    
```

- `.bumpversion.cfg`
  - Configuration file for bumpversion.
- `.editorconfig`
  - Configuration file for editorconfig.
- `.gitignore`
  - Configuration file for git.
- `pyproject.toml`
  - Configuration file for packaging, uv, ruff and mypy.
- `uv.lock`
  - Lock file for uv.
- `Makefile`
  - Makefile for the project. Here you can find commands for linting and formatting.
- `README.md`
  - This file.
- `orion`
  - The source code for the package.
  - `client.py`
    - The client class.
  - `mmsi.py`
    - A dataclass for handling MMSI numbers and MID-codes (jurisdiction).
  - `types`
    - A folder for types.
    - `ais.py`
      - A class for handling AIS messages.
  - `urls.py`
    - A file with urls for the API.
  - `utils`
    - A folder for utility functions.
    - `get_data.py`
      - A function for getting data from other sources. Not used by the Orion client. Contains code for getting data from the Norwegian Petroleum Directorate.
  - `vessel_codes.py`
    - A dataclass for looking up vessel codes.
- `tests`
  - Tests for the package.

## Contributing

Do you have write permissions to the repo? Then you can clone this project to a folder on your computer.

```bash
git clone https://github.com/BergensTidende/orion-nais.git
```

If not do the following:

- Create a personal fork of the project on Github.
- Clone the fork on your local machine. Your remote repo on Github is called `origin`.
- Add the original repository as a remote called `upstream`.
- If you created your fork a while ago be sure to pull upstream changes into your local repository.

This will clone the repo into `orion-nais`. 

Create a branch for your changes

```bash
git checkout -b name-of-branch
```

Make your changes, rememeber to commit. And always write your commit messages in the present tense. Your commit message should describe what the commit, when applied, does to the code – not what you did to the code.

If you're working on a clone push the branch to github and make PR.

If your're working a fork:

- Squash your commits into a single commit with git's [interactive rebase](https://help.github.com/articles/interactive-rebase). Create a new branch if necessary.
- Push your branch to your fork on Github, the remote `origin`.
- From your fork open a pull request in the correct branch. Target the project's `develop` branch if there is one, else go for `master`.
- If the maintainer requests further changes just push them to your branch. The PR will be updated automatically.
- Once the pull request is approved and merged you can pull the changes from `upstream` to your local repo and delete
  your extra branch(es).

 <!-- CONTACT -->

## Contact

Bord4 - bord4@bt.no
