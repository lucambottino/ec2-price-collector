import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { CoinsController } from './coins.controller';
import { CoinsService } from './coins.service';
import { Coin } from './coins.entity';
import { CoinData } from './coin-data.entity';

@Module({
  imports: [TypeOrmModule.forFeature([Coin, CoinData])],
  controllers: [CoinsController],
  providers: [CoinsService],
})
export class CoinsModule {}
