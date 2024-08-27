import {
  Injectable,
  NotFoundException,
  BadRequestException,
} from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository, DataSource } from 'typeorm';
import { Order } from './entities/order.entity';
import { CreateOrderDto } from './dto/create-order.dto';
import { UpdateOrderDto } from './dto/update-order.dto';
import { Coin } from 'src/coins/coins.entity';

@Injectable()
export class OrdersService {
  constructor(
    @InjectRepository(Order)
    private readonly orderRepository: Repository<Order>,
    @InjectRepository(Coin)
    private readonly coinRepository: Repository<Coin>,
    private readonly dataSource: DataSource, // Inject DataSource
  ) {}

  async create(createOrderDto: CreateOrderDto): Promise<Order> {
    const { coin_id, coin_name, ...rest } = createOrderDto;

    let coin: Coin | null = null;

    if (coin_id) {
      coin = await this.coinRepository.findOne({ where: { coin_id } });
      if (!coin) {
        throw new NotFoundException(`Coin with ID ${coin_id} not found`);
      }
    } else if (coin_name) {
      coin = await this.coinRepository.findOne({ where: { coin_name } });
      if (!coin) {
        throw new NotFoundException(`Coin with name ${coin_name} not found`);
      }
    } else {
      throw new BadRequestException(
        'Either coin_id or coin_name must be provided',
      );
    }

    // Create the Order entity and set the coin relation
    const order = this.orderRepository.create({ ...rest, coin });
    return this.orderRepository.save(order);
  }

  async findAll(): Promise<Order[]> {
    return this.orderRepository.find({ relations: ['coin'] });
  }

  async findOne(id: number): Promise<Order> {
    const order = await this.orderRepository.findOne({
      where: { id: Number(id) }, // Ensure id is a number
      relations: ['coin'], // Include the relations you need
    });

    if (!order) {
      throw new NotFoundException(`Order with ID ${id} not found`);
    }

    return order;
  }

  async update(id: number, updateOrderDto: UpdateOrderDto): Promise<Order> {
    const { coin_id, coin_name, ...rest } = updateOrderDto;

    // Find the existing order by ID
    const existingOrder = await this.orderRepository.findOne({
      where: { id },
      relations: ['coin'],
    });

    if (!existingOrder) {
      throw new NotFoundException(`Order with ID ${id} not found`);
    }

    // Handle coin update if coin_id or coin_name is provided
    let coin: Coin | null = null;
    if (coin_id) {
      coin = await this.coinRepository.findOne({ where: { coin_id } });
      if (!coin) {
        throw new NotFoundException(`Coin with ID ${coin_id} not found`);
      }
    } else if (coin_name) {
      coin = await this.coinRepository.findOne({ where: { coin_name } });
      if (!coin) {
        throw new NotFoundException(`Coin with name ${coin_name} not found`);
      }
    }

    // Use DataSource for QueryBuilder to update the order
    const result = await this.dataSource
      .createQueryBuilder()
      .update(Order)
      .set({
        ...rest,
        coin: coin ?? existingOrder.coin, // Ensure coin is set correctly
      })
      .where('id = :id', { id })
      .execute();

    // Check if the update affected any rows (i.e., if the order was updated)
    if (result.affected === 0) {
      throw new NotFoundException(`Order with ID ${id} not found`);
    }

    // Return the updated order
    return this.orderRepository.findOne({ where: { id }, relations: ['coin'] });
  }

  async remove(id: number): Promise<void> {
    const order = await this.findOne(id);
    await this.orderRepository.remove(order);
  }

  async deleteAll(): Promise<void> {
    await this.orderRepository.clear(); // This will delete all records from the orders table
  }
}
