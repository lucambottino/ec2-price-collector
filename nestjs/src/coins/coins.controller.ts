import {
  Controller,
  Get,
  Post,
  Param,
  Body,
  Delete,
  Put,
} from '@nestjs/common';
import { CoinsService } from './coins.service';
import { Coin } from './coins.entity';
import { CoinData } from './coin-data.entity';

@Controller('coins')
export class CoinsController {
  constructor(private readonly coinsService: CoinsService) {}

  @Get()
  findAll(): Promise<Coin[]> {
    return this.coinsService.findAll();
  }

  @Get(':id')
  findOne(@Param('id') id: number): Promise<Coin> {
    return this.coinsService.findOne(id);
  }

  @Get(':id/data')
  findCoinData(@Param('id') id: number): Promise<CoinData[]> {
    return this.coinsService.findCoinData(id);
  }

  @Get('exchange/:exchange')
  findAllByExchange(
    @Param('exchange') exchange: 'BINANCE' | 'COINEX',
  ): Promise<CoinData[]> {
    return this.coinsService.findAllByExchange(exchange);
  }
}
