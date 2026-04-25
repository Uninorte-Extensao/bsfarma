import { Component, InputSignal, input } from '@angular/core';
import { RouterLink } from "@angular/router";

interface ICardData {
  color: string;
  icon: string,
  value: string | number,
  label: string,
  labelRoute: string,
  route: string
}
@Component({
  selector: 'app-card-view',
  imports: [RouterLink],
  templateUrl: './card-view.component.html',
  styleUrl: './card-view.component.scss',
})
export class CardViewComponent {
  public cardData: InputSignal<ICardData> = input.required()
}
