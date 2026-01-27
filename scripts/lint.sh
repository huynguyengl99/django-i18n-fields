#!/usr/bin/env bash

if [ "$1" == "--fix" ]; then
  ruff check . --fix && black ./i18n_fields && toml-sort ./*.toml
else
  ruff check . && black ./i18n_fields --check && toml-sort ./*.toml --check
fi
