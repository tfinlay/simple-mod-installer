import { Component, OnInit, OnDestroy, Input, EventEmitter, Output, Inject } from '@angular/core';
import {ActivatedRoute} from "@angular/router";
import {MD_DIALOG_DATA, MdDialog, MdDialogRef, MdSnackBar} from "@angular/material";
import {loadSearchModJson, Mod, SearchMod} from "../mod";
import {ModSelectorService} from "../service/modSelector.service";
import {Http, RequestOptions, Headers} from "@angular/http";
import {Observable} from "rxjs/Observable";
import 'rxjs/add/operator/catch';
import {ModService} from "../service/mod.service";
import {ErrPopupComponent} from "./errPopup.component";
import {DEFAULT_SNACKBAR_CONFIG, ServerMessage} from "../util";
import 'rxjs/Observable';
import {isUndefined} from "util";
import {CollectionService} from "../service/collection.service";
import {ModUploadComponent} from "./modUpload.component";

@Component({
  selector: 'app-add-mod-selector',
  templateUrl: 'addModSelector.component.html'
})

export class AddModSelectorComponent implements OnInit, OnDestroy {
  mods: SearchMod[] = [];
  sub: any;
  modUploadEndpoint = "";

  searchTerm = "";
  searchMade = false;

  ngOnInit() { }

  fileChange(event) {
    let fileList: any = event.target.files;

    if (fileList.length > 0) {
      console.log(fileList);

      let file: File = fileList[0];
      let formData:FormData = new FormData();
      formData.append('file', file, file.name);
      this.http.post(`${this.modUploadEndpoint}`, formData)
          .map(res => res.json())
          .catch(error => Observable.throw(error))
          .subscribe(
              data => console.log('success'),
              error => console.log(error)
          );
    }
  }

  searchMods(form) {
      this.searchMade = true;

      console.log("Search request gotten.");
      console.log("Term is: " + form.term);

      const term = form.term;

      // Do a mod search request
      if (term.length > 0) { // let there be a term
        this.modService.searchMods(
            term,
            this.data.collId,
            this.data.search_installed,
            this.data.search_remote
        ).subscribe(data => {
            this.mods = loadSearchModJson(data);
        });
      }
  }

  _downloadMod(mod: SearchMod, overwrite = false) {
      // Download the Curse Mod
      const curse_id = mod.curse_id;
      const file_id = mod.versions[mod.selectedVersion].file_id;
      const url = mod.versions[mod.selectedVersion].dl_url;

      let promise = new Promise((resolve, reject) => {
          setTimeout(() => {
              this.modService.installCurseMod(
                  curse_id,
                  file_id,
                  url,
                  overwrite
              ).subscribe(response => {
                  if (response.success) {
                      console.log(`success, got modid: ${response.data.modid}`);
                      resolve(response.data.modid);
                  } else {
                      console.log("failed");

                      let dialogRef = this.dialog.open(ErrPopupComponent, {
                          data: {
                              errInfo: {
                                  title: response.errInfo.title,
                                  body: response.errInfo.title
                              },
                              actions: [
                                  "Cancel",
                                  "Continue installation"
                              ]
                          }
                      });

                      dialogRef.afterClosed().subscribe(result => {
                          if (result === 1) {
                              this._downloadMod(mod, true).then(modid => {
                                  resolve(modid); // cascade resolution upwards
                              },
                              () => {
                                  reject();
                              });
                          } else {
                              reject();
                          }
                      });
                  }
              });
          }, 1000);
      });
      return promise;
  }

