import { Controller, Get, Query, BadRequestException } from '@nestjs/common';
import { LatestCoinDataService } from './latest-coins.service';
import { LatestCoinData } from './latest-coins.entity';
import { CoinsService } from './coins.service';

@Controller('latest-coin-data')
export class LatestCoinDataController {
  constructor(
    private readonly latestCoinDataService: LatestCoinDataService,
    private readonly coinService: CoinsService, // Inject the CoinService
  ) {}

  @Get()
  async findAll(): Promise<LatestCoinData[]> {
    return this.latestCoinDataService.findAll();
  }

  @Get('exchange')
  async findByExchange(
    @Query('exchange') exchange: string,
  ): Promise<LatestCoinData[]> {
    return this.latestCoinDataService.findByExchange(exchange);
  }

  @Get('coin')
  async findByCoin(
    @Query('coin_id') coin_id?: number,
    @Query('coin_name') coin_name?: string,
  ): Promise<LatestCoinData[]> {
    // Resolve coin_id if coin_name is provided
    if (!coin_id && coin_name) {
      coin_id = await this.coinService.findCoinIdByName(coin_name);
      if (!coin_id) {
        throw new BadRequestException('Coin not found');
      }
    }

    if (!coin_id) {
      throw new BadRequestException('coin_id or coin_name must be provided');
    }

    return this.latestCoinDataService.findByCoin(coin_id);
  }

  @Get('coin-exchange')
  async findByCoinAndExchange(
    @Query('exchange') exchange: string,
    @Query('coin_id') coin_id?: number,
    @Query('coin_name') coin_name?: string,
  ): Promise<LatestCoinData[]> {
    // Resolve coin_id if coin_name is provided
    if (!coin_id && coin_name) {
      coin_id = await this.coinService.findCoinIdByName(coin_name);
      if (!coin_id) {
        throw new BadRequestException('Coin not found');
      }
    }

    if (!coin_id || !exchange) {
      throw new BadRequestException(
        'coin_id or coin_name and exchange must be provided',
      );
    }

    return this.latestCoinDataService.findByCoinAndExchange(coin_id, exchange);
  }
}
