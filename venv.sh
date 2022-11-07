#!/usr/bin/env bash
rm -rf env
python3.8 -m venv env
source "env/bin/activate"
pip3.8 install --upgrade pip

pip3.8 install -r requirements.txt

pip3.8 install -r requirements-tests.txt
