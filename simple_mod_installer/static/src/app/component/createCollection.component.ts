import {Component, OnInit, OnDestroy, Input, EventEmitter, Output, Inject} from '@angular/core';
import {ActivatedRoute, Router} from "@angular/router";
import {MD_DIALOG_DATA, MdDialog, MdDialogRef} from "@angular/material";
import {CollectionService} from "../service/collection.service";
import {Collection} from "../collection";
import {MiscService} from "../service/misc.service";
import {ErrPopupComponent} from "./errPopup.component";


@Component({
  selector: 'app-create-collection-form',
  templateUrl: 'createCollection.component.html'
})

export class CreateCollectionComponent implements OnInit, OnDestroy {
    coll = new Collection();
    versions: string[];

    submitted = false;

    ngOnInit() {
        this._loadMcVersions();
    }

    ngOnDestroy() {}

    _loadMcVersions() {
        // download valid minecraft versions from the server...
        this.miscService.getLocalMcVersions().subscribe(data => {
            this.versions = data;
        });
    }

    onSubmit({value, valid}) {
        // Submit the form
        this.submitted = true;

        console.log("Form submitting...");
        console.log(value, valid);

        this.collectionService.addCollection(
            value.name,
            value.mc_version,
            value.version_id
        ).subscribe(data => {
            if (data.success) {
                this.dialogRef.close(data.data.collid);
            } else {
                this.dialog.open(ErrPopupComponent, {
                    data: data
                });
                this.submitted = false;
            }
        });

        console.log(`Submitting form w/ data`);
    }

    constructor(
        private route: ActivatedRoute,
        private router: Router,
        private collectionService: CollectionService,
        private miscService: MiscService,
        @Inject(MD_DIALOG_DATA) public data: any, // To allow data to be passed in to it
        private dialogRef: MdDialogRef<CreateCollectionComponent>,
        private dialog: MdDialog
    ) {}
}
