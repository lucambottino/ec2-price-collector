import {
  Controller,
  Get,
  Post,
  Param,
  Body,
  Delete,
  Put,
  Query,
  HttpException,
  HttpStatus,
  Patch,
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

  //healthcheck
  @Get('healthcheck')
  async healthCheck(): Promise<HttpStatus> {
    try {
      return HttpStatus.OK;
    } catch (error) {
      throw new HttpException(
        'Health check failed',
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }

  @Get('data/:coin_name')
  async getDataByCoinName(
    @Param('coin_name') coin_name: string,
    @Query('limit') limit: number = 10,
    @Query('offset') offset: number = 0,
  ): Promise<CoinData[]> {
    return this.coinsService.findAllByCoinName(coin_name, limit, offset);
  }

  @Post()
  async createCoin(@Body() coin: Coin): Promise<Coin> {
    return this.coinsService.createCoin(coin);
  }

  @Post('reset-trading')
  async resetTrading(): Promise<void> {
    return this.coinsService.resetTradingStatus();
  }

  @Delete(':id')
  async deleteCoin(@Param('id') id: number): Promise<void> {
    return this.coinsService.delete(id);
  }

  @Delete(':name')
  async deleteCoinByName(@Param('name') name: string): Promise<void> {
    return this.coinsService.deleteByName(name);
  }

  @Put(':identifier')
  async updateCoin(
    @Param('identifier') identifier: string,
    @Body() coin: Coin,
  ): Promise<Coin> {
    // Check if the identifier is numeric (ID) or string (name)
    if (!isNaN(Number(identifier))) {
      return this.coinsService.updateCoin(Number(identifier), coin);
    } else {
      return this.coinsService.updateCoinByName(identifier, coin);
    }
  }

  @Patch(':id')
  async updateCoinPartial(
    @Param('id') id: number,
    @Body() coin: Partial<Coin>,
  ): Promise<Coin> {
    return this.coinsService.updatePartial(id, coin);
  }

  @Patch(':name')
  async updateCoinPartialByName(
    @Param('name') name: string,
    @Body() coin: Partial<Coin>,
  ): Promise<Coin> {
    return this.coinsService.updatePartialByName(name, coin);
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
