import falcon
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
    def on_get(self, req, resp):
        pet_type = req.params.get('pet_type')
        resp.media = {
            'data': [{
                'name': 'Theo',
                'pet_type': 'cat',
                'age': 1}]}


api = falcon.API()

api.add_route('/pets', PetsCollection())
