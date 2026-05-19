import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FormDispersationComponent } from './form-dispersation.component';

describe('FormDispersationComponent', () => {
  let component: FormDispersationComponent;
  let fixture: ComponentFixture<FormDispersationComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FormDispersationComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(FormDispersationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
