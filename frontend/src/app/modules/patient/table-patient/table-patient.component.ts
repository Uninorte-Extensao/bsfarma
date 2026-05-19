import { Component, inject, model, output } from '@angular/core';
import { IS_MOBILE } from '../../../shared/services/is-mobile.service';
import { IPaciente } from '../../../shared/models/IPatient';
import { TableModule } from "primeng/table";
import { IconField } from "primeng/iconfield";
import { InputIcon } from "primeng/inputicon";
import { Button } from "primeng/button";
import { DatePipe } from '@angular/common';
import { InputText } from 'primeng/inputtext';

@Component({
  selector: 'app-table-patient',
  imports: [TableModule, IconField, InputIcon, Button, DatePipe, InputText],
  templateUrl: './table-patient.component.html',
  styleUrl: './table-patient.component.scss',
})
export class TablePatientComponent {
  protected isMobile = inject(IS_MOBILE)
  public isVisible = model<boolean>(false)
  public codigo = model<string>('')

  listPacientes = model<IPaciente[]>([]);

  onItemDelete = output<IPaciente>();

  deleteItem(item: IPaciente) {
    this.onItemDelete.emit(item);
  }

  goToEdit(item: IPaciente) {
    this.codigo.set(item.codigo)
  }
}
