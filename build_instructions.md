# Build instructions

1. Download [Electron prebuilt binaries](https://github.com/electron/electron/releases)
2. Create directory: `simple mod installer` in `/build`
3. Copy the downloaded binaries into this folder
4. Create folder `simple mod installer\resources\app`
5. Copy files from simple-mod-installer-shell into here
6. Create directory `simple mod installer\resources\app\bin`
7. Do `Building python (to put in bin) - Windows` steps
8. Edit `electon.exe` to `smi.exe`, and update icon
9. Create installer in Visual Studio

## Building python (to put in bin) - Windows

1. Download the Python 3.6.* embeddable zip file, and unzip it into the `bin` folder
2. Download each of the required libraries, and drop them into `bin` alongside the Python files
3. Copy the `simple_mod_installer` directory (containing `__init__.py`) into the `bin` folder too.
4. Delete everything in static except `dist`