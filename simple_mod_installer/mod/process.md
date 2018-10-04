# Process

\- == application root

## Definitions

__mods__ - predefined to contain a generic 'mod' with everything set to _None_.

## Method

1. Read the MCMod.info file for the modfile
2. For each mod in the modfile, record it's data into __mods__
3. Check if the mods are already present in the database. (exec is__same__mod for every database entry with the same __modid__)
4. Move the modfile into -/mods.
    1. Check for double-up files. If one, goto is_same_mod, If none, continue with the move
4. Add every mod into in mods into the database.
    1. Set all of them to have the same __filename__

### is_same_mod (mod, mod2)

1. check if __mod.modid__ == __mod2.modid__ and mod.version == __mod2.version__ and __mod.mcversion__ == __mod2.mcversion__
    1. If so, ask if we want to continue, (return True)
    2. If not return just continue (return False)
