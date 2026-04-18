import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TableMedicinesComponent } from './table-medicines.component';

describe('TableMedicinesComponent', () => {
  let component: TableMedicinesComponent;
  let fixture: ComponentFixture<TableMedicinesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TableMedicinesComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(TableMedicinesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
