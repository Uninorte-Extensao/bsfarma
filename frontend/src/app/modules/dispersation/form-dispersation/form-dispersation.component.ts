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
import { inject } from '@angular/core';
import { ToastService } from '../../../shared/services/toast.service';
import { LoadingService } from '../../../shared/services/loading.service';
import { DispersationService } from '../../../shared/services/dispersation.service';
import { PatientService } from '../../../shared/services/patient.service';
import { MedicineService } from '../../../shared/services/medicine.service';
import { LoteService } from '../../../shared/services/batch.service';
import { RouterLink } from "@angular/router";


interface ILoteMedicamento extends IBatch {
  nome_generico: string
  concentracao: string
  via_administracao: string
}
@Component({
  selector: 'app-form-dispersation',
  imports: [Button, InputNumber, Select, AutoComplete, ReactiveFormsModule, FormsModule, RouterLink],
  templateUrl: './form-dispersation.component.html',
  styleUrl: './form-dispersation.component.scss',
})
export class FormDispersationComponent {
  public listPatient = signal<IPaciente[]>([]);
  public filteredPatient = signal<IPaciente[]>([]);
  protected form: FormGroup;
  public patientSelected = signal<IPaciente | null>(null);
  public listLote = signal<IBatch[]>([]);
  public listMedicine = signal<IMedicine[]>([]);

  protected batchSelected = signal<any[]>([]);
  value = 0

  public loteComputed = computed<ILoteMedicamento[]>(() => {

    return this.listLote().map((lote) => {

      const medicamento = this.listMedicine().find(
        (item) => item.id === lote.medicamento_id
      );

      return {
        ...lote,
        nome_generico: medicamento?.nome_generico ?? '',
        concentracao: medicamento?.concentracao ?? '',
        via_administracao: medicamento?.via_administracao ?? '',
      };

    });

  });

  public availableLotes = computed(() => {

    const selectedIds = this.batchSelected().map(item => item.id);

    return this.loteComputed().filter(
      lote =>
        !selectedIds.includes(lote.id) &&
        lote.quantidade_atual > 0
    );

  });

  private toast = inject(ToastService);

  private loading = inject(LoadingService);

  private dispersationService = inject(DispersationService);
  private pacienteService = inject(PatientService)
  private medicamentoService = inject(MedicineService)
  private loteService = inject(LoteService)
  protected selectedLote!: ILoteMedicamento

  constructor() {
    const fb = new FormBuilder()

    this.form = fb.group({
      paciente_id: [null, [Validators.required]],
    })

    this.onChangeValue()
  }

  ngOnInit() {
    this.getAllPacientes()
    this.getAllLotes()
    this.getAllMedicamentos()
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

    this.form.get('paciente_id')
      ?.valueChanges
      .subscribe((patientId) => {

        const patient = this.listPatient().find(
          item => item.codigo === patientId
        );

        this.patientSelected.set(
          patient ?? null
        );
      });
  }

  addLote(item: ILoteMedicamento) {

    if (!item || item.quantidade_atual <= 0) {
      return;
    }

    this.batchSelected.update((items) => [
      ...items,
      {
        ...item,
        quantidade: 1
      }
    ]);
  }

  clear() {

    this.form.reset();

    this.batchSelected.set([]);

    this.patientSelected.set(null);
  }

  submit() {

    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    if (!this.batchSelected().length) {
      return;
    }

    const pacienteId = this.form.get('paciente_id')?.value;

    const payloads = this.batchSelected().map((item) => {

      const payload = {
        codigo: pacienteId,
        lote_id: item.id,
        quantidade: item.quantidade
      };

      return this.dispersationService
        .createDispensacao(payload);
    });

    this.loading.show();

    Promise.all(payloads)
      .then(() => {

        this.toast.showToastSuccess(
          'Atendimento registrado com sucesso.'
        );

        this.clear();
      })
      .catch(() => {

        this.toast.showToastError(
          'Erro ao registrar atendimento.'
        );

      })
      .finally(() => {
        this.loading.hide();
      });
  }

  removeLote(index: number) {
    this.batchSelected.update((items) =>
      items.filter((_, i) => i !== index)
    );
  }

  getAllPacientes() {
    this.loading.show()
    this.pacienteService.getPacientes(true)
      .then((res: IPaciente[]) => {
        this.listPatient.set(res)
      })
      .finally(() => {
        this.loading.hide()
      })
  }

  getAllLotes() {
    this.loading.show()
    this.loteService.getLotes()
      .then((res: IBatch[]) => {
        this.listLote.set(res)
      })
      .finally(() => {
        this.loading.hide()
      })
  }

  getAllMedicamentos() {
    this.loading.show()
    this.medicamentoService.getMedicamentos()
      .then((res: IMedicine[]) => {
        this.listMedicine.set(res)
      })
      .finally(() => {
        this.loading.hide()
      })
  }
}
