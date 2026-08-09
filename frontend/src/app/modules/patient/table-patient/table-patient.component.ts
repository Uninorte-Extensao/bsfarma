import { Component, computed, inject, model, output, signal } from '@angular/core';
import { IS_MOBILE } from '../../../shared/services/is-mobile.service';
import { IPaciente } from '../../../shared/models/IPatient';

import { IconField } from 'primeng/iconfield';
import { InputIcon } from 'primeng/inputicon';
import { Button } from 'primeng/button';
import { Tag } from 'primeng/tag';
import { Select } from 'primeng/select';
import { FormsModule } from '@angular/forms';
import { Paginator, PaginatorState } from 'primeng/paginator';
import { DatePipe } from '@angular/common';
import { InputText } from 'primeng/inputtext';
import { Tooltip} from 'primeng/tooltip'
import { ConfirmPopup } from 'primeng/confirmpopup';
import { ConfirmationService } from 'primeng/api';

@Component({
  selector: 'app-table-patient',
  imports: [
    IconField,
    InputIcon,
    Button,
    Tag,
    Select,
    FormsModule,
    Paginator,
    DatePipe,
    InputText,
    Tooltip,
    ConfirmPopup
  ],
  templateUrl: './table-patient.component.html',
  styleUrl: './table-patient.component.scss',
})
export class TablePatientComponent {

  protected isMobile = inject(IS_MOBILE);
  private confirmationService = inject(ConfirmationService);

  public isVisible = model<boolean>(false);

  public codigo = model<string>('');

  listPacientes = model<IPaciente[]>([]);

  onItemDelete = output<IPaciente>();

  onItemEdit = output<IPaciente>();

  protected searchTerm = signal('');
  protected first = signal(0);
  protected rows = signal(12);

  public onFilter = output<boolean | undefined>()

  protected statusFilter = signal<boolean | undefined>(undefined);

  protected filterOptions = [
    { label: 'Todos', value: undefined },
    { label: 'Ativos', value: true },
    { label: 'Inativos', value: false }
  ];

  protected onStatusChange(value: boolean | undefined) {
    this.statusFilter.set(value);
    this.first.set(0);
    this.onFilter.emit(value);
  }

  protected filteredList = computed(() => {
    const term = this.searchTerm().trim().toLowerCase();
    const list = this.listPacientes();

    if (!term) return list;

    return list.filter(item =>
      item.codigo.toLowerCase().includes(term) ||
      item.condicao_clinica.toLowerCase().includes(term)
    );
  });

  protected pagedList = computed(() =>
    this.filteredList().slice(this.first(), this.first() + this.rows())
  );

  protected onSearch(value: string) {
    this.searchTerm.set(value);
    this.first.set(0);
  }

  protected onPageChange(event: PaginatorState) {
    this.first.set(event.first ?? 0);
    this.rows.set(event.rows ?? 8);
  }

  deleteItem(item: IPaciente, event: Event) {
    this.confirmationService.confirm({
      target: event.currentTarget as EventTarget,
      message: `Deseja realmente inativar o paciente ${item.codigo}?`,
      icon: 'pi pi-exclamation-triangle',
      acceptLabel: 'Sim',
      rejectLabel: 'Não',
      acceptButtonProps: { severity: 'danger' },
      rejectButtonProps: { severity: 'secondary', outlined: true },
      accept: () => {
        this.onItemDelete.emit(item);
      }
    });
  }

  goToEdit(item: IPaciente) {

    this.codigo.set(item.codigo);

    this.isVisible.set(true);

    this.onItemEdit.emit(item);
  }
}
