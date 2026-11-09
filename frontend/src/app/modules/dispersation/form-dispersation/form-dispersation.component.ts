import { Component, computed, signal } from '@angular/core';
import { IPaciente } from '../../../shared/models/IPatient';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { IBatch, IBatchDetalhado } from '../../../shared/models/IBatch';
import { Button } from "primeng/button";
import { InputNumber } from "primeng/inputnumber";
import { Select } from "primeng/select";
import { inject, OnInit } from '@angular/core';
import { ToastService } from '../../../shared/services/toast.service';
import { LoadingService } from '../../../shared/services/loading.service';
import { DispersationService } from '../../../shared/services/dispersation.service';
import { PatientService } from '../../../shared/services/patient.service';
import { LoteService } from '../../../shared/services/batch.service';
import { RouterLink } from "@angular/router";
import { Router } from '@angular/router';
import { DatePipe } from '@angular/common';
import { Tag } from 'primeng/tag';


interface ILoteMedicamento extends IBatch {
  nome_generico: string
  concentracao: string
  via_administracao: string
  // Primeiro lote (por validade) de um medicamento que tem mais de um lote disponível
  venceAntes?: boolean
}

interface ILoteSelecionado extends ILoteMedicamento {
  quantidade: number
}
@Component({
  selector: 'app-form-dispersation',
  imports: [Button, InputNumber, Select, ReactiveFormsModule, FormsModule, RouterLink, DatePipe, Tag],
  templateUrl: './form-dispersation.component.html',
  styleUrl: './form-dispersation.component.scss',
})
export class FormDispersationComponent implements OnInit {
  public listPatient = signal<IPaciente[]>([]);
  protected form: FormGroup;
  public patientSelected = signal<IPaciente | null>(null);
  public listLote = signal<IBatchDetalhado[]>([]);

  protected batchSelected = signal<ILoteSelecionado[]>([]);

  public loteComputed = computed<ILoteMedicamento[]>(() => {

    return this.listLote().map((lote) => {

      return {
        ...lote,
        nome_generico: lote.medicamento.nome_generico,
        concentracao: lote.medicamento.concentracao,
        via_administracao: lote.medicamento.via_administracao,
      };

    });

  });

  public availableLotes = computed(() => {

    const selectedIds = this.batchSelected().map(item => item.id);
    const hoje = new Date().toLocaleDateString('sv-SE'); // YYYY-MM-DD no fuso local

    // A API envia a validade como "YYYY-MM-DD"; lote vencido não pode ser dispensado.
    const disponiveis = this.loteComputed().filter(
      lote =>
        !selectedIds.includes(lote.id) &&
        lote.quantidade_atual > 0 &&
        String(lote.validade) >= hoje
    );

    // O backend devolve os lotes ordenados por validade, então o primeiro
    // de cada medicamento é o que vence antes.
    const vistos = new Set<string>();

    return disponiveis.map(lote => {
      const temOutros = disponiveis.some(
        outro => outro.medicamento_id === lote.medicamento_id && outro.id !== lote.id
      );
      const venceAntes = temOutros && !vistos.has(lote.medicamento_id);
      vistos.add(lote.medicamento_id);

      return { ...lote, venceAntes };
    });

  });

  private toast = inject(ToastService);

  private loading = inject(LoadingService);

  private dispersationService = inject(DispersationService);
  private pacienteService = inject(PatientService)
  private loteService = inject(LoteService)
  protected selectedLote: ILoteMedicamento | null = null
  private router = inject(Router)

  constructor() {
    const fb = new FormBuilder()

    this.form = fb.group({
      codigo: [null, [Validators.required]],
    })

    this.onChangeValue()
  }

  ngOnInit() {
    this.getAllPacientes()
    this.getAllLotes()
  }


  onChangeValue() {

    this.form.get('codigo')
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

  get totalUnidades(): number {
    return this.batchSelected().reduce((total, item) => total + (item.quantidade ?? 0), 0);
  }

  get podeConfirmar(): boolean {
    return !!this.patientSelected() && this.batchSelected().length > 0;
  }

  trocarPaciente() {
    this.form.get('codigo')?.setValue(null);
  }

  onSelectLote(lote: ILoteMedicamento | null) {
    if (!lote) return;

    this.addLote(lote);
    this.selectedLote = null;
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

    const pacienteId = this.form.get('codigo')?.value;

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
        this.router.navigate(['/dispersation'])
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
    this.loteService.getLotes(undefined, true)
      .then((res: IBatchDetalhado[]) => {
        this.listLote.set(res)
      })
      .finally(() => {
        this.loading.hide()
      })
  }
}
