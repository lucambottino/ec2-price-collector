import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { ConfigModule } from '@nestjs/config';
import { Coin } from './coins/coins.entity';
import { CoinData } from './coins/entities/coin-data.entity';
import { CoinsModule } from './coins/coins.module';
import { LatestCoinDataModule } from './coins/latest-coins.module';
import { LatestCoinData } from './coins/entities/latest-coins.entity';
import { OrdersModule } from './orders/orders.module';
import { Order } from './orders/entities/order.entity';
@Module({
  imports: [
    ConfigModule.forRoot(),
    TypeOrmModule.forRoot({
      type: 'postgres',
      host: process.env.DB_HOST,
      port: Number(process.env.DB_PORT),
      username: process.env.DB_USERNAME,
      password: process.env.DB_PASSWORD,
      database: process.env.DB_DATABASE,
      synchronize: false, // Set to false if you want to manage your schema manually
      logging: false,
      entities: [Coin, CoinData, LatestCoinData, Order],
    }),
    TypeOrmModule.forFeature([Coin, CoinData, LatestCoinData, Order]),
    CoinsModule,
    LatestCoinDataModule,
    OrdersModule,
  ],
  controllers: [],
  providers: [],
})
export class AppModule {}
