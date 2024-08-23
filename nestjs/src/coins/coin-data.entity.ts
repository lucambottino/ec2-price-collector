import {
  Entity,
  Column,
  PrimaryGeneratedColumn,
  ManyToOne,
  JoinColumn,
} from 'typeorm';
import { Coin } from './coins.entity';

export enum ExchangeEnum {
  BINANCE = 'BINANCE',
  COINEX = 'COINEX',
}

@Entity('coin_data_table')
export class CoinData {
  @PrimaryGeneratedColumn()
  data_id: number;

  @ManyToOne(() => Coin)
  @JoinColumn({ name: 'coin_id' })
  coin: Coin;

  @Column({ type: 'timestamptz' })
  timestamp: Date;

  @Column({ type: 'real', nullable: true })
  best_bid: number;

  @Column({ type: 'real', nullable: true })
  best_ask: number;

  @Column({ type: 'real', nullable: true })
  best_bid_qty: number;

  @Column({ type: 'real', nullable: true })
  best_ask_qty: number;

  @Column({ type: 'real', nullable: true })
  mark_price: number;

  @Column({ type: 'real', nullable: true })
  last_price: number;

  @Column({ type: 'timestamptz', default: () => 'CURRENT_TIMESTAMP' })
  updated_at: Date;

  @Column({ type: 'enum', enum: ExchangeEnum })
  exchange: ExchangeEnum;
}
