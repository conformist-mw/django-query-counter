# Changelog

## 0.6.0

- drop end-of-life Python 3.9 and Django 3.2/4.0/4.1 (minimum is now Python 3.10 / Django 4.2)
- automate PyPI publishing and GitHub releases on tag push
- remove obsolete `default_app_config` shim and minor code cleanup

## 0.5.0

- added DQC_ENABLED setting to disable output (#24)

## 0.4.2

- added check for django6/py3.14

## 0.4.1

- migrate to uv
- migrate meta to pyproject.toml

## 0.4.0

- integrate github actions
- fix py38 support

## 0.3.1

- fix an unclosed curly bracket
- introduce .gitignore

## 0.3.0

- prettify markdown files
- add smoke tests using tox

## 0.2.2

- fix decorator type in README.md (Thanks @MichaelAquilina)

## 0.2.1

- fix `DEFAULTS` settings typo
- suppress Django default_app_config warning

## 0.2.0

- fix the view/func name after the sql stats table
- move stats table to the bottom
- introduce CHANGELOG.md (Thanks @DmytroLitvinov)

## 0.1.0

- add base implementation of the decorator/middleware
- introduce setup.py to publish on PyPI
