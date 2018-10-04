# Simple Mod Installer / SimpleLauncher

The next version of the original [Simple Mod Installer](https://github.com/tfff1OFFICIAL/Simple-Mod-Installer-Master).

This project is a complete re-write and re-think of the Simple Mod Installer.

## The Features

* Easy-to-use Web UI
    * locally hosted, not available to the Network or to the Web
    * Works offline
* Mod Collections
    * Harnessing the launcher_config.json of Minecraft's launcher.
    * Powered by a central Mod Pool on the user's computer, so that the same mod can be used in many Collections' without using additional hard disk space.
    * Import from Technic ([See the docs](https://github.com/tfff1OFFICIAL/Technicpack-API-Docs))
    * Easily select from a list of pre-installed mods for addition to the modpack
* Modpack Support
    * Export Collection's to Technic and Curse
    * Automatic packaging of correct Forge version for the Collection (the one which is used at the time of export)
* Mods
    * Stored centrally and referenced by Symbolic Links in all of the collections that it is used in.
    * McMod.info is parsed for:
        * Name: for use in searches for the mod (e.g. when adding it to a collection) for reading by humans (e.g. in Collection View)
        * MCVersion: The version of Vanilla Minecraft that the mod is built for. Used for search narrowing and to highlight potential compatibility issues
        * Dependencies: for highlighting potential issues
    * If a modfile contains multiple mods (stated by the mod in the mcmod.info file) then each 'mod' in the file is added to the Database separately, then when mod lists are generated 5 'mod' names are displayed for the one file.
    * Identical modfiles can be added to the Mod Pool. However, they must have a different filename and the user must confirm that they want to do this (it'll be detected during import)
    * Can be uploaded from PC, imported from CurseForge, or downloaded from URL (must be direct download URL)
* Version Checking
    * Checks mods against each other, and the version of Forge installed for compatibility.
    * Checks and warns if the currently installed Forge version isn't the 'Recommended' release for that Minecraft Version.