import {
  IsEnum,
  IsNotEmpty,
  IsNumber,
  IsString,
  IsOptional,
} from 'class-validator';
import { ExchangeEnum } from 'src/coins/entities/coin-data.entity';

export class CreateOrderDto {
  @IsOptional() // Optional so either coin_id or coin_name can be provided
  @IsNumber()
  coin_id?: number;

  @IsOptional() // Optional so either coin_id or coin_name can be provided
  @IsString()
  coin_name?: string;

  @IsEnum(ExchangeEnum)
  exchange: ExchangeEnum;

  @IsNotEmpty()
  @IsString()
  symbol: string;

  @IsNotEmpty()
  @IsEnum(['LONG', 'SHORT'])
  side: 'LONG' | 'SHORT';

  @IsNumber()
  mean_premium: number;

  @IsNotEmpty()
  @IsNumber()
  entry_premium: number;

  @IsNotEmpty()
  @IsNumber()
  exit_premium: number;

  @IsNotEmpty()
  @IsNumber()
  quantity: number;

  @IsNumber()
  executed_quantity_entry: number;

  @IsNumber()
  executed_quantity_exit: number;
}
