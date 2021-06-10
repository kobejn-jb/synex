#!/bin/bash
BLACK_EXCLUDE="/(\.eggs|\.git|\.hg|\.mypy_cache|\.tox|\.venv|_build|buck-out|build|dist)/"
PYTHON_MODULES=$(find -name [a-z]*.py)
OUT_DIR=${2}/

if [ ${1} = "black" ]; then
  black . -l 120 -S -t py36 --check --diff --exclude ${BLACK_EXCLUDE} > ${OUT_DIR}black.out
elif [ ${1} = "black-fix" ]; then
  black . -l 120 -S -t py36 --exclude ${BLACK_EXCLUDE}
elif [ ${1} = "stylecheck" ]; then
  black . -l 120 -S -t py36 --check --diff --exclude ${BLACK_EXCLUDE} > ${OUT_DIR}black.out
  pylint -j 4 ${PYTHON_MODULES} > ${OUT_DIR}pylint.out
elif [ ${1} = "pylint" ]; then
  pylint -j 4 ${PYTHON_MODULES} > ${OUT_DIR}pylint.out
fi
