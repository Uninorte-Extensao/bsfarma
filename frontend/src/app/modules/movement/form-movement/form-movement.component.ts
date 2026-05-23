import { Component, inject, model, signal, OnInit, computed } from '@angular/core';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { AutoComplete, AutoCompleteCompleteEvent, AutoCompleteModule } from "primeng/autocomplete";
import { Button } from "primeng/button";
import { InputNumber } from "primeng/inputnumber";
import { Select } from "primeng/select";
import { LoadingService } from '../../../shared/services/loading.service';
import { LoteService } from '../../../shared/services/batch.service';
import { ToastService } from '../../../shared/services/toast.service';
import { AuthService } from '../../../shared/services/auth.service';
import { MedicineService } from '../../../shared/services/medicine.service';
import { MovementService } from '../../../shared/services/movement.service';
import { IBatch } from '../../../shared/models/IBatch';
import { ICreateMovimentacao, IMovimentacao, ITypeMovimentacao, IUpdateMovimentacao } from '../../../shared/models/IMovement';
import { IUser } from '../../../shared/models/IUser';
import { IMedicine } from '../../../shared/models/IMedicine';
import { Textarea} from 'primeng/textarea'
import { AlertService } from '../../../shared/services/alert.service';
@Component({
  selector: 'app-form-movement',
  imports: [
    AutoCompleteModule,
    Button,
    InputNumber,
    Select,
    FormsModule,
    ReactiveFormsModule,
    Textarea
  ],
  templateUrl: './form-movement.component.html',
  styleUrl: './form-movement.component.scss',
})
export class FormMovementComponent implements OnInit {
  protected form: FormGroup
  public listLotes = signal<IBatch[]>([])
  public filteredLote = signal<(IBatch & { medicamento?: IMedicine })[]>([]);
  public listMedicine = signal<IMedicine[]>([])

  public lotesComMedicamento = computed(() => {
    return this.listLotes().map(lote => ({
      ...lote,
      medicamento: this.listMedicine().find(
        med => med.id === lote.medicamento_id
      )
    }));
  });

  private router = inject(Router)
  private route = inject(ActivatedRoute)
  private loading = inject(LoadingService)
  private loteService = inject(LoteService)
  private toast = inject(ToastService)
  private auth = inject(AuthService)
  private service = inject(MovementService)
  private medicamentoService = inject(MedicineService)
  private alertService = inject(AlertService)

  protected isEdit = signal<boolean>(false)
  private movimentacaoId = signal<string | null>(null)
  private user = signal<IUser | null>(null)

  public listTipoMovimentacao = signal([
    {
      label: 'Entrada',
      value: ITypeMovimentacao.ENTRADA
    },
    {
      label: 'Saída',
      value: ITypeMovimentacao.SAIDA
    },
    {
      label: 'Perda',
      value: ITypeMovimentacao.PERDA
    },
    {
      label: 'Ajuste',
      value: ITypeMovimentacao.AJUSTE
    }
  ]);

  constructor() {
    const fb = new FormBuilder
    this.form = fb.group({
      lote_id: [null, [Validators.required]],
      tipo: [null, [Validators.required]],
      quantidade: [null, [Validators.required]],
      justificativa: [null, [Validators.required]]
    })

    this.movimentacaoId.set(this.route.snapshot.paramMap.get('id'))

    if (this.movimentacaoId()) {
      this.isEdit.set(true)
      this.getMovimentacaoById(this.movimentacaoId()!)
    }


    this.user.set(this.auth.getUser())
  }

  async ngOnInit() {
    this.loading.show()
    Promise.all([
      await this.getAllMedicamentos(),
      await this.getLotes()
    ]).catch(() => {
      this.toast.showToastError('Erro ao buscar dados.')
    }).finally(() => {
      this.loading.hide()
    })
  }

  filterLote(event: AutoCompleteCompleteEvent) {
    const query = event.query.toLowerCase();

    const filtered = this.lotesComMedicamento().filter(item =>
      item.numero_lote.toLowerCase().includes(query) ||
      item.medicamento?.nome_generico.toLowerCase().includes(query)
    );

    this.filteredLote.set(filtered);

    console.log('filtered', this.filteredLote())
  }

  async getLotes() {
    this.loading.show()

    await this.loteService.getLotes()
      .then((res: IBatch[]) => {
        this.listLotes.set(res)
      })
      .finally(() => {
        this.loading.hide()
      })
  }

  private setValues(movimentacao: IMovimentacao) {
    this.form.patchValue({
      justificativa: movimentacao.justificativa
    });
  }

  submit() {
    const formValue = this.form.value;


    if (this.isEdit()) {
      const payload: IUpdateMovimentacao = {
        justificativa: formValue.justificativa
      }
      this.update(payload);
    } else {
      const payload: ICreateMovimentacao = {
        lote_id: formValue.lote_id.id,
        usuario_id: this.user()!.id,
        tipo: formValue.tipo,
        quantidade: formValue.quantidade,
        justificativa: formValue.justificativa
      };
      this.create(payload);
    }
  }

  private create(lote: ICreateMovimentacao) {
    this.loading.show()

    this.service.createMovimentacao(lote)
      .then(async () => {

        await this.alertService.verificarAlertas();

        this.alertService.atualizarQuantidadeAlertas();

        this.toast.showToastSuccess('Lote criado com sucesso.')
        this.router.navigate(['/movement'])
      })
      .catch(() => {
        this.toast.showToastError('Erro ao criar lote.')
      })
      .finally(() => {
        this.loading.hide()
      })
  }

  private update(lote: IUpdateMovimentacao) {
    this.loading.show()

    this.service.updateMovimentacao(this.movimentacaoId()!, lote)
      .then(() => {
        this.toast.showToastSuccess('Lote atualizado com sucesso.')
        this.router.navigate(['/movement'])
      })
      .catch(() => {
        this.toast.showToastError('Erro ao atualizar lote.')
      })
      .finally(() => {
        this.loading.hide()
      })
  }

  close() {
    this.router.navigate(['/movement'])
  }

  async getAllMedicamentos() {
    this.loading.show()
    await this.medicamentoService.getMedicamentos()
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

  getMovimentacaoById(movimentacaoId: string) {
    this.loading.show()
    this.service.getMovimentacaoById(movimentacaoId)
    .then((res:IMovimentacao) => {
      this.setValues(res)
    })
    .catch(() => {
      this.toast.showToastError('Erro ao buscar movimentação.')
    })
    .finally(() => {
      this.loading.hide()
    })
  }

}
