import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Coin } from './coins.entity';
import { CoinData, ExchangeEnum } from './coin-data.entity';

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

  // Get a coin by ID
  findOne(id: number): Promise<Coin> {
    return this.coinsRepository.findOne({ where: { coin_id: id } });
  }

  // Get all coins from a specific exchange
  async findAllByExchange(exchange: 'BINANCE' | 'COINEX'): Promise<CoinData[]> {
    return this.coinDataRepository.find({
      where: { exchange: exchange as ExchangeEnum },
      relations: ['coin'], // to get coin details as well
    });
  }

  // Get coin data by coin ID
  async findCoinData(coin_id: number): Promise<CoinData[]> {
    return this.coinDataRepository.find({ where: { coin: { coin_id } } });
  }

  // Create a new coin
  create(coin_name: string): Promise<Coin> {
    const coin = this.coinsRepository.create({ coin_name });
    return this.coinsRepository.save(coin);
  }

  // Create new coin data
  async createCoinData(coinData: Partial<CoinData>): Promise<CoinData> {
    const coin = await this.findOne(coinData.coin.coin_id);
    if (!coin) throw new Error('Coin not found');
    const newCoinData = this.coinDataRepository.create({ ...coinData, coin });
    return this.coinDataRepository.save(newCoinData);
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
