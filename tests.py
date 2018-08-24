import collections

import falcon.testing
import falcon.util
import marshmallow.validate
import pytest

import feisty
import feisty.generate

api = falcon.API()


class RequestSchema(marshmallow.Schema):
    name = marshmallow.fields.String(
        validate=marshmallow.validate.OneOf(['Adam']))


class TestResource(object):
    @feisty.request_schema(RequestSchema(), enforce=True)
    def on_post(self, req, resp, data):
        resp.media = {'received': data}

    @feisty.request_schema(RequestSchema(), enforce=True)
    def on_get(self, req, resp, data):
        resp.media = {'received': data}


class TestClassResource(object):
    @feisty.request_schema(RequestSchema, enforce=True)
    def on_post(self, req, resp, data):
        resp.media = {'received': data}

    @feisty.request_schema(RequestSchema, enforce=True)
    def on_get(self, req, resp, data):
        resp.media = {'received': data}


api.add_route('/test', TestResource())
api.add_route('/test_class', TestClassResource())


@pytest.fixture
def client():
    return falcon.testing.TestClient(api)


@pytest.mark.parametrize('endpoint', ['/test', '/test_class'])
def test_on_post_decorator_rejects_invalid_input(client, endpoint):
    resp = client.simulate_post(endpoint, json={'name': 'Nathan'})

    assert resp.status_code == 400
    assert resp.json == {'errors': {'name': ['Not a valid choice.']}}


@pytest.mark.parametrize('endpoint', ['/test', '/test_class'])
def test_on_post_decorator_accepts_valid_input(client, endpoint):
    resp = client.simulate_post(endpoint, json={'name': 'Adam'})

    assert resp.status_code == 200
    assert resp.json == {'received': {'name': 'Adam'}}


@pytest.mark.parametrize('endpoint', ['/test', '/test_class'])
def test_on_get_decorator_rejects_invalid_input(client, endpoint):
    resp = client.simulate_get(endpoint, query_string='name=Nathan')

    assert resp.status_code == 400
    assert resp.json == {'errors': {'name': ['Not a valid choice.']}}


@pytest.mark.parametrize('endpoint', ['/test', '/test_class'])
def test_on_post_decorator_accepts_valid_input(client, endpoint):
    resp = client.simulate_get(endpoint, query_string='name=Adam')

    assert resp.status_code == 200
    assert resp.json == {'received': {'name': 'Adam'}}


@pytest.mark.parametrize('cls', [TestResource, TestClassResource])
def test_response_decorators_set_schema_metadata(cls):
    assert isinstance(cls.on_get._feisty_request_schema, RequestSchema)
    assert isinstance(cls.on_post._feisty_request_schema, RequestSchema)


def test_generate_apispec():
    spec = feisty.generate.generate_schema(api, {
        'title': 'Test API',
        'version': '0.0.1'})
    want_schema = {
        'info': {
            'title': 'Test API',
            'version': '0.0.1'
        },
        'paths': collections.OrderedDict([
            ('/test', {
                'get': {
                    'parameters': [
                        {'in': 'body',
                         'schema': {
                             'type': 'object',
                             'properties': {
                                 'name': {
                                     'type': 'string',
                                     'enum': ['Adam']}}}}],
                    'responses': {
                        200: {}}},
                'post': {
                    'parameters': [
                        {'in': 'body',
                         'schema': {
                             'type': 'object',
                             'properties': {
                                 'name': {
                                     'type': 'string',
                                     'enum': ['Adam']}}}}],
                    'responses': {
                        200: {}}}}), (
                '/test_class', {'get': {
                    'parameters': [{
                        'in': 'body',
                        'schema': {
                            'type': 'object',
                            'properties': {
                                'name': {
                                    'type': 'string',
                                    'enum': ['Adam']}}}}],
                    'responses': {200: {}}}, 'post': {
                    'parameters': [{'in': 'body',
                                    'schema': {
                                        'type': 'object',
                                        'properties': {
                                            'name': {
                                                'type': 'string',
                                                'enum': ['Adam']}}}}],
                    'responses': {200: {}}}})]),
        'tags': [],
        'swagger': '2.0',
        'definitions': {},
        'parameters': {}}

    assert spec.to_dict() == want_schema

