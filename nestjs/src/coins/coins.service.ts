import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Coin } from './coins.entity';
import { CoinData, ExchangeEnum } from './entities/coin-data.entity';

@Injectable()
export class CoinsService {
  constructor(
    @InjectRepository(Coin)
    private coinsRepository: Repository<Coin>,
    @InjectRepository(CoinData)
    private coinDataRepository: Repository<CoinData>,
  ) {}

  // Get all coins
  findAll(): Promise<Coin[]> {
    return this.coinsRepository.find();
  }

  async findCoinIdByName(coin_name: string): Promise<number | null> {
    const coin = await this.coinsRepository.findOne({ where: { coin_name } });
    return coin ? coin.coin_id : null;
  }

  // Get all data for a specific coin by coin_name with pagination
  async findAllByCoinName(
    coin_name: string,
    limit: number,
    offset: number,
  ): Promise<CoinData[]> {
    const coin = await this.coinsRepository.findOne({ where: { coin_name } });
    if (!coin) {
      throw new Error('Coin not found');
    }
    return this.coinDataRepository.find({
      where: { coin: { coin_id: coin.coin_id } },
      relations: ['coin'],
      order: { timestamp: 'DESC' }, // Order by timestamp descending
      take: limit,
      skip: offset,
    });
  }

  // Get all coins from a specific exchange with pagination
  async findAllByExchange(
    exchange: 'BINANCE' | 'COINEX',
    limit: number,
    offset: number,
  ): Promise<CoinData[]> {
    return this.coinDataRepository.find({
      where: { exchange: exchange as ExchangeEnum },
      relations: ['coin'],
      order: { timestamp: 'DESC' }, // Order by timestamp descending
      take: limit,
      skip: offset,
    });
  }

  // Get all data for a specific coin and exchange with pagination
  async findAllByCoinNameAndExchange(
    coin_name: string,
    exchange: 'BINANCE' | 'COINEX',
    limit: number,
    offset: number,
  ): Promise<CoinData[]> {
    const coin = await this.coinsRepository.findOne({ where: { coin_name } });
    if (!coin) {
      throw new Error('Coin not found');
    }
    return this.coinDataRepository.find({
      where: {
        coin: { coin_id: coin.coin_id },
        exchange: exchange as ExchangeEnum,
      },
      relations: ['coin'],
      order: { timestamp: 'DESC' }, // Order by timestamp descending
      take: limit,
      skip: offset,
    });
  }

  async findMostRecentPriceByCoinName(coin_name: string): Promise<any[]> {
    const coin = await this.coinsRepository.findOne({ where: { coin_name } });
    if (!coin) {
      throw new Error('Coin not found');
    }

    return this.coinDataRepository
      .createQueryBuilder('coin_data')
      .innerJoin(
        (qb) =>
          qb
            .select('exchange')
            .addSelect('MAX(timestamp)', 'max_timestamp')
            .from(CoinData, 'coin_data')
            .where('coin_data.coin_id = :coin_id', { coin_id: coin.coin_id })
            .groupBy('exchange'),
        'max_data',
        'coin_data.exchange = max_data.exchange AND coin_data.timestamp = max_data.max_timestamp',
      )
      .select('coin_data') // Select all fields from coin_data
      .where('coin_data.coin_id = :coin_id', { coin_id: coin.coin_id })
      .orderBy('coin_data.timestamp', 'DESC')
      .getMany();
  }

  //create coin
  async createCoin(coin: Coin): Promise<Coin> {
    return this.coinsRepository.save(coin);
  }

  async updateCoin(id: number, coinData: Partial<Coin>): Promise<Coin> {
    await this.coinsRepository.update(id, coinData);
    // Use an explicit condition structure for the 'where' clause
    return this.coinsRepository.findOne({
      where: { coin_id: id }, // Assuring that 'id' is recognized as a valid property
    });
  }

  async updatePartial(id: number, coinData: Partial<Coin>): Promise<Coin> {
    await this.coinsRepository.update(id, coinData);
    return this.coinsRepository.findOne({
      where: { coin_id: id },
    });
  }

  async updateCoinByName(name: string, coinData: Partial<Coin>): Promise<Coin> {
    await this.coinsRepository.update({ coin_name: name }, coinData);
    return this.coinsRepository.findOne({
      where: { coin_name: name },
    });
  }

  async updatePartialByName(
    name: string,
    coinData: Partial<Coin>,
  ): Promise<Coin> {
    await this.coinsRepository.update({ coin_name: name }, coinData);
    return this.coinsRepository.findOne({
      where: { coin_name: name },
    });
  }

  async delete(id: number): Promise<void> {
    await this.coinsRepository.delete(id);
  }

  async deleteByName(name: string): Promise<void> {
    await this.coinsRepository.delete({ coin_name: name });
  }
}
