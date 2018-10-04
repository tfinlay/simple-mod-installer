import {Component, OnInit, OnDestroy, Input, EventEmitter, Output, Inject, Injectable} from '@angular/core';
import {ActivatedRoute} from "@angular/router";
import {MD_DIALOG_DATA, MdDialogRef, MdSnackBar} from "@angular/material";
import {loadSearchModJson, SearchMod} from "../mod";
import {ModSelectorService} from "../service/modSelector.service";
import {Http, RequestOptions, Headers} from "@angular/http";
import {Observable} from "rxjs/Observable";
import 'rxjs/add/operator/catch';
import {ModService} from "../service/mod.service";

@Component({
  selector: 'app-err-popup',
  templateUrl: 'errPopup.component.html'
})

@Injectable()
export class ErrPopupComponent implements OnInit, OnDestroy {
  ngOnInit() { }

  ngOnDestroy() {
  }

  listActions() {

  }

  closeWithAction(res: string) {
      this.dialogRef.close(res);
  }

  constructor(
    private route: ActivatedRoute,
    private modSelectorService: ModSelectorService,
    private modService: ModService,
    private http: Http,
    private snackBar: MdSnackBar,
    @Inject(MD_DIALOG_DATA) public data: any, // To allow data to be passed in to it
    private dialogRef: MdDialogRef<ErrPopupComponent>
  ) {

  }
}
