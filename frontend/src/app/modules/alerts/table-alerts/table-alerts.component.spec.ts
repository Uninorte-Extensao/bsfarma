import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TableAlertsComponent } from './table-alerts.component';

describe('TableAlertsComponent', () => {
  let component: TableAlertsComponent;
  let fixture: ComponentFixture<TableAlertsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TableAlertsComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(TableAlertsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
