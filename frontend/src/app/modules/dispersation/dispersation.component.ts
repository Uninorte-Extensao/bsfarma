import { Component, computed, signal } from '@angular/core';
import { Button } from 'primeng/button';
import { AutoComplete, AutoCompleteCompleteEvent } from "primeng/autocomplete";
import { PACIENTE } from '../../shared/mocks/pacientes.mock';
import { IPaciente } from '../../shared/models/IPatient';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { Select } from "primeng/select";
import { IBatch } from '../../shared/models/IBatch';
import { LOTE } from '../../shared/mocks/lote.mock';
import { IMedicine } from '../../shared/models/IMedicine';
import { MEDICAMENTOS } from '../../shared/mocks/medicamentos.mock';
import { InputNumber } from 'primeng/inputnumber';
@Component({
  selector: 'app-dispersation',
  imports: [
    Button,
    AutoComplete,
    ReactiveFormsModule,
    Select,
    InputNumber,
    FormsModule
  ],
  templateUrl: './dispersation.component.html',
  styleUrl: './dispersation.component.scss',
})
export class DispersationComponent {
  public listPatient = signal<IPaciente[]>(PACIENTE);
  public filteredPatient = signal<IPaciente[]>([]);
  protected form: FormGroup;
  public patientSelected = signal<IPaciente | null>(null);
  public listLote = signal<IBatch[]>(LOTE);
  public listMedicine = signal<IMedicine[]>(MEDICAMENTOS);

  protected batchSelected = signal<any[]>([]);
  value = 0

  public loteComputed = computed(() => {

    return this.listLote().map((lote) => {

      const medicamento = this.listMedicine().find(
        (item) => item.id === lote.medicamento_id
      );

      return {
        ...lote,
        nomeGenerico: medicamento?.nome_generico ?? '',
        concentracao: medicamento?.concentracao ?? '',
        viaAdministracao: medicamento?.via_administracao ?? '',
      };

    });

  });

  public availableLotes = computed(() => {

    const selectedIds = this.batchSelected().map(item => item.id);

    return this.loteComputed().filter(
      lote => !selectedIds.includes(lote.id)
    );

  });

  constructor() {
    const fb = new FormBuilder()

    this.form = fb.group({
      paciente_id: [null, [Validators.required]],
    })

    this.onChangeValue()
  }


  filterPatient(event: AutoCompleteCompleteEvent) {
    let filtered: IPaciente[] = [];
    let query = event.query;

    for (let i = 0; i < (this.listPatient() as IPaciente[]).length; i++) {
      let patient = (this.listPatient() as IPaciente[])[i];
      if (patient.codigo.toLowerCase().indexOf(query.toLowerCase()) == 0) {
        filtered.push(patient);
      }
    }

    this.filteredPatient.set(filtered);
  }

  onChangeValue() {
    let patientId = ''
    this.form.valueChanges.subscribe(value => {
      patientId = value.paciente_id
    })

    let patient = this.listPatient().find(item => item.codigo === patientId)
    if (patient) {
      this.patientSelected.set(patient)
    }
  }

  addLote(item: any) {
    this.batchSelected.update((items) => [
      ...items,
      {
        ...item,
        quantidade: 0
      }
    ]);
  }

  clear(){}

  submit(){}

  removeLote(index: number) {
  this.batchSelected.update((items) =>
    items.filter((_, i) => i !== index)
  );
}
}
