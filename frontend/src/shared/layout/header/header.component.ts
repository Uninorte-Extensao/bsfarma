import { Component, OnDestroy, OnInit, signal, WritableSignal } from '@angular/core';
import { InputIcon } from 'primeng/inputicon';
import { IconField } from 'primeng/iconfield';
import { InputText } from 'primeng/inputtext';
import { DatePipe } from '@angular/common';
@Component({
  selector: 'app-header',
  imports: [
    InputIcon,
    IconField,
    InputText,
    DatePipe
  ],
  templateUrl: './header.component.html',
  styleUrl: './header.component.scss',
})
export class HeaderComponent implements OnInit, OnDestroy {
  protected date: WritableSignal<Date> = signal(new Date());
  private intervalId: any;

  ngOnInit() {
    this.intervalId = setInterval(() => {
      this.date.set(new Date())
    }, 1000)
  }

  ngOnDestroy() {
    clearInterval(this.intervalId)
  }

  showGreeting(currentDate: Date): string {
    let greeting = ''
    const hour = currentDate.getHours()

    if (hour > 5 && hour < 12) {
      greeting = 'Bom Dia !'
    } else if(hour > 12 && hour < 18) {
      greeting = 'Boa Tarde !'
    } else {
      greeting = 'Boa Noite !'
    }

    return greeting
  }
}
