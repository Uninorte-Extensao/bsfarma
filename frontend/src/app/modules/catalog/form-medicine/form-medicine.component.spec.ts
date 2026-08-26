import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FormMedicineComponent } from './form-medicine.component';

describe('FormMedicineComponent', () => {
  let component: FormMedicineComponent;
  let fixture: ComponentFixture<FormMedicineComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FormMedicineComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(FormMedicineComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
