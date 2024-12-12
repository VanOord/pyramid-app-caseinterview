#!/bin/bash

# install oh-my-zsh
wget https://github.com/robbyrussell/oh-my-zsh/raw/master/tools/install.sh -O - | zsh || true

# install application
pip install -e '.[testing]' --upgrade
pyramid_app_caseinterview_initialize_db development-docker.ini