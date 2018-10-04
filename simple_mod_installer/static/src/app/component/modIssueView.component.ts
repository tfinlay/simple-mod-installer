import {Component, Inject, OnInit} from '@angular/core';
import {MD_DIALOG_DATA, MdDialogRef} from "@angular/material";
import {CollectionService} from "../service/collection.service";
import {Collection} from "../collection";

@Component({
  selector: 'app-mod-issue-view',
  templateUrl: './modIssueView.component.html'
})

export class ModIssueViewComponent implements OnInit {
    collection: Collection = new Collection();

    constructor(
        private dialogRef: MdDialogRef<ModIssueViewComponent>,
        @Inject(MD_DIALOG_DATA) private data: any,
        private collectionService: CollectionService
    ) {}

    getCollData() {
        // get collection data for some hints
        this.collectionService.getCollectionData(this.data.collId).subscribe(info => {
            this.collection = new Collection(info.id, info.name, info.mc_version, info.version_id, info.epoch_created);
        });
    }

    ngOnInit() {
        this.getCollData();
    }
}

