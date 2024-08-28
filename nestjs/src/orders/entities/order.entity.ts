import {
  Entity,
  Column,
  PrimaryGeneratedColumn,
  ManyToOne,
  JoinColumn,
  PrimaryColumn,
} from 'typeorm';
import { Coin } from 'src/coins/coins.entity';
import { ExchangeEnum } from 'src/coins/entities/coin-data.entity';

@Entity('orders')
export class Order {
  @PrimaryGeneratedColumn()
  id: number;

  @ManyToOne(() => Coin)
  @JoinColumn({ name: 'coin_id' })
  coin: Coin; // Define the relation to the Coin entity

  @PrimaryColumn({ type: 'enum', enum: ExchangeEnum })
  exchange: ExchangeEnum;

  @Column({ type: 'varchar', length: 10 })
  symbol: string;

  @Column({ type: 'varchar', length: 5 })
  side: 'LONG' | 'SHORT';

  @Column({ type: 'decimal', precision: 10, scale: 4, default: 0.0 })
  mean_premium: number;

  @Column({ type: 'decimal', precision: 10, scale: 4 })
  entry_premium: number;

  @Column({ type: 'decimal', precision: 10, scale: 4 })
  exit_premium: number;

  @Column({ type: 'decimal', precision: 10, scale: 4 })
  quantity: number;

  @Column({ type: 'decimal', precision: 10, scale: 4, default: 0.0 })
  executed_quantity_entry: number;

  @Column({ type: 'decimal', precision: 10, scale: 4, default: 0.0 })
  executed_quantity_exit: number;

  @Column({ type: 'timestamptz', default: () => 'CURRENT_TIMESTAMP' })
  created_at: Date;
}
