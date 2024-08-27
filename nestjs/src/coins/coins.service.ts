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

  // Create a new coin
  create(coin_name: string): Promise<Coin> {
    const coin = this.coinsRepository.create({ coin_name });
    return this.coinsRepository.save(coin);
  }

  // Update a coin's data
  async updateCoinData(
    id: number,
    updateData: Partial<CoinData>,
  ): Promise<CoinData> {
    await this.coinDataRepository.update(id, updateData);
    return this.coinDataRepository.findOne({ where: { data_id: id } });
  }

  // Delete a coin
  async remove(id: number): Promise<void> {
    await this.coinsRepository.delete(id);
  }

  // Delete coin data
  async removeCoinData(id: number): Promise<void> {
    await this.coinDataRepository.delete(id);
  }
}
