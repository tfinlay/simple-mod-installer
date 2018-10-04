# Curse integration specification

## Saved data for a mod

- Curse Id
    - For identifying if the local mod is from Curse in the first place, and which mod to look up in the curse database for more detail
- File Id
    - For identifying which exact file is installed, for update checking

## Search

- Search will access the Curse mod database, but will remove results from curse that meeting the following:
    - Are installed, at that version, locally (identified by the Curse id saved to the database, and the file id saved). In this case, the entire SearchMod will be exempted from results as the locally installed one is to be favored. If a newer file at the same version is available, an update will be displayed.
    - If a context is provided, only files matching the context's mc_version will be added, as other results are irrelevant.
- Locally installed mods will be preferred over Curse mods, they will be rewarded one point for this trait.
- Files that are not in release will not be rewarded a point that all other files are. If there is a file at the same mc_version that is slightly older than the un-released version it will be preferred for that mc_version, and the non-release version will not be saved.

## Updates

Local Curse mods can be update checked if they are saved with their curse id. If a newer file is available, in release, at the same mc version, the user will be asked whether they want to install the update.

