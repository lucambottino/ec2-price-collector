import {
    Entity,
    Column,
    PrimaryGeneratedColumn,
    ManyToOne,
    JoinColumn,
    PrimaryColumn,
  } from 'typeorm';
  import { Coin } from './coins.entity';
  import { ExchangeEnum } from './coin_data.entity';
  
  @Entity('orders')
  export class Order {
    @PrimaryGeneratedColumn()
    id: number;
  
    @ManyToOne(() => Coin)
    @JoinColumn({ name: 'coin_id' })
    coin: Coin;
  
    @PrimaryColumn({ type: 'enum', enum: ExchangeEnum })
    exchange: ExchangeEnum;
  
    @PrimaryColumn()
    id: number;
  
    @Column({ type: 'varchar', length: 10 })
    symbol: string;
  
    @Column({ type: 'varchar', length: 5 })
    side: 'LONG' | 'SHORT';
  
    @Column({ type: 'decimal', precision: 10, scale: 4, default: 0.0 })
    mean: number;
  
    @Column({ type: 'decimal', precision: 10, scale: 4 })
    entry: number;
  
    @Column({ type: 'decimal', precision: 10, scale: 4 })
    exit: number;
  
    @Column({ type: 'decimal', precision: 10, scale: 4 })
    quantity: number;
  
    @Column({ type: 'decimal', precision: 10, scale: 4, default: 0.0 })
    executed_quantity_entry: number;
  
    @Column({ type: 'decimal', precision: 10, scale: 4, default: 0.0 })
    executed_quantity_exit: number;
  
    @Column({ type: 'timestamptz', default: () => 'CURRENT_TIMESTAMP' })
    created_at: Date;
  }
  