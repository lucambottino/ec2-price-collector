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
  async getAllCoins(): Promise<Coin[]> {
    return this.coinsService.findAll();
  }

  @Get('data/:coin_name')
  async getDataByCoinName(
    @Param('coin_name') coin_name: string,
  ): Promise<CoinData[]> {
    return this.coinsService.findAllByCoinName(coin_name);
  }

  @Get('exchange/:exchange')
  async getDataByExchange(
    @Param('exchange') exchange: 'BINANCE' | 'COINEX',
  ): Promise<CoinData[]> {
    return this.coinsService.findAllByExchange(exchange);
  }

  @Get('data/:coin_name/exchange/:exchange')
  async getDataByCoinNameAndExchange(
    @Param('coin_name') coin_name: string,
    @Param('exchange') exchange: 'BINANCE' | 'COINEX',
  ): Promise<CoinData[]> {
    return this.coinsService.findAllByCoinNameAndExchange(coin_name, exchange);
  }

  @Get('data/:coin_name/last')
  async getMostRecentPriceByCoinName(@Param('coin_name') coin_name: string) {
    return this.coinsService.findMostRecentPriceByCoinName(coin_name);
  }
}
