import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MovementComponent } from './movement.component';
import { testProviders } from '../../../testing/test-providers';

describe('MovementComponent', () => {
  let component: MovementComponent;
  let fixture: ComponentFixture<MovementComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MovementComponent],
      providers: testProviders
    })
    .compileComponents();

    fixture = TestBed.createComponent(MovementComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
