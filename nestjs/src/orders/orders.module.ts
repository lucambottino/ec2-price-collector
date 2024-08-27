import { Module } from '@nestjs/common';
import { OrdersService } from './orders.service';
import { OrdersController } from './orders.controller';
import { TypeOrmModule } from '@nestjs/typeorm';
import { Order } from './entities/order.entity';
import { Coin } from 'src/coins/coins.entity';

@Module({
  imports: [
    TypeOrmModule.forFeature([Order]),
    TypeOrmModule.forFeature([Coin]),
  ],
  controllers: [OrdersController],
  providers: [OrdersService],
})
export class OrdersModule {}
