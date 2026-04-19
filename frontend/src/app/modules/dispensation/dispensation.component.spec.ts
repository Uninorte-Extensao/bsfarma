import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DispensationComponent } from './dispensation.component';

describe('DispensationComponent', () => {
  let component: DispensationComponent;
  let fixture: ComponentFixture<DispensationComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DispensationComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DispensationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
