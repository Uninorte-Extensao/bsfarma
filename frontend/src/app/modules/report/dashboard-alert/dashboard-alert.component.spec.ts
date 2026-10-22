import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DashboardAlertComponent } from './dashboard-alert.component';
import { testProviders } from '../../../../testing/test-providers';

describe('DashboardAlertComponent', () => {
  let component: DashboardAlertComponent;
  let fixture: ComponentFixture<DashboardAlertComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DashboardAlertComponent],
      providers: testProviders
    })
    .compileComponents();

    fixture = TestBed.createComponent(DashboardAlertComponent);
    component = fixture.componentInstance;
    fixture.componentRef.setInput('alerts', []);
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
