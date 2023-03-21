#!/bin/bash
pip install cookiecutter --upgrade
REPLAYFILE=.cookiecutter/cookiecutter.replay.json
REPLAYFILESRC=~/.cookiecutter_replay/template.json
TMPDIR=$(mktemp -u)
echo "Using working directory: $TMPDIR..."
mkdir -p $TMPDIR/template/{{cookiecutter.project_repo}}
cp -r . $TMPDIR/template/{{cookiecutter.project_repo}}
rm -rf $TMPDIR/template/{{cookiecutter.project_repo}}/.git
rm -rf $TMPDIR/template/{{cookiecutter.project_repo}}/.cookiecutter
cp -r .cookiecutter/* $TMPDIR/template
mkdir -p $TMPDIR/rendered
if [ -f "$REPLAYFILE" ]; then
    echo "Using replay file: $REPLAYFILE"
    cookiecutter -f --replay-file ./$REPLAYFILE -o $TMPDIR/rendered $TMPDIR/template
else 
    cookiecutter -f -o $TMPDIR/rendered $TMPDIR/template
fi
cp -r $TMPDIR/rendered/*/* .
if [ -f "$REPLAYFILESRC" ]; then
    cp -r $REPLAYFILESRC $REPLAYFILE
fi
rm -rf {{*}}
rm -rf $TMPDIR