import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DashboardMovementComponent } from './dashboard-movement.component';

describe('DashboardMovementComponent', () => {
  let component: DashboardMovementComponent;
  let fixture: ComponentFixture<DashboardMovementComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DashboardMovementComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DashboardMovementComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
