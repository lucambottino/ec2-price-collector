import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { LatestCoinDataService } from './latest-coins.service';
import { LatestCoinDataController } from './latest-coins.controller';
import { LatestCoinData } from './entities/latest-coins.entity';
import { CoinsModule } from './coins.module';

@Module({
  imports: [TypeOrmModule.forFeature([LatestCoinData]), CoinsModule],
  providers: [LatestCoinDataService],
  controllers: [LatestCoinDataController],
})
export class LatestCoinDataModule {}
