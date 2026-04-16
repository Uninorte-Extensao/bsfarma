import { Component, InputSignal, input } from '@angular/core';

@Component({
  selector: 'app-card-view',
  imports: [],
  templateUrl: './card-view.component.html',
  styleUrl: './card-view.component.scss',
})
export class CardViewComponent {
  public cardColor: InputSignal<string> = input('green');
  public icon: InputSignal<string> = input.required();
  public value: InputSignal<string | number> = input.required();
  public label: InputSignal<string> = input.required();
  public labelRoute: InputSignal<string> = input.required();
  public route: InputSignal<string> = input.required();
}
