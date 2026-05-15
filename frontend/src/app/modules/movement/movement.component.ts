import { Component, signal } from '@angular/core';
import { CardViewComponent } from "../../shared/components/card-view/card-view.component";
import { TableModule } from "primeng/table";
import { IconField } from "primeng/iconfield";
import { InputIcon } from "primeng/inputicon";
import { Select } from "primeng/select";
import { Button } from "primeng/button";
import { FormsModule } from '@angular/forms';
import { DatePipe } from '@angular/common';
import { InputText } from 'primeng/inputtext';

@Component({
  selector: 'app-movement',
  imports: [CardViewComponent, TableModule, IconField, InputIcon, Select, Button, FormsModule, DatePipe, InputText],
  templateUrl: './movement.component.html',
  styleUrl: './movement.component.scss',
})
export class MovementComponent {
  protected cardItems = signal<any[]>([
    {
      title: 'TOTAL ENTRADAS',
      value: '1.284 un.',
      subtitle: '+12% vs mês anterior',
      icon: 'pi pi-arrow-up-right',
      variant: 'success'
    },

    {
      title: 'TOTAL SAÍDAS',
      value: '842 un.',
      subtitle: '-4% vs mês anterior',
      icon: 'pi pi-arrow-down-right',
      variant: 'danger'
    },

    {
      title: 'MEDICAMENTOS',
      value: '326 itens',
      subtitle: '+8 novos cadastrados',
      icon: 'pi pi-box',
      variant: 'primary'
    },

    {
      title: 'ESTOQUE BAIXO',
      value: '18 alertas',
      subtitle: 'Necessitam reposição',
      icon: 'pi pi-exclamation-triangle',
      variant: 'warning'
    }
  ]);
  protected listMovements = signal([
    {
      id: '1',
      lote_id: 'LT-001',
      usuario_id: 'Maria Silva',
      tipo: 'entrada',
      quantidade: 120,
      justificativa: 'Reposição mensal do estoque',
      ocorrido_em: new Date('2026-05-10T08:30:00')
    },

    {
      id: '2',
      lote_id: 'LT-002',
      usuario_id: 'João Santos',
      tipo: 'saida',
      quantidade: 35,
      justificativa: 'Dispensação para atendimento',
      ocorrido_em: new Date('2026-05-11T14:20:00')
    },

    {
      id: '3',
      lote_id: 'LT-003',
      usuario_id: 'Ana Costa',
      tipo: 'entrada',
      quantidade: 200,
      justificativa: 'Novo lote recebido',
      ocorrido_em: new Date('2026-05-12T09:15:00')
    },

    {
      id: '4',
      lote_id: 'LT-001',
      usuario_id: 'Carlos Lima',
      tipo: 'saida',
      quantidade: 18,
      justificativa: 'Uso interno hospitalar',
      ocorrido_em: new Date('2026-05-12T16:40:00')
    },

    {
      id: '5',
      lote_id: 'LT-004',
      usuario_id: 'Fernanda Alves',
      tipo: 'saida',
      quantidade: 60,
      justificativa: 'Transferência entre unidades',
      ocorrido_em: new Date('2026-05-13T10:00:00')
    }
  ])

  protected lotes = signal([
    {
      id: 'LT-001',
      numero_lote: 'Lote 001',
      fabricante: 'EMS'
    },

    {
      id: 'LT-002',
      numero_lote: 'Lote 002',
      fabricante: 'Neo Química'
    },

    {
      id: 'LT-003',
      numero_lote: 'Lote 003',
      fabricante: 'Medley'
    },

    {
      id: 'LT-004',
      numero_lote: 'Lote 004',
      fabricante: 'Eurofarma'
    }
  ])

  protected loteId: string | null = null

  goToCreate() {

  }

  goToEdit(item: any) {

  }

  onChangeLote(loteId: string | null) {
    this.loteId = loteId
  }
}
