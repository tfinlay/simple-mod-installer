import { Injectable } from '@angular/core';
import {Http, RequestOptions, Response, URLSearchParams} from "@angular/http";
import 'rxjs/add/operator/map';

@Injectable()
export class ModSelectorService {
  constructor(private http: Http) {}

  private getBaseURL(id: number): string {
    return "/mod/" + id;
  }

  getModList(collId: number, searchTerm: string = "") {
    // Get an initial list of mods
    const url = "/mod/search?context=" + collId + "&term=%" + searchTerm + "%";

    return this.http.get(url)
      .map((res: Response) => res.json());
  }
}
