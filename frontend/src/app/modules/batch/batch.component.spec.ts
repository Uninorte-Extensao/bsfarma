import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BatchComponent } from './batch.component';
import { testProviders } from '../../../testing/test-providers';

describe('BatchComponent', () => {
  let component: BatchComponent;
  let fixture: ComponentFixture<BatchComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [BatchComponent],
      providers: testProviders
    })
    .compileComponents();

    fixture = TestBed.createComponent(BatchComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
