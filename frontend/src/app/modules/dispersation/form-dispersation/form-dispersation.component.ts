import { Component, computed, signal } from '@angular/core';
import { AutoCompleteCompleteEvent, AutoComplete } from 'primeng/autocomplete';
import { IPaciente } from '../../../shared/models/IPatient';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { IMedicine } from '../../../shared/models/IMedicine';
import { MEDICAMENTOS } from '../../../shared/mocks/medicamentos.mock';
import { IBatch } from '../../../shared/models/IBatch';
import { LOTE } from '../../../shared/mocks/lote.mock';
import { PACIENTE } from '../../../shared/mocks/pacientes.mock';
import { Button } from "primeng/button";
import { InputNumber } from "primeng/inputnumber";
import { Select } from "primeng/select";

@Component({
  selector: 'app-form-dispersation',
  imports: [Button, InputNumber, Select, AutoComplete, ReactiveFormsModule, FormsModule],
  templateUrl: './form-dispersation.component.html',
  styleUrl: './form-dispersation.component.scss',
})
export class FormDispersationComponent {
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

  clear() { }

  submit() { }

  removeLote(index: number) {
    this.batchSelected.update((items) =>
      items.filter((_, i) => i !== index)
    );
  }
}
