import { Component, effect, inject, model, output, OutputEmitterRef, signal, OnInit } from '@angular/core';
import { Button } from 'primeng/button';
import { DatePicker } from 'primeng/datepicker';
import { InputText } from 'primeng/inputtext';
import { AutoComplete, AutoCompleteCompleteEvent } from 'primeng/autocomplete'
import { InputNumber } from 'primeng/inputnumber';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { IBatch, ICreateLote, IUpdateLote } from '../../../shared/models/IBatch';
import { MEDICAMENTOS } from '../../../shared/mocks/medicamentos.mock';
import { IMedicine } from '../../../shared/models/IMedicine';
import { ActivatedRoute, Router } from '@angular/router';
import { LoadingService } from '../../../shared/services/loading.service';
import { LoteService } from '../../../shared/services/batch.service';
import { ToastService } from '../../../shared/services/toast.service';
import { AuthService } from '../../../shared/services/auth.service';
import { IUser } from '../../../shared/models/IUser';
import { MedicineService } from '../../../shared/services/medicine.service';

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
export class FormBatchComponent implements OnInit {
  protected form: FormGroup;
  public lote = model<IBatch | null>(null);
  public listMedicine = signal<IMedicine[]>([]);
  public filteredMedicine = signal<IMedicine[]>([]);

  private router = inject(Router)
  private route = inject(ActivatedRoute)
  private loading = inject(LoadingService)
  private service = inject(LoteService)
  private toast = inject(ToastService)
  private auth = inject(AuthService)
  private medicamentoService = inject(MedicineService)

  private isEdit = signal<boolean>(false)
  private loteId = signal<string | null>(null)
  private user = signal<IUser | null>(null)

  constructor() {
    const fb = new FormBuilder
    this.form = fb.group({
      medicamento_id: [null, [Validators.required]],
      numero_lote: [null, [Validators.required]],
      fabricante: [null, [Validators.required]],
      validade: [new Date(), [Validators.required]],
      quantidade_inicial: [null, [Validators.required]]
    })

    this.loteId.set(this.route.snapshot.paramMap.get('id'))

    if (this.loteId()) {
      this.isEdit.set(true)
      this.getLoteById(this.loteId()!)
    }


    this.user.set(this.auth.getUser())
  }

  ngOnInit() {
    this.getAllMedicamentos()
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

  private getLoteById(loteId: string) {
    this.loading.show()

    this.service.getLoteById(loteId)
      .then((res: IBatch) => {
        this.setValues(res)
      })
      .finally(() => {
        this.loading.hide()
      })
  }

  private setValues(lote: IBatch) {
    this.form.patchValue({
      medicamento_id: lote.medicamento_id,
      numero_lote: lote.numero_lote,
      fabricante: lote.fabricante,
      validade: new Date(lote.validade),
      quantidade_inicial: lote.quantidade_inicial
    });
  }

  submit() {
    const formValue = this.form.value;

    const payload = {
      ...formValue,
      registrado_por: this.user()?.id,
      validade: formValue.validade.toISOString().split('T')[0]
    }

    if (this.isEdit()) {
      this.update(payload);
    } else {
      this.create(payload);
    }
  }

  private create(lote: ICreateLote) {
    this.loading.show()

    this.service.createLote(lote)
      .then(() => {
        this.toast.showToastSuccess('Lote criado com sucesso.')
        this.router.navigate(['/batch'])
      })
      .catch(() => {
        this.toast.showToastError('Erro ao criar lote.')
      })
      .finally(() => {
        this.loading.hide()
      })
  }

  private update(lote: IUpdateLote) {
    this.loading.show()

    this.service.updateLote(this.loteId()!, lote)
      .then(() => {
        this.toast.showToastSuccess('Lote atualizado com sucesso.')
        this.router.navigate(['/batch'])
      })
      .catch(() => {
        this.toast.showToastError('Erro ao atualizar lote.')
      })
      .finally(() => {
        this.loading.hide()
      })
  }

  close() {
    this.router.navigate(['/batch'])
  }

  getAllMedicamentos() {
    this.loading.show()
    this.medicamentoService.getMedicamentos()
      .then((res: IMedicine[]) => {
        this.listMedicine.set(res)
      })
      .catch(() => {
        this.toast.showToastError('Erro ao buscar medicamentos.')
      })
      .finally(() => {
        this.loading.hide()
      })
  }

}
