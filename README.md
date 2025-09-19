# Live coding task description

Please check [openapi documentation](./openapi.yaml) for endpoint descriptions and request/response examples.\
We suggest to utilize https://editor.swagger.io/ for more convenient view. Just copy the content of the .yaml file there.


Task 1:
* Create a .py test file
* Initialise RequestMock class and make the instance usable in every possible future test case.\
_Useful info:_
```
# import
from mock_requests.api_client import RequestMock

# URL to use:
"https://api.example.com/data"

# available methods: get(), post(), delete()
```
Task 2:
* Test order creation flow

Task 3 (Optional):
* Test order deletion flow
