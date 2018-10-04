import { Component, OnInit, OnDestroy } from '@angular/core';
import {Router} from "@angular/router";
import {CollectionMini} from "../collection";
import {CollectionListService} from "../service/collectionList.service";
import {MdDialog, MdSnackBar} from "@angular/material";
import {CreateCollectionComponent} from "./createCollection.component";
import {DEFAULT_SNACKBAR_CONFIG} from "../util";
import {HowToPlayComponent} from "./howToPlay.component";
import {CollectionService} from "../service/collection.service";

@Component({
  selector: 'app-collectionlist',
  templateUrl: './collectionlist.component.html',
  providers: [CollectionListService]
})

export class CollectionListComponent implements OnInit, OnDestroy {
  collections: CollectionMini[] = [];
  sub: any;
  router: Router;

  loading = true;

  constructor(
    private _collectionListService: CollectionListService,
    private collectionService: CollectionService,
    private r: Router,
    private dialog: MdDialog,
    private snackbar: MdSnackBar
  ) {
    this.router = r;
  }

  ngOnInit(): void {
    this.getCollections();
  }

  ngOnDestroy(): void {
    this.sub.unsubscribe();
  }

  getCollections(): void {
    /*
    this._collectionListService.getCollections().then(
      (colls: CollectionMini[]) => {
        this.collections = colls; console.log(this.collections);
      });*/
    this.loading = true;
    this.sub = this._collectionListService.getCollections().subscribe(
      colls => {
        this.collections = colls;
        console.log(colls);
        this.loading = false;
      }
      );
  }

  showAddCollectionDialog(): void {
      let ref = this.dialog.open(CreateCollectionComponent, {});

      ref.afterClosed().subscribe(collid => {
          if (collid) {  // if the dialog succeeded
              this.snackbar.open('Collection Created', null, DEFAULT_SNACKBAR_CONFIG);
              this.router.navigate(['collection', collid]);
          }
      });
  }

  playCollection(id): void {
      // show dialog telling the user how to
      this.dialog.open(HowToPlayComponent);
  }

  delColl(id): void {
      this.collectionService.deleteCollection(id).subscribe(res => {
          this.snackbar.open("Collection Deleted", "", DEFAULT_SNACKBAR_CONFIG);
          this.getCollections();
      });
  }

  routeToCollection(id): void {
    this.router.navigate(['collection', id]);
  }
}
