import {stringifyArray, getFilename} from "./util";
import {CollectionMini} from "./collection";

export class Mod {
    id: number;
    filename: string;

    name: string;
    modid: string;
    version: string;
    mc_version: string;
    description: string;
    credits: string;

    hasIssues = false;
    issues: issue[] = [];

    constructor(id, filename, name, modid, version, mc_version, description, credits) {
        this.id = id;
        this.filename = filename;
        this.name = name;
        this.modid = modid;
        this.version = version;
        this.mc_version = mc_version;
        this.description = description;
        this.credits = credits;
    }

    getName() {
        if (!this.name) {
            if (this.filename) {
                return this.filename;
            } else {
                return "Unnamed Mod";
            }
        } else {
            return this.name;
        }
    }
}

/*
* Issues
*/

export const issues = {  // predefined issueTypes
    mcversion: {issueId: 0, name: 'Minecraft Version', description: 'This mod doesn\'t support the Minecraft Version that this collection is using.'},
    dependency: {issueId: 1, name: 'Dependency', description: 'This mod is missing one or more of the mods that it depends on.'}
};


export interface issue {
    // an issue type, and (if applicable), the
    type: issueType;

    causing?: any[];  // array of the things which are causing this issue (for this mod, if applicable) i.e. modids which are missing (for depcheck)
}


export interface issueType {
    issueId: number; // internal name, 0: mcVersion, 1: dependencyMissing

    // human interface
    name: string;
    description: string;
}

/*
* Searching
*/

export class SearchMod {
  name: string;
  curse_id: string;
  local_id: number;
  versions: version[];
  authors: string[];
  is_installed = false;

  // Frontend data
  selectedVersion: string;
  installing = false;

  constructor(name, curse_id, local_id, versions, authors) {
      this.name = name;
      this.curse_id = curse_id;
      this.local_id = local_id;
      this.versions = versions;
      this.authors = authors;

      if (Object.keys(this.versions).length === 1) {
          this.selectedVersion = Object.keys(this.versions)[0];
      }

      if (this.local_id != null && Object.keys(this.versions).length === 1) {
          console.log("Mod: " + name + " is installed!");
          this.is_installed = true;
      }
  }

  getVersions() {
      let x = [];
      for (let key in this.versions) {
          x.push(key);
      }

      return x;
  }

  getFilenames() {
      let x = [];
      for (let key in this.versions) {
          x.push(this.versions[key].filename);
      }

      return x;
  }

  getAuthors() {
      if (this.authors.length > 0) {
          return stringifyArray(this.authors);
      } else {
          return 'Unkown';
      }
  }

  getName() {
      if (!this.name) {
          for (let key in this.versions) {
              if (this.versions[key].installed) {
                  return this.versions[key].filename;
              } else {
                  return getFilename(this.versions[key].dl_url);
              }
          }
          return "Unnamed Mod";
      } else {
          return this.name;
      }
  }
}


interface version {
    installed: boolean;
    filename: boolean;
    dl_url: string;
    file_id: string;
}


export function loadModJson(data: Mod[]): Mod[] {
    let x = [];

    for (let m in data) {
        x.push(new Mod(
            data[m].id,
            data[m].filename,
            data[m].name,
            data[m].modid,
            data[m].version,
            data[m].mc_version,
            data[m].description,
            data[m].credits
        ));
    }

    return x;
}

export function loadSearchModJson(data: SearchMod[]): SearchMod[] {
    let x = [];

    for (let m in data) {
        x.push(new SearchMod(
            data[m].name,
            data[m].curse_id,
            data[m].local_id,
            data[m].versions,
            data[m].authors
        ));
    }

    return x;
}
