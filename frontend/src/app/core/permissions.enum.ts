export enum Module {
    CATALOG = 'catalog',
    BATCH = 'batch',
    DISPENSATINS = 'dispersation',
    ALERTS = 'alerts',
    MANAGEMENT = 'management',
    REPORT = 'report'
}

export enum Action {
    VIEW = 'view',
    CREATE = 'create',
    UPDATE = 'update',
    DELETE = 'delete'
}

export type Permission = `${Module}.${Action}`