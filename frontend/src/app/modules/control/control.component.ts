import { Component } from '@angular/core';
import { CardViewComponent } from "../../../shared/components/card-view/card-view.component";
import {CommonModule} from '@angular/common'

@Component({
  selector: 'app-control',
  imports: [
    CardViewComponent,
    CommonModule
  ],
  templateUrl: './control.component.html',
  styleUrl: './control.component.scss',
})
export class ControlComponent {
  routes = [
    {
      icon: "health_and_safety",
      value: "Bom",
      label: "Status de inventário",
      labelRoute: "Visão Detalhada",
      route: "/home"
    }
  ]
}
