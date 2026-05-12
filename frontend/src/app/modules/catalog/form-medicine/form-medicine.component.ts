import { Component, model, output, signal } from '@angular/core';
import { InputText } from 'primeng/inputtext';
import { SelectModule } from "primeng/select";
import { InputNumber } from "primeng/inputnumber";
import { ToggleSwitch } from 'primeng/toggleswitch';
import { FormsModule } from '@angular/forms';
import { Button } from "primeng/button";
import { RouterLink } from "@angular/router";
import { FORMA_FARMACEUTICA, UNIDADE_CONCENTRACAO, VIA_ADMINISTRACAO } from '../../../shared/mocks/medicamentos.mock';

type ITypeDialog = 'create' | 'update'
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
  public isVisible = model(false)
  public typeDialog = model<ITypeDialog>('create')
  public onChangeCreate = output()
  public onChangeUpdate = output()
  public medicine = model<any | null>(null)
  listConcentracao = signal(UNIDADE_CONCENTRACAO)
  listViaAdm = signal(VIA_ADMINISTRACAO)
  listFormaFarm = signal(FORMA_FARMACEUTICA)
}
