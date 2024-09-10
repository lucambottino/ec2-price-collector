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

  @Column('float')
  min_amount_binance: number;

  @Column('float')
  min_amount_coinex: number;

  @Column()
  trading: boolean;

  @Column()
  collecting: boolean;
}
