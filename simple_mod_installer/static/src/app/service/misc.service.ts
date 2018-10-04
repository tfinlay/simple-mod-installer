import { Injectable } from '@angular/core';
import {CollectionMini} from "../collection";
import {Http, RequestOptions, Response, URLSearchParams} from "@angular/http";
import 'rxjs/add/operator/map';
import {ServerMessage} from "../util";
import {loadModJson} from "../mod";

@Injectable()
export class MiscService {
    constructor(private http: Http) {}

    getLocalMcVersions() {
        return this.http.get('/api/mcversions').map((res: Response) => res.json());
    }
}
