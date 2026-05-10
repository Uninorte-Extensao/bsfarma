import { Component, computed, signal } from '@angular/core';
import { Button } from 'primeng/button';
import { AutoComplete, AutoCompleteCompleteEvent } from "primeng/autocomplete";
import { PACIENTE } from '../../shared/mocks/pacientes.mock';
import { IPatient } from '../../shared/models/IPatient';
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
  public listPatient = signal<IPatient[]>(PACIENTE);
  public filteredPatient = signal<IPatient[]>([]);
  protected form: FormGroup;
  public patientSelected = signal<IPatient | null>(null);
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
        nomeGenerico: medicamento?.nomeGenerico ?? '',
        concentracao: medicamento?.concentracao ?? '',
        viaAdministracao: medicamento?.viaAdministracao ?? '',
      };

    });

  });

  constructor() {
    const fb = new FormBuilder()

    this.form = fb.group({
      paciente_id: [null, [Validators.required]],
    })

    this.onChangeValue()
  }


  filterPatient(event: AutoCompleteCompleteEvent) {
    let filtered: IPatient[] = [];
    let query = event.query;

    for (let i = 0; i < (this.listPatient() as IPatient[]).length; i++) {
      let patient = (this.listPatient() as IPatient[])[i];
      if (patient.id_interno.toLowerCase().indexOf(query.toLowerCase()) == 0) {
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

    let patient = this.listPatient().find(item => item.id === patientId)
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
}
