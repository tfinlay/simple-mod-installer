import { Injectable } from '@angular/core';
import {CollectionMini} from "../collection";
import {Http, RequestOptions, Response, URLSearchParams} from "@angular/http";
import 'rxjs/add/operator/map';
import {ServerMessage} from "../util";
import {loadModJson} from "../mod";

@Injectable()
export class CollectionService {
    constructor(private http: Http) {}

    private getBaseURL(id: number): string {
        return "/collection/" + id;
    }

    getCollectionData(id: number) {
        let url = this.getBaseURL(id) + ".json";

        return this.http.get(url)
          .map(( res: Response ) => res.json());
    }

    getModData(id: number) { // -> Mod
        let url = this.getBaseURL(id) + "/mods.json";

        return this.http.get(url)
          .map((res: Response) => loadModJson(res.json()));
    }

    addMod(collId: number, modId: number) {
        let url = this.getBaseURL(collId) + "add_mod?id=" + modId;
        return this.http.post(url, "").map((res: Response) => {
            return new ServerMessage(res.json());
        });
    }

    addCollection(name, mc_version, version_id) {
        const url = `/collection/add?name=${name}&mcversion=${mc_version}&version-id=${version_id}`;
        return this.http.post(url, "").map((res: Response) => {
            return new ServerMessage(res.json());
        });
    }

    remMod(collId: number, modId: number) {
        let url = this.getBaseURL(collId) + "/rem_mod?id=" + modId;
        return this.http.post(url, "").map((res: Response) => {
            return new ServerMessage(res.json());
        });
    }

    getMcVersionIssues(collId: number) {
        const url = this.getBaseURL(collId) + '/issues/mcversion';

        return this.http.get(url).map((res: Response) => {
            return res.json();
        });
    }

    getDepIssues(collId: number) {
        const url = this.getBaseURL(collId) + '/issues/depcheck';

        return this.http.get(url).map((res: Response) => {
            return res.json();
        });
    }

    exploreCollection(collId: number) {
        const url = this.getBaseURL(collId) + '/browse';

        return this.http.post(url, "").map((res: Response) => {
            return res.json();
        });
    }

    deleteCollection(collId: number) {
        const url = `collection/remove?id=${collId}`;

        return this.http.post(url, "").map((res: Response) => {
            return res;
        });
    }
}
