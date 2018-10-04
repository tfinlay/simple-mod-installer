import { Component, OnInit, Input, EventEmitter, Output } from '@angular/core';

@Component({
  selector: 'app-listcard',
  templateUrl: 'listCard.component.html'
})

export class ListCardComponent implements OnInit {
  @Input() id: number;
  @Input() header: string;
  @Input() subheader: string;
  @Input() actionText: string;
  @Input() warning: string;
  @Input() contextMenu: object;

  @Output() actionClick = new EventEmitter();
  @Output() click = new EventEmitter<number>();

  ngOnInit() {}

  componentClickEvent() {
    this.click.emit();
  }

  actionButtonClickEvent() {
    this.actionClick.emit(this.id);
  }
}

