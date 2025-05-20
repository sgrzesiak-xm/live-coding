from decimal import Decimal
from typing import Optional, Union, Dict
from urllib.parse import urlparse, parse_qs


def count_decimal_places(number: float) -> int:
    exponent = int(Decimal(str(number)).normalize().as_tuple().exponent)
    if exponent < 0:
        return -exponent
    return 0


class MockResponse:

    def __init__(self,
                 status_code: int,
                 json_data: Optional[dict] = None,
                 message: Union[str, dict] = "") -> None:
        self.status_code = status_code
        self.__json_data = json_data
        self.__message = message

    def json(self) -> dict:
        if self.__json_data is None:
            return {"message": self.__message}
        return self.__json_data


class RequestMock:

    def __init__(self) -> None:
        self.__url = "https://api.example.com/data"
        self.__db: Dict[int, Optional[dict]] = {}
        self.__allowed_symbols = ["EURUSD", "USDEUR", "JPYUSD"]
        self.__decimal_points = 5
        self.__order_directions = ["BUY", "SELL"]

    def get(self, url: str) -> MockResponse:
        if not url.startswith(self.__url):
            return MockResponse(status_code=404, message="Not Found")

        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)

        order_id = query_params.get('id', [None])[0]

        if order_id is None:
            return MockResponse(status_code=200, json_data=self.__db)

        if not order_id.isdigit():
            return MockResponse(status_code=400, message="Bad Request. ID must be an integer")

        order_id = int(order_id)
        order = self.__db.get(order_id)
        if not order:
            return MockResponse(status_code=404, message="Order not found")

        return MockResponse(status_code=200, json_data={order_id: order})

    def post(self, url: str, json: Optional[dict] = None) -> MockResponse:
        if url != self.__url:
            return MockResponse(status_code=404, message="Not Found")

        err_message = self.__validate_order(json)
        if err_message:
            return MockResponse(status_code=400, message=err_message)

        order_id = self.__get_id()
        self.__db[order_id] = json

        return MockResponse(status_code=200, json_data={"OrderID": order_id})

    def delete(self, url: str, json: Optional[dict] = None) -> MockResponse:
        if url != self.__url:
            return MockResponse(status_code=404, message="Not Found")

        if not json or not (order_id := json.get('id')):
            return MockResponse(status_code=400, message="Bad Request. ID is required")

        if not isinstance(order_id, int):
            return MockResponse(status_code=400, message="Bad Request. ID must be an integer")

        if order_id not in self.__db:
            return MockResponse(status_code=404, message="Order not found")

        del self.__db[order_id]
        return MockResponse(status_code=200, message="Order deleted")

    def __validate_order(self, order_payload: Optional[dict]) -> str:
        order_payload = order_payload or {}
        volume = order_payload.get('volume')
        symbol = order_payload.get('symbol')
        price = order_payload.get('price')
        direction = order_payload.get('direction')

        if not all(var is not None for var in [volume, symbol, price, direction]):
            return "Missing required fields"

        messages = []
        if not isinstance(volume, int) or volume < 1:
            messages.append("Volume must be an integer greater than 0")
        if symbol not in self.__allowed_symbols:
            messages.append("Invalid symbol")
        if not isinstance(price, float) or not count_decimal_places(price) == 5:
            messages.append("Price must be a number and have 5 decimal points")
        if direction not in self.__order_directions:
            messages.append("Invalid direction")

        return ", ".join(messages)

    def __get_id(self) -> int:
        return list(self.__db.keys())[-1] + 1 if self.__db.keys() else 1
