import {
  Controller,
  Get,
  Post,
  Param,
  Body,
  Delete,
  Put,
  Query,
} from '@nestjs/common';
import { CoinsService } from './coins.service';
import { Coin } from './coins.entity';
import { CoinData } from './entities/coin-data.entity';

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
    @Query('limit') limit: number = 10,
    @Query('offset') offset: number = 0,
  ): Promise<CoinData[]> {
    return this.coinsService.findAllByCoinName(coin_name, limit, offset);
  }

  @Get('exchange/:exchange')
  async getDataByExchange(
    @Param('exchange') exchange: 'BINANCE' | 'COINEX',
    @Query('limit') limit: number = 10,
    @Query('offset') offset: number = 0,
  ): Promise<CoinData[]> {
    return this.coinsService.findAllByExchange(exchange, limit, offset);
  }

  @Get('data/:coin_name/exchange/:exchange')
  async getDataByCoinNameAndExchange(
    @Param('coin_name') coin_name: string,
    @Param('exchange') exchange: 'BINANCE' | 'COINEX',
    @Query('limit') limit: number = 10,
    @Query('offset') offset: number = 0,
  ): Promise<CoinData[]> {
    return this.coinsService.findAllByCoinNameAndExchange(
      coin_name,
      exchange,
      limit,
      offset,
    );
  }

  @Get('data/:coin_name/last')
  async getMostRecentPriceByCoinName(@Param('coin_name') coin_name: string) {
    return this.coinsService.findMostRecentPriceByCoinName(coin_name);
  }
}
