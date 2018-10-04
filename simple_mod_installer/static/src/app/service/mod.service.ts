import { Injectable } from '@angular/core';
import {Http, RequestOptions, Response, URLSearchParams} from "@angular/http";
import 'rxjs/add/operator/map';
import {ServerMessage} from "../util";

@Injectable()
export class ModService {
  constructor(private http: Http) {}

  private getBaseURL(id: number): string {
    return "/mod/" + id;
  }

  linkMod(collId: number, modId: number) {
    // Links a mod to a collection
    const url = "/collection/" + collId + "/add_mod?id=" + modId;

    return this.http.post(url, "").map(data => {
      return new ServerMessage(data.json());
    });
  }

  searchMods(term: string = "", collId: number = null, search_local = true, search_remote = true) {
      let url = "/mod/search?local=" + search_local + "&remote=" + search_remote + "&term=" + term;

      if (collId != null) {
          url += "&context=" + collId;
      }

      return this.http.get(url)
          .map((res: Response) => res.json());
  }

  unlinkMod(collId: number, id: number) {
      const url = '/collection/' + collId + "/rem_mod?id=" + id;

      return this.http.post(url, "").map((res: Response) => {
          return new ServerMessage(res.json());
      });
  }

  installCurseMod(curse_id: string, file_id: string, url: string, overwrite = false) {
      const u = '/mod/add/curse?curse_id=' + curse_id + '&file_id=' + file_id + '&overwrite=' + overwrite + '&url=' + url;

      return this.http.post(u, "").map((res: Response) => {
          return new ServerMessage(res.json());
      });
  }

  delMod(id: number) {
      const url = `/mod/remove?id=${id}`;

      return this.http.post(url, "").map((res: Response) => {
          return new ServerMessage(res.json());
      });
  }
}
