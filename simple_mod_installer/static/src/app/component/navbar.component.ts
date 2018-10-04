import {Component, Inject, OnInit} from '@angular/core';
import {MD_DIALOG_DATA, MdDialog, MdDialogRef, MdSnackBar} from "@angular/material";
import {DEFAULT_SNACKBAR_CONFIG} from "../util";

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html'
})

export class NavbarComponent implements OnInit {
  routeLinks: routeLink[];
  activeLinkIndex = 0;

  constructor(
      private dialog: MdDialog,
      private snackbar: MdSnackBar
  ) {}

  ngOnInit() {
    this.routeLinks = [
            {label: 'Collections', link: '/'},
            {label: 'Mods', link: '/mods'}
    ];
  }

  openFeedback() {
      /*this.dialog.open(FeedbackComponent).afterClosed().subscribe(() => {
          this.snackbar.open("Thank you for your feedback!", "", DEFAULT_SNACKBAR_CONFIG);
      });*/
  }
}

interface routeLink {
  label: string;
  link: string;
}


@Component({
  selector: 'app-feedback-form',
  template: `
<iframe src="http://minecraft-mod-installer.weebly.com/v3-feedback.html#form-395534660595331538" style="width:100%;height:calc(100vh - 80px);"></iframe>
`
})

export class FeedbackComponent implements OnInit {
/*
    constructor(
        @Inject(MD_DIALOG_DATA) public data: any, // To allow data to be passed in to it
        private dialogRef: MdDialogRef<FeedbackComponent>
    ) {}
*/
    ngOnInit() {
    }
}
