import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { RouterModule, Routes } from "@angular/router";
import {HttpClientModule} from "@angular/common/http";
import {HttpModule} from "@angular/http";
import {FormsModule} from "@angular/forms";

import {BrowserAnimationsModule} from '@angular/platform-browser/animations';

import {
    MdButtonModule,
    MdMenuModule,
    MdCardModule,
    MdToolbarModule,
    MdIconModule,
    MdTabsModule,
    MdTooltipModule,
    MdRippleModule,
    MdDialogModule,
    MdInputModule,
    MD_RIPPLE_GLOBAL_OPTIONS,
    RippleGlobalOptions,
    MdSnackBarModule,
    MdSelectModule,
    MdFormFieldModule,
    MdRadioModule,
    MdSliderModule,
    MdSlideToggleModule, MdProgressSpinnerModule
} from "@angular/material";

import { AppComponent } from './component/app.component';
import {FeedbackComponent, NavbarComponent} from "./component/navbar.component";
import {CollectionListComponent} from "./component/collectionList.component";
import {ListCardComponent} from "./component/listCard.component";
import {CollectionDetailComponent} from "./component/collectionDetail.component";
import {CollectionModListComponent} from "./component/collectionModList.component";
import {AddModSelectorComponent} from "./component/addModSelector.component";

import {CollectionListService} from "./service/collectionList.service";
import {ModSelectorService} from "./service/modSelector.service";
import {ModService} from "./service/mod.service";
import {ModUploadComponent} from "./component/modUpload.component";
import {PageNotFoundComponent} from "./component/PageNotFound.component";
import {ModListComponent} from "./component/modList.component";
import {ErrPopupComponent} from "./component/errPopup.component";
import {CreateCollectionComponent} from "./component/createCollection.component";
import {CollectionService} from "./service/collection.service";
import {MiscService} from "./service/misc.service";
import {LoadingSpinnerComponent} from "./component/common/loadingSpinner.component";
import {ModIssueViewComponent} from "./component/modIssueView.component";
import {HowToPlayComponent} from "./component/howToPlay.component";

const appRoutes: Routes = [
  {
    path: 'collection',
    component: CollectionListComponent
  },
  {
    path: 'collection/:id',
    children: [
      {
        path: '',
        component: CollectionDetailComponent
      }
    ]
  },
    {
        path: 'mod',
        component: ModListComponent
    },
  {path: 'feedback', component: FeedbackComponent},
  {path: 'MODUPLOAD', component: ModUploadComponent},
  {path: '', redirectTo: 'collection', pathMatch: 'full'}, // The root
  {path: '404', component: PageNotFoundComponent},
  {path: '**', component: PageNotFoundComponent}
];

const globalRippleConfig: RippleGlobalOptions = {
  disabled: false,
  baseSpeedFactor: 1
};

@NgModule({
  declarations: [
    AppComponent,
    NavbarComponent,
    CollectionListComponent,
    ListCardComponent,
    CollectionDetailComponent,
    CollectionModListComponent,
    AddModSelectorComponent,
    ModUploadComponent,
    ModListComponent,
    PageNotFoundComponent,
    ErrPopupComponent,
    CreateCollectionComponent,
    ModIssueViewComponent,

    LoadingSpinnerComponent,

    HowToPlayComponent,
    FeedbackComponent
  ],
  imports: [
      BrowserModule,
      BrowserAnimationsModule,
      RouterModule.forRoot(
      appRoutes,
      {enableTracing: false}  // debugging only
      ),
      HttpClientModule,
      HttpModule,
      FormsModule,

      MdButtonModule,
      MdMenuModule,
      MdCardModule,
      MdToolbarModule,
      MdIconModule,
      MdTabsModule,
      MdTooltipModule,
      MdRippleModule,
      MdDialogModule,
      MdSnackBarModule,
      MdInputModule,
      MdSelectModule,
      MdFormFieldModule,
      MdSelectModule,
      MdRadioModule,
      MdSliderModule,
      MdSlideToggleModule,
      MdProgressSpinnerModule
  ],
  entryComponents: [ // Components that are to be generated dynamically
      AddModSelectorComponent,
      ErrPopupComponent,
      CreateCollectionComponent,
      ModIssueViewComponent,
      HowToPlayComponent
  ],
  providers: [
      {provide: MD_RIPPLE_GLOBAL_OPTIONS, useValue: globalRippleConfig},
      ModSelectorService,
      ModService,
      CollectionService,
      MiscService

  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
