@echo off

cd %~dp0

pyinstaller simple_mod_installer/__init__.py --add-data simple_mod_installer/static;static --add-data simple_mod_installer/templates;templates --exclude-module simple_mod_installer.testing