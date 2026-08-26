import { HttpClient, HttpParams } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { lastValueFrom } from 'rxjs';
import { IEstoqueMedicamento, IGestaoDashboard, IItemCritico, IMovimentacaoRelatorio, IPaginacao, IRelatorioDispensacao } from '../models/IReport';
import { environment } from '../../../environments/environment';
import { IMovimentacao } from '../models/IMovement';

@Injectable({
  providedIn: 'root',
})
export class ReportService {
  private http = inject(HttpClient)

  getDashboard() {
    return lastValueFrom(this.http.get<IGestaoDashboard>(`${environment.apiUrl}/relatorios/dashboard`))
  }

  getConsumoMensal(dataInicio?: string, dataFim?: string, medicamentoId?: string) {
    let params = new HttpParams();

    if (dataInicio) {
      params = params.set('data_inicio', dataInicio);
    }

    if (dataFim) {
      params = params.set('data_fim', dataFim);
    }

    if (medicamentoId) {
      params = params.set('medicamento_id', medicamentoId);
    }

    return lastValueFrom(
      this.http.get<IRelatorioDispensacao[]>(
        `${environment.apiUrl}/relatorios/consumo-mensal`,
        { params }
      )
    );
  }

  getEstoqueAtual(indicacao?: string) {
    let params = new HttpParams();

    if (indicacao) {
      params = params.set('indicacao', indicacao);
    }

    return lastValueFrom(
      this.http.get<IEstoqueMedicamento[]>(
        `${environment.apiUrl}/relatorios/estoque-atual`,
        { params }
      )
    );
  }

  getItensCriticos() {
    return lastValueFrom(
      this.http.get<IItemCritico[]>(
        `${environment.apiUrl}/relatorios/itens-criticos`
      )
    )
  }

  getMovimentacoes(
    page: number = 1,
    pageSize: number = 50,
    dataInicio?: string,
    dataFim?: string,
    tipo?: string,
    medicamentoId?: string
  ) {
    let params = new HttpParams()
      .set('page', page)
      .set('page_size', pageSize);

    if (dataInicio) {
      params = params.set('data_inicio', dataInicio);
    }

    if (dataFim) {
      params = params.set('data_fim', dataFim);
    }

    if (tipo) {
      params = params.set('tipo', tipo);
    }

    if (medicamentoId) {
      params = params.set('medicamento_id', medicamentoId);
    }

    return lastValueFrom(
      this.http.get<IPaginacao<IMovimentacaoRelatorio>>(
        `${environment.apiUrl}/relatorios/movimentacoes`,
        { params }
      )
    );
  }

  exportarConsumoCsv(dataInicio: string, dataFim: string) {
    const params = new HttpParams()
      .set('data_inicio', dataInicio)
      .set('data_fim', dataFim);

    // const url = `${environment.apiUrl}/relatorios/exportar/consumo.csv?${params.toString()}`;

    // window.open(url, '_blank');


    // HTTPCLIENT

    return lastValueFrom(
      this.http.get(
        `${environment.apiUrl}/relatorios/exportar/consumo.csv`,
        {
          params,
          responseType: 'blob'
        }
      )
    );

  }

  exportarConsumoXlsx(dataInicio: string, dataFim: string) {
    const params = new HttpParams()
      .set('data_inicio', dataInicio)
      .set('data_fim', dataFim);

    // const url = `${environment.apiUrl}/relatorios/exportar/consumo.xlsx?${params.toString()}`;

    // window.open(url, '_blank');


    return lastValueFrom(
      this.http.get(
        `${environment.apiUrl}/relatorios/exportar/consumo.xlsx`,
        {
          params,
          responseType: 'blob'
        }
      )
    );

  }

  exportarEstoqueXlsx() {
    // const url = `${environment.apiUrl}/relatorios/exportar/estoque.xlsx`;
    // window.open(url, '_blank');

    return lastValueFrom(
      this.http.get(
        `${environment.apiUrl}/relatorios/exportar/estoque.xlsx`,
        {
          responseType: 'blob'
        }
      )
    );

  }

  exportarMovimentacoesCsv(
    dataInicio: string,
    dataFim: string,
    tipo?: string
  ) {
    let params = new HttpParams()
      .set('data_inicio', dataInicio)
      .set('data_fim', dataFim);

    if (tipo) {
      params = params.set('tipo', tipo);
    }

    // const url = `${environment.apiUrl}/relatorios/exportar/movimentacoes.csv?${params.toString()}`;

    // window.open(url, '_blank');


    return lastValueFrom(
      this.http.get(
        `${environment.apiUrl}/relatorios/exportar/movimentacoes.csv`,
        {
          params,
          responseType: 'blob'
        }
      )
    );
  
  }
}
