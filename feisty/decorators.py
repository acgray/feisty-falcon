import functools

import falcon
import marshmallow


class ValidationError(falcon.HTTPBadRequest):
    def __init__(self, errors):
        super(ValidationError, self).__init__(falcon.HTTP_400)
        self.errors = errors

    def to_dict(self, obj_type=dict):
        return {'errors': self.errors}


def request_schema(schema_or_cls, enforce=False, load_from='auto'):
    def decorator(f):
        if load_from not in ('query', 'body', 'auto'):
            raise ValueError(
                'load_from must be one of "query", "body", or "auto')

        schema = _get_schema_instance(schema_or_cls)

        if load_from == 'query' or (
                load_from == 'auto' and f.__name__ == 'on_get'):
            load_attr = 'params'
        elif load_from == 'body' or (
                load_from == 'auto' and f.__name__ == 'on_post'):
            load_attr = 'media'
        else:
            raise ValueError(
                'Don\'t know how to load data from a {} handler. '
                'Specify load_from manually.')

        f._feisty_request_schema = schema
        f._feisty_request_schema_in = (
            'query' if load_attr == 'params' else 'body')

        @functools.wraps(f)
        def _wrapped(self, req, resp, *args, **kwargs):

            data = getattr(req, load_attr)

            if enforce:
                result = schema.load(data)
                if result.errors:
                    raise ValidationError(result.errors)
                data = result.data
            else:
                data = req.media
            return f(self, req, resp, data, *args, **kwargs)

        return _wrapped

    return decorator


def response_schema(schema_or_cls, enforce=True):
    schema = _get_schema_instance(schema_or_cls)

    def decorator(f):
        f._feisty_response_schema = schema

        @functools.wraps(f)
        def _wrapped(self, req, resp, *args, **kwargs):
            ret = f(self, req, resp, *args, **kwargs)
            if enforce:
                result = schema.dump(resp.media)
                resp.media = result.data
            return ret

        return _wrapped

    return decorator


def _get_schema_instance(schema_or_cls):
    if isinstance(schema_or_cls, type):
        schema = schema_or_cls()
    elif isinstance(schema_or_cls, marshmallow.Schema):
        schema = schema_or_cls
    else:
        raise TypeError(
            'schema_or_class must be a marshmallow Schema class or instance')

    return schema
