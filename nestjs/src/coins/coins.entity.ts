import { Entity, Column, PrimaryGeneratedColumn } from 'typeorm';

@Entity('coins_table')
export class Coin {
  @PrimaryGeneratedColumn()
  coin_id: number;

  @Column({ unique: true })
  coin_name: string;
}
