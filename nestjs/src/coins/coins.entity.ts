import { Entity, Column, PrimaryGeneratedColumn } from 'typeorm';

@Entity('coins_table')
export class Coin {
  @PrimaryGeneratedColumn()
  coin_id: number;

  @Column({ unique: true })
  coin_name: string;

  @Column()
  precision_binance: number;

  @Column()
  precision_coinex: number;

  @Column()
  min_amount_binance: number;

  @Column()
  min_amount_coinex: number;
}
