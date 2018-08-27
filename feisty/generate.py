import functools
import os

import apispec
import apispec.ext.marshmallow
import marshmallow
import yaml


class FeistyConfigSchema(marshmallow.Schema):
    title = marshmallow.fields.String(required=True)
    version = marshmallow.fields.String(required=True)


converter = apispec.ext.marshmallow.OpenAPIConverter('2.0')


def _recurse_nodes(nodes, spec):
    for node in nodes:
        if hasattr(node, 'children') and node.children:
            _recurse_nodes(node.children, spec)
        else:
            ops = {}
            for method, f in node.method_map.items():
                if (method.lower() not in ['get', 'put', 'post', 'delete']
                        or isinstance(f, functools.partial)):
                    continue

                req_schema = getattr(f, '_feisty_request_schema', None)
                resp_schema = getattr(f, '_feisty_response_schema', None)

                op = {'parameters': [], 'responses': {200: {}}}
                if req_schema:
                    op['parameters'] = converter.schema2parameters(
                        req_schema,
                        default_in=f._feisty_request_schema_in)

                if resp_schema:
                    op['responses'][200][
                        'schema'] = converter.schema2jsonschema(
                        resp_schema)

                ops[method.lower()] = op

            spec.add_path(node.uri_template, ops)


def generate_schema(api, config=None):
    if not config:
        cwd = os.getcwd()
        try:
            with open(os.path.join(cwd, '.feistyrc.yaml')) as f:
                config = yaml.load(f)
        except (IOError, OSError):
            raise ValueError('Could not find .feistyrc.yaml file')

    schema = FeistyConfigSchema()
    result = schema.load(config)

    if result.errors:
        raise ValueError('Invalid Feisty config: {}'.format(result.errors))

    config = result.data

    spec = apispec.APISpec(
        config['title'],
        str(config['version']),
        openapi_version='2.0',
        plugins=(apispec.ext.marshmallow.MarshmallowPlugin(),))

    _recurse_nodes(api._router._roots, spec)

    return spec
