> Helpers for writing typesafe Tornado handlers.

Static type analysis is a great way to catch bugs. It is also a great way to inform editors, AI assistants, and other
tools about the contracts within your code. This library started out as a way to improve the docuemntation of Tornado
web applications with hopes of being able to keep OpenAPI specifications up to date in addition to providing type
safety inside the codebase.

```python
import uuid

import pydantic
import sprockets_typed
from tornado import web

class CreateItemRequest(pydantic.BaseModel):
    name: str
    description: str

class Item(CreateItemRequest):
    id: uuid.UUID

class CreateItemHandler(sprockets_typed.RequestHandler,
                        web.RequestHandler):
    async def post(self) -> None:
        request = self.get_request_as(CreateItemRequest)
        item = await self.create_item(request)
        self.send_response(item)

    async def create_item(self, request: CreateItemRequest) -> Item:
        ...

class ItemHandler(sprockets_typed.RequestHandler,
                  web.RequestHandler):
    async def get(self, **_: object) -> None:
        item_id = self.get_path_argument('item_id', uuid.UUID)
        item = await self.get_item(item_id)
        if item is None:
            self.send_error(404)
        else:
            self.send_response(item)

    async def get_item(self, item_id: uuid.UUID) -> Item:
        ...
```

## Key functions

### get_request_as(model_cls)
Deserialize the request body as the given model. This will raise `exceptions.RequestValidationError` when the request
body cannot be deserialized as `model_cls`. The status code is set to "415 Unsupported Media Type" if the content type
is not supported and "422 Unprocessable Entity" if the request body does not match the model schema.

### send_response(response)
### get_path_argument(name, coerce_to)
### get_query_argument(name:, coerce_to, default)
