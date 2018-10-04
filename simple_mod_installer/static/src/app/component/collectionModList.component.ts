import { Component, OnInit, OnDestroy, Input, EventEmitter, Output } from '@angular/core';
import {ActivatedRoute} from "@angular/router";
import {issues, Mod} from "../mod";
import {MdDialog, MdSnackBar} from "@angular/material";
import {AddModSelectorComponent} from "./addModSelector.component";
import {ModService} from "../service/mod.service";
import {DEFAULT_SNACKBAR_CONFIG} from "../util";
import {CollectionService} from "../service/collection.service";
import {ModIssueViewComponent} from "./modIssueView.component";


@Component({
  selector: 'app-collection-mod-list',
  templateUrl: 'collectionModList.component.html'
})

export class CollectionModListComponent implements OnInit, OnDestroy {
    @Input() collId: number;

    mods: Mod[] = [];

    loading = true;

    ngOnInit() {
        this.loadModList();
    }

    _loadMcVersion() {
        // load mcversion issues into Mods
        this.collectionService.getMcVersionIssues(this.collId).subscribe(i => {
            console.log(`McVersion issues are: ${issues}`);
            for (let mod of this.mods) {
                if (i.indexOf(mod.id) !== -1) {
                    console.log(`Found mcVersion issue with mod: ${mod.id}`);
                    mod.issues.push({
                        type: issues.mcversion
                    });
                }
            }
        });
    }

    _loadDepChecks() {
        // load dependency issues into Mods
        this.collectionService.getDepIssues(this.collId).subscribe(i => {
            console.log(`Dependency issues are: ${issues}`);
            for (let mod of this.mods) {
                if (i.hasOwnProperty(mod.id)) {
                    mod.issues.push({
                        type: issues.dependency,
                        causing: i[mod.id]
                    });
                }
            }
        });
    }

    showIssuePopupForMod(mod: Mod) {
        // show the issues popup for a specific mod
        console.log(`Showing issue popup for mod: ${mod}`);

        let dialog = this.dialog.open(ModIssueViewComponent, {
            data: {
                mod: mod,
                collId: this.collId
            }
        });
    }

    loadModIssues(): void {
        // load the issues for each Mod

        this._loadMcVersion();
        this._loadDepChecks();
    }

    loadModList(): void {
        this.mods = [];
        this.loading = true;
        // load the modlist
        this.collectionService.getModData(this.collId).subscribe(data => {
            this.loading = false;

            this.mods = data;

            this.loadModIssues();
        });
    }

  remMod(modid: number): void {
    // Remove a particular mod from the collection, then refresh
    this.collectionService.remMod(this.collId, modid).subscribe(data => {
      this.loadModList(); // reload
      let snackBarRef = this.snackBar.open("Mod Removed", "Undo", DEFAULT_SNACKBAR_CONFIG);
      snackBarRef.onAction().subscribe(() => {
        // Re-link mod
        this.modService.linkMod(this.collId, modid).subscribe(next => {
          snackBarRef.dismiss();
          this.loadModList();
        });
      });
    });
  }

  openAddModDialog(): void {
      let dialog = this.dialog.open(AddModSelectorComponent, {
          data: {
              collId: this.collId,
              search_installed: true,
              search_remote: true
          }
      });

      dialog.afterClosed().subscribe(snackbarRef => {
          this.loadModList();
          snackbarRef.onAction().subscribe(() => {
              this.loadModList();
          });
      });
  }

    ngOnDestroy() {
    }

    constructor(
        private route: ActivatedRoute,
        private collectionService: CollectionService,
        private modService: ModService,
        private dialog: MdDialog,
        private snackBar: MdSnackBar
    ) {}
}
