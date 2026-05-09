import { Component, model, signal } from '@angular/core';
import { TableModule } from 'primeng/table';
import { RouterLink } from "@angular/router";
import { IconField } from "primeng/iconfield";
import { InputIcon } from "primeng/inputicon";
import { InputText } from 'primeng/inputtext';
import { DatePipe } from '@angular/common';
import { LOTE } from '../../shared/mocks/lote.mock';
import { Dialog } from 'primeng/dialog';
import { Button } from 'primeng/button';
import { ICreateLote, IUpdateLote } from '../../shared/models/IBatch';
import { FormsModule } from '@angular/forms';
import { FormBatchComponent } from "./form-batch/form-batch.component";

type ITypeDialog = 'create' | 'update'
@Component({
  selector: 'app-batch',
  imports: [
    TableModule,
    RouterLink,
    IconField,
    InputIcon,
    InputText,
    DatePipe,
    Dialog,
    Button,
    FormsModule,
    FormBatchComponent
],
  templateUrl: './batch.component.html',
  styleUrl: './batch.component.scss',
})
export class BatchComponent {
    listLote = signal<any[]>(LOTE);
    isVisible = model<boolean>(false);
    typeDialog = model<ITypeDialog>('create');

    protected showModal(type: ITypeDialog, lote?: any) {
      this.typeDialog.set(type)
      this.isVisible.set(true)
    }

    protected closeModal() {
      this.isVisible.set(false);
    }

    protected submit(lote: ICreateLote) {

    }


    protected update(lote: IUpdateLote){
      
    }
}
