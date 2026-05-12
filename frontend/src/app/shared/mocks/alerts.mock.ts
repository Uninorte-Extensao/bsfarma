import { IAlert } from "../models/IAlert";
import { LOTE } from "./lote.mock";
import { MEDICAMENTOS } from "./medicamentos.mock";

export const ALERTS = [
    {
        icon: 'pi pi-calendar',
        title: 'Lote vence em 12 dias - Insulina NPH',
        subtitle: 'Lote INS-2024-002 - Validade 23/05/2026',
        label: 'Vencimento',
        status: 'Aberto',
        gerado: new Date()
    },
    {
        icon: 'pi pi-home',
        title: 'Estoque abaixo de mínimo - Amoxicilina',
        subtitle: 'Estoque atual: 38un. - Mínimo: 100 un',
        label: 'Estoque mínimo',
        status: 'Aberto',
        gerado: new Date()
    },
    {
        icon: 'pi pi-calendar',
        title: 'Lote vence em 7 dias - Paracetamol',
        subtitle: 'Lote PAR-2025-014 - Validade 18/05/2026',
        label: 'Vencimento',
        status: 'Aberto',
        gerado: new Date()
    },
    {
        icon: 'pi pi-home',
        title: 'Estoque abaixo de mínimo - Cefalexina',
        subtitle: 'Estoque atual: 22un. - Mínimo: 80 un',
        label: 'Estoque mínimo',
        status: 'Aberto',
        gerado: new Date()
    },
    {
        icon: 'pi pi-calendar',
        title: 'Lote vence em 3 dias - Dipirona',
        subtitle: 'Lote DIP-2025-031 - Validade 14/05/2026',
        label: 'Vencimento',
        status: 'Aberto',
        gerado: new Date()
    },
    {
        icon: 'pi pi-home',
        title: 'Estoque abaixo de mínimo - Omeprazol',
        subtitle: 'Estoque atual: 15un. - Mínimo: 60 un',
        label: 'Estoque mínimo',
        status: 'Aberto',
        gerado: new Date()
    },
    {
        icon: 'pi pi-calendar',
        title: 'Lote vence em 20 dias - Loratadina',
        subtitle: 'Lote LOR-2025-008 - Validade 31/05/2026',
        label: 'Vencimento',
        status: 'Aberto',
        gerado: new Date()
    },
    {
        icon: 'pi pi-home',
        title: 'Estoque abaixo de mínimo - Metformina',
        subtitle: 'Estoque atual: 41un. - Mínimo: 120 un',
        label: 'Estoque mínimo',
        status: 'Aberto',
        gerado: new Date()
    }
];


export const ALERTAS: IAlert[] = LOTE.flatMap((lote) => {
    const medicamento = MEDICAMENTOS.find(
        med => med.id === lote.medicamento_id
    )

    if (!medicamento) return []

    const alertas = []

    const hoje = new Date()

    const diffDias = Math.ceil(
        (lote.validade.getTime() - hoje.getTime()) / (1000 * 60 * 60 * 24)
    )

    if (diffDias <= 90) {
        alertas.push({
            id: crypto.randomUUID(),
            lote_id: lote.id,
            medicamento_id: medicamento.id,
            tipo: 'Vencimento',
            status: 'Aberto',
            gerado_em: new Date(),
            resolvido_em: null
        })
    }

     if(lote.quantidade_atual <= medicamento.estoqueMinimo) {
        alertas.push({
            id: crypto.randomUUID(),
            lote_id: lote.id,
            medicamento_id: medicamento.id,
            tipo: 'Estoque mínimo',
            status: 'Aberto',
            gerado_em: new Date(),
            resolvido_em: null
        })
     }

     return alertas
})