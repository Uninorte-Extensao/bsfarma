import { HttpClient, HttpParams } from "@angular/common/http";
import { inject, Injectable } from "@angular/core";
import { IBatch, ICreateLote, IUpdateLote } from "../models/IBatch";
import { lastValueFrom } from "rxjs";
import { environment } from "../../../environments/environment";

@Injectable({
    providedIn: 'root',
})
export class LoteService {
    private http = inject(HttpClient)

    public createLote(lote: ICreateLote) {
        return lastValueFrom(this.http.post<IBatch>(`${environment.apiUrl}/lotes`, lote))
    }

    public getLotes(medicamentoId?: string, comSaldo?: boolean) {
        let params = new HttpParams();

        if (medicamentoId) {
            params = params.set('medicamento_id', medicamentoId)
        }

        if (comSaldo !== undefined) {
            params = params.set('apenas_com_saldo', comSaldo)
        }
        return lastValueFrom(this.http.get<IBatch[]>(`${environment.apiUrl}/lotes`, { params }))
    }

    public getLoteById(loteId: string) {
        return lastValueFrom(this.http.get<IBatch>(`${environment.apiUrl}/lotes/${loteId}`))
    }

    public updateLote(loteId: string, lote: IUpdateLote) {
        return lastValueFrom(this.http.patch<IBatch>(`${environment.apiUrl}/lotes/${loteId}`, lote))
    }

}