import { Injectable } from '@angular/core';
import {CollectionMini} from "../collection";
import {Http, Response} from "@angular/http";
import 'rxjs/add/operator/map';
import {loadModJson} from "../mod";

@Injectable()
export class CollectionListService {
  constructor(private http: Http) {}

  getCollections() {
    return this.http.get('/collection.json')
      .map(( res:Response ) => loadModJson(res.json()));
  }

  /*getColls(): any {
    this._http.get<CollectionMini>('/collection.json').retry(3).subscribe(
      data => {
        // return that data
        console.log("Service got data:");
        console.log(data);
        return Promise.resolve(data);
      },
      (err: HttpErrorResponse) => {
        if (err.error instanceof Error) {
          console.warn("An error occurred:", err.error.message);
        } else {
          console.warn("Bad response code (" + err.status + ") for CollectionListService! Body was", err.error);
        }
      }
    );
  }*/
}
