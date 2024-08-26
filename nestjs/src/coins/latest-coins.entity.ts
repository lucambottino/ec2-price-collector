import {
  Entity,
  Column,
  PrimaryGeneratedColumn,
  ManyToOne,
  JoinColumn,
} from 'typeorm';
import { Coin } from './coins.entity';

@Entity('latest_coin_data_table')
export class LatestCoinData {
  @PrimaryGeneratedColumn()
  coin_id: number;

  @Column()
  data_id: number;

  @Column()
  timestamp: Date;

  @Column({ type: 'decimal', nullable: true })
  best_bid: number;

  @Column({ type: 'decimal', nullable: true })
  best_ask: number;

  @Column({ type: 'decimal', nullable: true })
  best_bid_qty: number;

  @Column({ type: 'decimal', nullable: true })
  best_ask_qty: number;

  @Column({ type: 'decimal', nullable: true })
  mark_price: number;

  @Column({ type: 'decimal', nullable: true })
  last_price: number;

  @Column()
  updated_at: Date;

  @Column()
  exchange: string;

  @ManyToOne(() => Coin)
  @JoinColumn({ name: 'coin_id' })
  coin: Coin; // Define the relation to the Coin entity
}
