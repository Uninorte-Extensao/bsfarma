import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TableAlertsComponent } from './table-alerts.component';
import { testProviders } from '../../../../testing/test-providers';
import { IAlertaValidade } from '../../../shared/models/IAlert';

const ALERTA: IAlertaValidade = {
  id: '1',
  tipo_alerta: 'Vencimento',
  status_alerta: 'Pendente',
  gerado_em: new Date(),
  resolvido_em: null,
  lote: { id: '1', numero_lote: 'L001', validade: new Date(), quantidade_atual: 10, quantidade_inicial: 100 },
  medicamento: { id: '1', nome_generico: 'Dipirona', concentracao: '500mg', forma_farmaceutica: 'Comprimido', estoque_minimo: 20 },
};

describe('TableAlertsComponent', () => {
  let component: TableAlertsComponent;
  let fixture: ComponentFixture<TableAlertsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TableAlertsComponent],
      providers: testProviders
    })
    .compileComponents();

    fixture = TestBed.createComponent(TableAlertsComponent);
    component = fixture.componentInstance;
    fixture.componentRef.setInput('item', ALERTA);
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
