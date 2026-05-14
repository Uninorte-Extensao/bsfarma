import { Component, effect, inject, model, OnInit, output, signal } from '@angular/core';
import { InputText } from 'primeng/inputtext';
import { SelectModule } from "primeng/select";
import { InputNumber } from "primeng/inputnumber";
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { Button } from "primeng/button";
import { FORMA_FARMACEUTICA, UNIDADE_CONCENTRACAO, VIA_ADMINISTRACAO } from '../../../shared/mocks/medicamentos.mock';
import { MedicineService } from '../../../shared/services/medicine.service';
import { ToastService } from '../../../shared/services/toast.service';
import { LoadingService } from '../../../shared/services/loading.service';
import { ICreateMedicine, IMedicine } from '../../../shared/models/IMedicine';
import { ToggleSwitch } from 'primeng/toggleswitch';
import { ActivatedRoute, Router } from '@angular/router';

type ITypeDialog = 'create' | 'update'
@Component({
  selector: 'app-form-medicine',
  imports: [
    InputText,
    SelectModule,
    InputNumber,
    FormsModule,
    Button,
    ReactiveFormsModule,
    ToggleSwitch
  ],
  templateUrl: './form-medicine.component.html',
  styleUrl: './form-medicine.component.scss',
})
export class FormMedicineComponent implements OnInit {
  checked: boolean = false;
  listConcentracao = signal(UNIDADE_CONCENTRACAO)
  listViaAdm = signal(VIA_ADMINISTRACAO)
  listFormaFarm = signal(FORMA_FARMACEUTICA)


  private toast = inject(ToastService)
  private route = inject(ActivatedRoute)
  private router = inject(Router)
  private service = inject(MedicineService)
  private loading = inject(LoadingService)


  public form: FormGroup;
  public medicineId = signal<string | null>(null)
  public isEdit = signal<boolean>(false)

  constructor() {
    const fb = new FormBuilder()

    this.form = fb.group({
      nome_generico: [null, [Validators.required]],
      nome_comercial: [null, [Validators.required]],
      forma_farmaceutica: [null, [Validators.required]],
      via_administracao: [null, [Validators.required]],
      estoque_minimo: [null, [Validators.required]],
      valor: [null, [Validators.required]],
      unidade: [null, [Validators.required]]
    })
  }

  ngOnInit() {
    this.medicineId.set(this.route.snapshot.paramMap.get('id'))

    if (this.medicineId()) {
      this.isEdit.set(true)
      this.getMedicamento(this.medicineId()!)
    }
  }


  protected submit() {
    if (this.form.invalid) {
      this.toast.showToastWarn('Por favor, preencha todos os campos.')
      return
    }

    const valor = this.form.value.valor
    const unidade = this.form.value.unidade

    const payload: ICreateMedicine = {
      ...this.form.value,
      concentracao: `${valor} ${unidade}`,
      ativo: this.checked
    }

    if (this.isEdit()) {
      this.update(payload)
    } else {
      this.create(payload)
    }
  }

  private setValues(medicine: IMedicine) {
    const [valor, unidade] = medicine.concentracao.split(' ')

    this.form.patchValue({
      nome_generico: medicine.nome_generico,
      nome_comercial: medicine.nome_comercial,
      forma_farmaceutica: medicine.forma_farmaceutica,
      via_administracao: medicine.via_administracao,
      estoque_minimo: medicine.estoque_minimo,
      valor: Number(valor),
      unidade: unidade
    })

    this.checked = medicine.ativo
  }

  private create(medicine: ICreateMedicine) {
    this.loading.show()

    this.service.createMedicamentos(medicine)
      .then(() => {
        this.toast.showToastSuccess('Medicamento criado com sucesso.')
        this.router.navigate(['/catalog'])
      })
      .catch(() => {
        this.toast.showToastError('Erro ao criar medicamento.')
      })
      .finally(() => {
        this.loading.hide()
      })
  }

  private update(medicine: ICreateMedicine) {
    this.loading.show()

    this.service.updateMedicamento(this.medicineId()!, medicine)
      .then(() => {
        this.toast.showToastSuccess('Medicamento atualizado com sucesso.')
        this.router.navigate(['/catalog'])
      })
      .catch(() => {
        this.toast.showToastError('Erro ao atualizar medicamento.')
      })
      .finally(() => {
        this.loading.hide()
      })
  }

  getMedicamento(medicamentoId: string) {
    this.loading.show()

    this.service.getMedicamentoById(medicamentoId)
      .then((res: IMedicine) => {
        this.setValues(res)
      })
      .finally(() => {
        this.loading.hide()
      })
  }

  protected close() {
    this.router.navigate(['/catalog'])
  }
}
