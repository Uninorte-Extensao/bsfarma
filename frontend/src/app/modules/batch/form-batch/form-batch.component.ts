import { Component, effect, model, output, OutputEmitterRef, signal } from '@angular/core';
import { Button } from 'primeng/button';
import { DatePicker } from 'primeng/datepicker';
import { InputText } from 'primeng/inputtext';
import { AutoComplete, AutoCompleteCompleteEvent } from 'primeng/autocomplete'
import { InputNumber } from 'primeng/inputnumber';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { ICreateLote, IBatch, IUpdateLote } from '../../../shared/models/IBatch';
import { MEDICAMENTOS } from '../../../shared/mocks/medicamentos.mock';
import { IMedicine } from '../../../shared/models/IMedicine';

type ITypeDialog = 'create' | 'update'

@Component({
  selector: 'app-form-batch',
  imports: [
    DatePicker,
    Button,
    InputText,
    AutoComplete,
    InputNumber,
    ReactiveFormsModule
  ],
  templateUrl: './form-batch.component.html',
  styleUrl: './form-batch.component.scss',
})
export class FormBatchComponent {
  protected form: FormGroup;
  public lote = model<IBatch | null>(null);
  public onChangeCreate = output<ICreateLote>();
  public onChangeUpdate = output<IUpdateLote>()
  public typeDialog = model<ITypeDialog>('create');
  public listMedicine = signal<IMedicine[]>(MEDICAMENTOS);
  public filteredMedicine = signal<IMedicine[]>([]);
  public isVisible = model<boolean>(false)
  constructor() {
    const fb = new FormBuilder
    this.form = fb.group({
      medicamento_id: [null, [Validators.required]],
      lote: [null, [Validators.required]],
      fabricante: [null, [Validators.required]],
      validade: [new Date(), [Validators.required]],
      quantidade: [null, [Validators.required]]
    })

    effect(() => {
      this.typeDialog()
    })
  }

  submit() {
    if (this.typeDialog() === 'create') {
      this.onChangeCreate.emit(this.form.value)
    } else {
      this.onChangeUpdate.emit(this.form.value)
    }
  }

  filterMedicine(event: AutoCompleteCompleteEvent) {
    let filtered: any[] = [];
    let query = event.query;

    for (let i = 0; i < (this.listMedicine() as IMedicine[]).length; i++) {
      let country = (this.listMedicine() as IMedicine[])[i];
      if (country.nome_generico.toLowerCase().indexOf(query.toLowerCase()) == 0) {
        filtered.push(country);
      }
    }

    this.filteredMedicine.set(filtered);
  }

  close() {
    this.isVisible.set(false)
  }
}
