#!/bin/bash

# install oh-my-zsh
wget https://github.com/robbyrussell/oh-my-zsh/raw/master/tools/install.sh -O - | zsh || true

# set Van Oord pypi as default
export PIP_INDEX_URL=https://$PIP_ACCESS_TOKEN@pkgs.dev.azure.com/VanOord-IT/VanOord_Artifacts/_packaging/VanOord_Artifacts/pypi/simple/

# install application
pip install -e '.[testing]' --upgrade
pyramid_app_caseinterview_initialize_db development-docker.ini