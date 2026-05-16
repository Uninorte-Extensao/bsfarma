import { HttpClient, HttpParams } from "@angular/common/http";
import { inject, Injectable } from "@angular/core";
import { ICreateMovimentacao, IMovimentacao, IUpdateMovimentacao } from "../models/IMovement";
import { lastValueFrom } from "rxjs";
import { environment } from "../../../environments/environment";

@Injectable({
    providedIn: 'root',
})

export class MovementService {
    private http = inject(HttpClient)

    createMovimentacao(movimentacao: ICreateMovimentacao) {
        return lastValueFrom(this.http.post<IMovimentacao>(`${environment.apiUrl}/movimentacoes`, movimentacao))
    }

    getMovimentacao(loteId?: string) {
        let params = new HttpParams();

        if (loteId) {
            params = params.set('lote_id', loteId)
        }
        return lastValueFrom(this.http.get<IMovimentacao[]>(`${environment.apiUrl}/movimentacoes`, { params }))
    }

    getMovimentacaoById(movimentacaoId: string) {
        return lastValueFrom(this.http.get<IMovimentacao>(`${environment.apiUrl}/movimentacoes/${movimentacaoId}`))
    }

    updateMovimentacao(movimentacaoId: string, movimentacao: IUpdateMovimentacao) {
        return lastValueFrom(this.http.patch<IMovimentacao>(`${environment.apiUrl}/movimentacoes/${movimentacaoId}`, movimentacao))
    }
}