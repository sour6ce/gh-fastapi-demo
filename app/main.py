from enum import StrEnum
from typing import List

from fastapi import FastAPI
from pydantic import BaseModel, validator

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


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/solution", response_model=float)
async def solution(data: ProcessModel) -> float:
    process_orders(data.orders, data.criterion)


def process_orders(orders, criterion):
    raise NotImplementedError()
