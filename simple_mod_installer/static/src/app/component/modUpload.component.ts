import {Component, OnInit, OnDestroy, Inject} from '@angular/core';
import {CollectionListService} from "../service/collectionList.service";
import {ModService} from "../service/mod.service";
import {Observable} from "rxjs/Observable";
import {Http, RequestOptions, Headers} from "@angular/http";
import "rxjs/add/operator/map";
import "rxjs/add/operator/catch";
import "rxjs/add/observable/throw";
import {MD_DIALOG_DATA, MdDialogRef} from "@angular/material";
import {ServerMessage} from "../util";

const URL = "/mod/add/upload";

@Component({
  selector: 'app-mod-upload',
  templateUrl: './modUpload.component.html',
  providers: [ModService],
})

export class ModUploadComponent implements OnInit, OnDestroy {
    loading = false;

  ngOnInit(): void {}

  ngOnDestroy(): void {}

  fileChange(event) {
      this.loading = true;

      let fileList: FileList = event.target.files;
      if (fileList.length > 0) {
          let file: File = fileList[0];
          console.log(file.name);
          let formData:FormData = new FormData();
          formData.append('file', file, file.name);
          let headers = new Headers();
          /** No need to include Content-Type in Angular 4 */
          //headers.append('Content-Type', 'multipart/form-data');
          headers.append('Accept', 'application/json');
          let options = new RequestOptions({ headers: headers });
          this.http.post(`${URL}`, formData, options)
              .map(res => {
                  return new ServerMessage(res.json());
              })
              .subscribe(
                  response => {
                      // do the successful upload stuff
                      console.log('file uploaded successfully');
                      this.dialogRef.close(response);
                  }
              );
      }
  }

  constructor(
    private http: Http,
    @Inject(MD_DIALOG_DATA) public data: any, // To allow data to be passed in to it
    private dialogRef: MdDialogRef<ModUploadComponent>
  ) {}
}
