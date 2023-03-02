#!/bin/bash

# install oh-my-zsh
wget https://github.com/robbyrussell/oh-my-zsh/raw/master/tools/install.sh -O - | zsh || true

# install application
pip install -e '.[testing]' --upgrade
{{cookiecutter.project_slug}}_initialize_db development-docker.ini