export class CollectionMini {
  id: number;
  name: string;
  mc_version: string;
}

export class Collection {
  id: number;
  name: string;
  mc_version: string;
  version_id: string;
  epoch_created: number;
  mods: number[];

  constructor(id = null, name = null, mc_version = null, version_id = null, epoch_created = null) {
      this.id = id;
      this.name = name;
      this.mc_version = mc_version;
      this.version_id = version_id;
      this.epoch_created = epoch_created;
  }
}
