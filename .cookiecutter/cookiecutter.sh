#!/bin/bash

# don't run when in template directory
pwd=`pwd`
base=`basename $pwd`
if [ $base = "template-pyramid-app" ]; then
    exit
fi

# link template repo and merge latest changes
git remote -v | grep -w template || git remote add template https://github.com/VanOord/template-pyramid-app.git
git fetch template master
git merge template/master --allow-unrelated-histories --no-commit

# create cookiecutter environment
pip install cookiecutter --upgrade
REPLAYFILE=.cookiecutter/cookiecutter.replay.json
REPLAYFILESRC=~/.cookiecutter_replay/template.json

# create template environment
TMPDIR=$(mktemp -u)
echo "Using working directory: $TMPDIR..."
mkdir -p $TMPDIR/template/{{cookiecutter.project_repo}}
cp -r . $TMPDIR/template/{{cookiecutter.project_repo}}
rm -rf $TMPDIR/template/{{cookiecutter.project_repo}}/.git
rm -rf $TMPDIR/template/{{cookiecutter.project_repo}}/.cookiecutter
cp -r .cookiecutter/. $TMPDIR/template
mkdir -p $TMPDIR/rendered

# apply cookiecutter
if [ -f "$REPLAYFILE" ]; then
    echo "Using replay file: $REPLAYFILE"
    cookiecutter -f -o $TMPDIR/rendered $TMPDIR/template --replay-file ./$REPLAYFILE
else 
    cookiecutter -f -o $TMPDIR/rendered $TMPDIR/template
fi

# copy result
cp -r $TMPDIR/rendered/*/. .
if [ ! -f "$REPLAYFILE" ] && [ -f "$REPLAYFILESRC" ]; then
    cp -r $REPLAYFILESRC $REPLAYFILE
fi

# clean up
find . -iname '{{*}}' -delete
rm -rf $TMPDIR
