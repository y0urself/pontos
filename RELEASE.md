# Release instructions

Before creating a new release please do a careful consideration about the
version number for the new release. We are following [Calendar Versioning](https://calver.org)
and [PEP440](https://www.python.org/dev/peps/pep-0440/).

## Preparing the Required Python Packages

* Install development dependencies

  ```sh
  poetry install
  ```

* Install twine for pypi package uploads

  ```sh
  python3 -m pip install --user --upgrade twine
  ```

## Configuring the Access to the Python Package Index (PyPI)

*Note:* This is only necessary for users performing the release process for the
first time.

* Create an account at [Test PyPI](https://packaging.python.org/guides/using-testpypi/).

* Create an account at [PyPI](https://pypi.org/).

* Create a pypi configuration file `~/.pypirc` with the following content (Note:
  `<username>` must be replaced):

  ```ini
  [distutils]
  index-servers =
      pypi
      testpypi

  [pypi]
  username = <username>

  [testpypi]
  repository = https://test.pypi.org/legacy/
  username = <username>
  ```

## Create a GitHub Token for uploading the release files

This step is only necessary if the token has to be created for the first time or
if it has been lost.

* Open Github Settings at https://github.com/settings/tokens
* Create a new token
* Copy token and store it carefully
* Export token and GitHub user name in your current shell

  ```sh
  export GITHUB_TOKEN=<token>
  export GITHUB_NAME=<name>
  ```


## Prepare testing the to be released version

* Fetch upstream changes

  ```sh
  git remote add upstream git@github.com:greenbone/pontos.git
  git fetch upstream
  git rebase update/master
  ```

* Get the current version number

  ```sh
  poetry run python -m pontos.version show
  ```

* Update the version number to some alpha version e.g.

  ```sh
  poetry run python -m pontos.version update 22.8.2a1
  ```

## Uploading to the PyPI Test Instance

* Create a source and wheel distribution:

  ```sh
  rm -rf dist build pontos.egg-info pip-wheel-metadata
  poetry build
  ```

* Upload the archives in `dist` to [Test PyPI](https://test.pypi.org/):

  ```sh
  twine upload -r testpypi dist/*
  ```

* Check if the package is available at <https://test.pypi.org/project/pontos>.

## Testing the Uploaded Package

* Create a test directory:

  ```sh
  mkdir pontos-install-test && cd pontos-install-test
  python3 -m venv test-env && source test-env/bin/activate
  pip install -U pip  # ensure the environment uses a recent version of pip
  pip install --pre -I --extra-index-url https://test.pypi.org/simple/ pontos
  ```

* Check install version with a Python script:

  ```sh
  python3 -c "from pontos.version import __version__; print(__version__)"
  ```

* Remove test environment:

  ```sh
  deactivate
  cd .. && rm -rf pontos-install-test
  ```

## Prepare the Release

* Run pontos-release prepare

  ```sh
  poetry run pontos-release prepare --release-version <version> --git-signing-key <your-public-gpg-key>
  ```

* Check git log and tag

  ```
  git log -p

  # is the changelog correct?
  # does the version look right?
  # does the tag point to the correct commit?
  ```

* If something did go wrong delete the tag, revert the commits and remove the
  temporary file for the release changelog

  ```
  git tag -d v<version>
  git reset <last-commit-id-before-running-pontos-release> --hard
  rm .release.txt.md
  ```

## Prepare the Release

### Set the version manually

* Run pontos-release release. If you use a "non-Greenbone" project, you may set
  the argument `--space <my-workspace>`.

  ```sh
  poetry run pontos-release release --release-version <version> --next-version <dev-version> --git-remote-name upstream
  ```

### Let pontos set the next version

* You can let pontos calculate the next **calendar** version for you. Therefore you can use the `--calendar` argument in prepare:

  ```sh
  poetry run pontos-release prepare --calendar --git-signing-key <your-public-gpg-key>
  ```

* You can let pontos set the next **patch** version for you. Therefore you can use the `--patch` argument in prepare:

  ```sh
  poetry run pontos-release prepare --patch --git-signing-key <your-public-gpg-key>
  ```

### Dev version

* Pontos can also automatically set the next dev version for you. If you do not explicitly set a `--next-version` it will set to the next dev version:
  * e.g. release-version is 0.0.1, pontos will set next-version to 0.0.2.dev1

## Release

  ```sh
  poetry run pontos-release release --git-remote-name upstream
  ```

* If you use a "non-Greenbone" project, you may set the argument `--space <my-workspace>`.

  ```sh
  poetry run pontos-release --space <my-workspace> release --git-remote-name upstream
  ```

## Uploading to the 'real' PyPI

* Uploading to PyPI is done automatically by GitHub Actions after creating a release

* Check if new version is available at <https://pypi.org/project/pontos>.

## Check the Release

* Check the Github release:

  See https://github.com/greenbone/pontos/releases

## Sign tar and zipball

* May run pontos-release sign
* If you use a "non-Greenbone" project, you may set the argument `--space <my-workspace>`.
* The `--release-version` is not required, latest will be looked up in the project 
  definition, if not set explicitly

  ```sh
      poetry run pontos-release sign --release-version <version>
  ```
