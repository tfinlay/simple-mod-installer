import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-how-to-play',
  template: `
      <h2>How to play</h2>
      <p>You can find this collection in your Minecraft Launcher. Click it to play!</p>
      <p>If the collection's not already selected, click the arrow next to the <i>PLAY</i> button, and scroll to find it.</p>
      <p>Have fun!</p>
  `
})

export class HowToPlayComponent implements OnInit {

  ngOnInit() {
  }
}
