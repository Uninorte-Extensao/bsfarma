import { DatePipe } from '@angular/common';
import { Component, computed, effect, input, signal } from '@angular/core';
import { Button } from "primeng/button";
import { IAlert } from '../../../shared/models/IAlert';
import { MEDICAMENTOS } from '../../../shared/mocks/medicamentos.mock';
import { LOTE } from '../../../shared/mocks/lote.mock';

@Component({
  selector: 'app-table-alerts',
  imports: [Button, DatePipe],
  templateUrl: './table-alerts.component.html',
  styleUrl: './table-alerts.component.scss',
})
export class TableAlertsComponent {
  item = input.required<IAlert>()
  listMedicine = signal(MEDICAMENTOS);
  listLote = signal(LOTE);

  alert = computed(() => {
    const date = new Date()
    const medicine = this.listMedicine().find(medicine => medicine.id === this.item().medicamento_id)
    const lote = this.listLote().find(lote => lote.id === this.item().lote_id)
  
    const days = lote?.validade
    ? Math.ceil(
        (lote.validade.getTime() - date.getTime()) /
        (1000 * 60 * 60 * 24)
      )
    : null

    const validade = lote?.validade
    const estoque_atual = lote?.quantidade_atual
    const estoque_minimo = medicine?.estoque_minimo

    return {
      ...this.item(),
      nome_medicamento: medicine?.nome_generico,
      nome_lote: lote?.numero_lote,
      dias_vencimento: days,
      validade: validade,
      estoque_atual: estoque_atual,
      estoque_minimo: estoque_minimo
    }
  })

  constructor() {
    effect(() => {
      console.log('alert', this.item())
      console.log('computed', this.alert())
    })
  }


  getTag(tag: string): string {
    if (tag === 'Vencimento') {
      return 'tag-red'
    } else if (tag === 'Aberto') {
      return 'tag-green'
    } else if (tag === 'Estoque mínimo') {
      return 'tag-yellow'
    }
    return 'tag-red'
  }

  // getBox(boxIcon: string): string {
  //   if (boxIcon === 'pi pi-calendar') {
  //     return 'box-red'
  //   } else if (boxIcon === 'pi pi-home') {
  //     return 'box-yellow'
  //   }
  //   return 'box-red'
  // }
}
