import { Component, computed, inject, input, InputSignal, output, signal } from '@angular/core';
import { IMedicine } from '../../../shared/models/IMedicine';
import { IconField } from "primeng/iconfield";
import { InputIcon } from "primeng/inputicon";
import { InputText } from 'primeng/inputtext';
import { Router } from '@angular/router';
import { Button } from "primeng/button";
import { Tag } from 'primeng/tag';
import { Select } from 'primeng/select';
import { FormsModule } from '@angular/forms';
import { Paginator, PaginatorState } from 'primeng/paginator';
import { IS_MOBILE } from '../../../shared/services/is-mobile.service';
import { AuthService } from '../../../shared/services/auth.service';

@Component({
  selector: 'app-table-medicines',
  imports: [
    IconField,
    InputIcon,
    InputText,
    Button,
    Tag,
    Select,
    FormsModule,
    Paginator
  ],
  templateUrl: './table-medicines.component.html',
  styleUrl: './table-medicines.component.scss',
})
export class TableMedicinesComponent {
  listMedicine: InputSignal<IMedicine[]> = input.required();
  private router = inject(Router)
  public onItemDelete = output<IMedicine>()
  public isMobile = inject(IS_MOBILE)
  protected authService = inject(AuthService)

  protected searchTerm = signal('');
  protected first = signal(0);
  protected rows = signal(12);

  protected statusFilter = signal<boolean | undefined>(undefined);

  protected filterOptions = [
    { label: 'Todos', value: undefined },
    { label: 'Ativos', value: true },
    { label: 'Inativos', value: false }
  ];

  protected onStatusChange(value: boolean | undefined) {
    this.statusFilter.set(value);
    this.first.set(0);
  }

  protected filteredList = computed(() => {
    const term = this.searchTerm().trim().toLowerCase();
    const status = this.statusFilter();

    let list = this.listMedicine();

    if (status !== undefined) {
      list = list.filter(item => item.ativo === status);
    }

    if (!term) return list;

    return list.filter(item =>
      item.nome_generico.toLowerCase().includes(term) ||
      item.nome_comercial.toLowerCase().includes(term) ||
      item.concentracao.toLowerCase().includes(term)
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
    this.rows.set(event.rows ?? 12);
  }

  protected goToEdit(medicine: IMedicine) {
    this.router.navigate(['/catalog/edit', medicine.id])
  }

  protected goToCreate() {
    this.router.navigate(['/catalog/create'])
  }

  public deleteItem(medicamento: IMedicine) {
    this.onItemDelete.emit(medicamento)
  }
}
