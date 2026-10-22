export type ICardVariant = 'primary' | 'success' | 'danger' | 'warning' | 'teal'

export interface ICard {
  title: string;
  value: string;
  subtitle: string;
  icon: string;
  variant: ICardVariant;
}
