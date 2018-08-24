# feisty-falcon

Give your [Falcon](https://falcon-framework.org) some [Swagger](https://www.swagger.io).

Feisty is a suite of tools for automatically generating Swagger API specs
from your Falcon API, powered by [apispec](https://github.com/marshmallow-code/apispec)
and [Marshmallow](https://github.com/marshmallow-code/marshmallow).

## Installation

```bash
pip install feisty
```

## Usage

### Schema generation

Feisty provides decorators to specify the request and response schemas for
your Falcon handler methods, as follows:

```python
import falcon
import marshmallow
import marshmallow.validate

import feisty


class GetPetsRequest(marshmallow.Schema):
    pet_type = marshmallow.fields.String(
        validate=marshmallow.validate.OneOf(['dog', 'cat']))
    min_age = marshmallow.fields.Integer()


class GetPetsResponseData(marshmallow.Schema):
    name = marshmallow.fields.String(required=True)
    pet_type = marshmallow.fields.String(
        validate=marshmallow.validate.OneOf(['dog', 'cat']),
        required=True)
    age = marshmallow.fields.Integer(required=True)


class GetPetsResponse(marshmallow.Schema):
    data = marshmallow.fields.Nested(
        GetPetsResponseData(),
        required=True)


class PetsCollection(object):
    @feisty.request_schema(GetPetsRequest())
    @feisty.response_schema(GetPetsResponse())
    def on_get(self, req, resp, data):
        pet_type = req.params.get('pet_type')
        resp.media = {
            'data': [{
                'name': 'Theo',
                'pet_type': 'cat',
                'age': 1}]}


api = falcon.API()

api.add_route('/pets', PetsCollection())
```

You additionally need to put a `.feistyrc.yml` file in your project root,
specifying the title and version for your schema.  For example

```yaml
title: Pet Store
version: 1.0
```

You can then run `feisty your.module:your_falcon_api_obj` to output a Swagger
schema for your API.

In the above example, the output would be:

```yaml
definitions: {}
info: {title: Pet Store, version: '1.0'}
parameters: {}
paths:
  /pets:
    get:
      parameters:
      - {format: int32, in: query, name: min_age, required: false, type: integer}
      - enum: [dog, cat]
        in: query
        name: pet_type
        required: false
        type: string
      responses:
        200:
          schema:
            properties:
              data:
                properties:
                  age: {format: int32, type: integer}
                  name: {type: string}
                  pet_type:
                    enum: [dog, cat]
                    type: string
                required: [age, name, pet_type]
                type: object
            required: [data]
            type: object
swagger: '2.0'
tags: []
```

### Validation

Optionally, you can pass `enforce=True` to either decorator.

For request schemas, this will validate input against the schema and raise a
`ValidationError` for any errors.  This extends the Falcon HTTP 400 exception
so will automatically trigger a 400 response with the Marshmallow validation
error passed to the client.

For response schemas, the response `media` will be loaded with the given schema
and then dumped back into `resp.media`.