import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FormMedicineComponent } from './form-medicine.component';
import { testProviders } from '../../../../testing/test-providers';

describe('FormMedicineComponent', () => {
  let component: FormMedicineComponent;
  let fixture: ComponentFixture<FormMedicineComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FormMedicineComponent],
      providers: testProviders
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
