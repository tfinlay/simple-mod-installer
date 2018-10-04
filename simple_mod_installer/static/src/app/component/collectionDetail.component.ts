import { Component, OnInit, OnDestroy, Input, EventEmitter, Output } from '@angular/core';
import {ActivatedRoute, Router} from "@angular/router";
import {CollectionService} from "../service/collection.service";


@Component({
  selector: 'app-collection-detail',
  templateUrl: 'collectionDetail.component.html'
})

export class CollectionDetailComponent implements OnInit, OnDestroy {
    id: number;
    name: string;
    mc_version: string;
    version_id: string;
    epoch_created: number;
    date_created;

    route_sub: any;
    collData_sub: any;

    ngOnInit() {
    this.route_sub = this.route.params.subscribe(params => {
        this.id = +params["id"];
        this.getCollData();
    });
    }

    getCollData() {
        this.collData_sub = this.collectionService.getCollectionData(this.id).subscribe( data => {
            this.name = data["name"];
            this.mc_version = data["mc_version"];
            this.version_id = data["version_id"];
            this.epoch_created = +data["epoch_created"];
            this.date_created = new Date(this.epoch_created * 1000);
        },err => {
            this.router.navigate(['/404']);
        });
    }

    ngOnDestroy() {
        this.route_sub.unsubscribe();
        this.collData_sub.unsubscribe();
    }

    exploreCollFiles() {
        this.collectionService.exploreCollection(this.id).subscribe(data => {
            console.log("exploring collection...");
        });
    }


    constructor(
        private route: ActivatedRoute,
        private router: Router,
        private collectionService: CollectionService
    ) {}
}
