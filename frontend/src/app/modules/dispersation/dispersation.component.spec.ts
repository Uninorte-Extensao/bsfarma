import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DispersationComponent } from './dispersation.component';

describe('DispersationComponent', () => {
  let component: DispersationComponent;
  let fixture: ComponentFixture<DispersationComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DispersationComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DispersationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
