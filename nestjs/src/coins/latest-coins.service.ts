import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { LatestCoinData } from './latest-coins.entity';

@Injectable()
export class LatestCoinDataService {
  constructor(
    @InjectRepository(LatestCoinData)
    private readonly latestCoinDataRepository: Repository<LatestCoinData>,
  ) {}

  async findAll(): Promise<any[]> {
    return this.latestCoinDataRepository
      .createQueryBuilder('latestCoinData')
      .leftJoinAndSelect('latestCoinData.coin', 'coin')
      .select(['latestCoinData', 'coin.coin_name'])
      .getMany();
  }

  async findByExchange(exchange: string): Promise<any[]> {
    return this.latestCoinDataRepository
      .createQueryBuilder('latestCoinData')
      .leftJoinAndSelect('latestCoinData.coin', 'coin')
      .select(['latestCoinData', 'coin.coin_name'])
      .where('latestCoinData.exchange = :exchange', { exchange })
      .getMany();
  }

  async findByCoin(coin_id: number): Promise<any[]> {
    return this.latestCoinDataRepository
      .createQueryBuilder('latestCoinData')
      .leftJoinAndSelect('latestCoinData.coin', 'coin')
      .select(['latestCoinData', 'coin.coin_name'])
      .where('latestCoinData.coin_id = :coin_id', { coin_id })
      .getMany();
  }

  async findByCoinAndExchange(
    coin_id: number,
    exchange: string,
  ): Promise<any[]> {
    return this.latestCoinDataRepository
      .createQueryBuilder('latestCoinData')
      .leftJoinAndSelect('latestCoinData.coin', 'coin')
      .select(['latestCoinData', 'coin.coin_name'])
      .where('latestCoinData.coin_id = :coin_id', { coin_id })
      .andWhere('latestCoinData.exchange = :exchange', { exchange })
      .getMany();
  }

  async findLatestByCoin(coin_id: number): Promise<any> {
    return this.latestCoinDataRepository
      .createQueryBuilder('latestCoinData')
      .leftJoinAndSelect('latestCoinData.coin', 'coin')
      .select(['latestCoinData', 'coin.coin_name'])
      .where('latestCoinData.coin_id = :coin_id', { coin_id })
      .orderBy('latestCoinData.timestamp', 'DESC')
      .getOne();
  }

  async findLatestByExchangeAndCoin(
    coin_id: number,
    exchange: string,
  ): Promise<any> {
    return this.latestCoinDataRepository
      .createQueryBuilder('latestCoinData')
      .leftJoinAndSelect('latestCoinData.coin', 'coin')
      .select(['latestCoinData', 'coin.coin_name'])
      .where('latestCoinData.coin_id = :coin_id', { coin_id })
      .andWhere('latestCoinData.exchange = :exchange', { exchange })
      .orderBy('latestCoinData.timestamp', 'DESC')
      .getOne();
  }
}
