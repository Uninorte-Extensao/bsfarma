import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DashboardMonthlyConsumptionComponent } from './dashboard-monthly-consumption.component';
import { testProviders } from '../../../../testing/test-providers';

describe('DashboardMonthlyConsumptionComponent', () => {
  let component: DashboardMonthlyConsumptionComponent;
  let fixture: ComponentFixture<DashboardMonthlyConsumptionComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DashboardMonthlyConsumptionComponent],
      providers: testProviders
    })
    .compileComponents();

    fixture = TestBed.createComponent(DashboardMonthlyConsumptionComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
