import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TableMedicinesComponent } from './table-medicines.component';
import { testProviders } from '../../../../testing/test-providers';

describe('TableMedicinesComponent', () => {
  let component: TableMedicinesComponent;
  let fixture: ComponentFixture<TableMedicinesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TableMedicinesComponent],
      providers: testProviders
    })
    .compileComponents();

    fixture = TestBed.createComponent(TableMedicinesComponent);
    component = fixture.componentInstance;
    fixture.componentRef.setInput('listMedicine', []);
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
