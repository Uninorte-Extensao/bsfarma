import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FormBatchComponent } from './form-batch.component';
import { testProviders } from '../../../../testing/test-providers';

describe('FormBatchComponent', () => {
  let component: FormBatchComponent;
  let fixture: ComponentFixture<FormBatchComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FormBatchComponent],
      providers: testProviders
    })
    .compileComponents();

    fixture = TestBed.createComponent(FormBatchComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
