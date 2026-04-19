import { Component } from '@angular/core';
import { InputText } from 'primeng/inputtext';
import { SelectModule } from "primeng/select";
import { InputNumber } from "primeng/inputnumber";
import { ToggleSwitch } from 'primeng/toggleswitch';
import { FormsModule } from '@angular/forms';
import { Button } from "primeng/button";
import { RouterLink } from "@angular/router";
@Component({
  selector: 'app-form-medicine',
  imports: [
    InputText,
    SelectModule,
    InputNumber,
    ToggleSwitch,
    FormsModule,
    Button,
    RouterLink
],
  templateUrl: './form-medicine.component.html',
  styleUrl: './form-medicine.component.scss',
})
export class FormMedicineComponent {
  checked: boolean = false;
}
