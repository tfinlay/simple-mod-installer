import { Component, OnInit, OnDestroy } from '@angular/core';
import {Router} from "@angular/router";
import {SearchMod, loadSearchModJson} from "../mod";
import {MdDialog, MdSnackBar} from "@angular/material";
import {AddModSelectorComponent} from "./addModSelector.component";
import {ModService} from "../service/mod.service";
import {DEFAULT_SNACKBAR_CONFIG} from "../util";

@Component({
  selector: 'app-modlist',
  templateUrl: './modList.component.html'
})

export class ModListComponent implements OnInit, OnDestroy {
    mods: SearchMod[] = [];

    loading = true;

    constructor(
        private router: Router,
        private dialog: MdDialog,
        private modService: ModService,
        private snackbar: MdSnackBar
    ) {}

    ngOnInit(): void {
        this.getModList();
    }

    ngOnDestroy(): void {}

    getModList() {
        this.loading = true;
        this.modService.searchMods("", null, true, false).subscribe(data => {
            this.mods = loadSearchModJson(data);
            this.loading = false;
        });
    }

    openAddModDialog() {
        let dialog = this.dialog.open(AddModSelectorComponent, {
            data: {
                search_installed: false,
                search_remote: true
            }
        });

        dialog.afterClosed().subscribe(() => {
            // refresh
            this.getModList();
        });
    }

    routeToMod(id: number) {
        this.router.navigate(['mod', id]);
    }

    delMod(id: number) {
        this.modService.delMod(id).subscribe(res => {
            if (res.success) {
                this.snackbar.open("Mod deleted", null, DEFAULT_SNACKBAR_CONFIG);
                this.getModList();
            } else {
                let x = this.snackbar.open("Mod deletion failed", "retry", DEFAULT_SNACKBAR_CONFIG);
                x.onAction().subscribe(() => {
                    this.delMod(id);
                });
            }
        });
    }
}