  _verifySelectedVersion(mod: SearchMod) {
      let promise = new Promise((resolve, reject) => {
          if (isUndefined(mod.selectedVersion)) {
              console.log("selectedVersion is undefined, asking for the user to select one...");

              console.log(this.data.collId);

              const showVersionErrorPopup = () => {
                  // ask the user to select a version
                  this.dialog.open(ErrPopupComponent, {
                      data: {
                          errInfo: {
                              title: "Which one?",
                              body: "Please select a Minecraft version from the dropdown underneath the mod name, we couldn't figure out which one you want!"
                          },
                          actions: [
                              'close'
                          ]
                      }
                  });
                  reject();
              };

              if (this.data.collId) {
                  // We have a context
                  this.collectionService.getCollectionData(this.data.collId).subscribe(data => {
                      console.log(`checking if ${data.mc_version} is in ${Object.keys(mod.versions)}`);
                      if (Object.keys(mod.versions).indexOf(data.mc_version) != -1) {
                          // guess which version they want
                          mod.selectedVersion = data.mc_version;
                          console.log(`Successfully guessed that they want version: ${mod.selectedVersion}`);

                          resolve();
                      } else {
                          showVersionErrorPopup();
                      }
                  });
              } else {
                  // We have no context, so we can't attempt a guess, just raise the error popup right away
                  showVersionErrorPopup();
              }
          } else {
              resolve();
          }
      });

      return promise;
  }

  reloadSearch() {
      this.searchMods({term: this.searchTerm});  // reload
  }

  _afterInstall(mod: SearchMod, status = {success: false}) {
      // called after installation methods, no matter whether they fail or succeed
      mod.installing = false;

      if (status.success) {
          this.reloadSearch();
      }
  }

  downloadLinkMod(mod: SearchMod) {
      mod.installing = true;

      console.log(`downloading mod: ${mod} @ mcversion: ${mod.selectedVersion} from Curse...`);

      this._verifySelectedVersion(mod).then(
          success => {

              console.log("mod version successfully verified!");

              // download and link a Curse mod
              this._downloadMod(mod).then((modid: number) => {
                  console.log(`Mod id is: ${modid}`);
                  if (this.data.collId) {
                      console.log(`collId is specified, linking as well...`);
                      this.linkMod(modid);
                  } else {
                      // we're done here...
                      this.snackBar.open("Mod downloaded", null, DEFAULT_SNACKBAR_CONFIG);
                  }
                  this._afterInstall(mod, {success: true});
              },
              (err) => {
                  console.warn(`downloaded mod failed or was cancelled. Code is: ${err}`)
                  this._afterInstall(mod);
              });
          },
          err => {
              console.log("mod version was invalid");
              this._afterInstall(mod);
          }
      );
  }

  linkMod(id: number) {
      // link an already installed mod
      if (this.data.collId) {
        this.modService.linkMod(this.data.collId, id).subscribe(response => {
            if (response.success) {
                let snackBarRef = this.snackBar.open("Mod linked", "Undo", DEFAULT_SNACKBAR_CONFIG);
                snackBarRef.onAction().subscribe(() => {
                    // unlink mod again
                    this.modService.unlinkMod(this.data.collId, id).subscribe(next => {
                        snackBarRef.dismiss();
                    });
                });

                this.dialogRef.close(snackBarRef);

            } else {
                let dialogRef = this.dialog.open(ErrPopupComponent, {
                    data: response
                });
                dialogRef.afterClosed().subscribe(result => {
                    console.log(`Dialog results: ${result}`);
                });
            }
          });
      }
  }

    uploadMod() {
        let x = this.dialog.open(ModUploadComponent);
        x.afterClosed().subscribe(response => {
            if (response.success) {
                if (this.data.collId) {
                    // we have a collection, so link
                    this.linkMod(response.data.modid);
                } else {
                    this.snackBar.open("Mod uploaded successfully", null, DEFAULT_SNACKBAR_CONFIG);
                }
            } else {
                this.dialog.open(ErrPopupComponent, {
                    data: response
                });
            }
        });
    }

  ngOnDestroy() {
  }

  constructor(
    private route: ActivatedRoute,
    private modSelectorService: ModSelectorService,
    private modService: ModService,
    private collectionService: CollectionService,
    private http: Http,
    private snackBar: MdSnackBar,
    @Inject(MD_DIALOG_DATA) public data: any, // To allow data to be passed in to it
    private dialogRef: MdDialogRef<AddModSelectorComponent>,
    private dialog: MdDialog
  ) {}
}
