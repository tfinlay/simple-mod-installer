# Simple Mod Install v3 data structure

Collection -> Mod

Every Collection links to many Mods.

Mods (their files) are stored in a central repository (/mods). Collections contain symlinks to the mod files.

This means that one Mod file can be used across many Collections without using lots of disk space. This also simplifies data storage, as there should only be one of every mod file (for any given mod and version).

To retain this, when mods are imported (either via CurseForge, Technic, or manual import) both their file name, and their mcmod.info will be checked against the database. If matching file name and/or metadata is found, we ask the user if they really do want to have a duplicate mod.

If yes, rename file and create new Mod instance.
If no, cancel import of that specific file, and instead use the existing file.