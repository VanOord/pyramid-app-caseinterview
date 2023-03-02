#!/bin/bash
pip install cookiecutter --upgrade
tmpdir=$(mktemp -u)
echo "Using $tmpdir..."
mkdir -p $tmpdir/template/{{cookiecutter.project_repo}}
cp -r . $tmpdir/template/{{cookiecutter.project_repo}}
rm -rf $tmpdir/template/{{cookiecutter.project_repo}}/.git
rm -rf $tmpdir/template/{{cookiecutter.project_repo}}/cookiecutter.*
cp -r cookiecutter.* $tmpdir/template
mkdir -p $tmpdir/rendered
cookiecutter -f -o $tmpdir/rendered $tmpdir/template
cp -r $tmpdir/rendered/*/* .
rm -rf $tmpdir