import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DashboardAlertComponent } from './dashboard-alert.component';

describe('DashboardAlertComponent', () => {
  let component: DashboardAlertComponent;
  let fixture: ComponentFixture<DashboardAlertComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DashboardAlertComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DashboardAlertComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
