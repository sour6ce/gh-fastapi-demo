import os
from enum import StrEnum
from typing import List

import redis
from fastapi import FastAPI
from pydantic import BaseModel, validator

# region Cache Load

REDIS_URL = os.environ.get('REDIS_URL', "redis://localhost:6379")
REDIS_ON = False

if REDIS_URL is not None:
    cache = redis.from_url(REDIS_URL)
    try:
        REDIS_ON = cache.ping()
    except:
        pass


# endregion


# region Models

Status = StrEnum('Status', 'completed pending canceled')

Criterion = StrEnum('Criterion', 'completed pending canceled all')


class Order(BaseModel):
    id: int
    item: str
    quantity: int
    price: float
    status: Status

    @validator('price')
    def check_price_not_negative(cls, price: float) -> float:
        if price < 0:
            raise ValueError('Price value mut be greater than or equal to 0')
        return price


class ProcessModel(BaseModel):
    orders: List[Order]
    criterion: Criterion

# endregion


app = FastAPI()

# region Endpoints


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/solution", response_model=float)
async def solution(data: ProcessModel) -> float:
    # Check if the cache has the value
    if REDIS_ON:
        key = data.json()
        result = cache.get(key)

        if result is None:
            result = process_orders(data.orders, data.criterion)
            cache.set(key, result)
            return result
        else:
            return float(result.decode('utf-8'))
    else:
        return process_orders(data.orders, data.criterion)

# endregion


def process_orders(orders, criterion):
    # Not interfering with signature but yet typing for better editor support
    orders: List[Order] = orders
    criterion: Criterion = criterion

    def match(order: Order, criterion: Criterion) -> bool:
        # The text in both enums definitions are the same except or 'all'
        return criterion == Criterion.all or \
            order.status.name == criterion.name

    return sum(
        (order.price * order.quantity for order in orders
         if match(order, criterion))
    )
