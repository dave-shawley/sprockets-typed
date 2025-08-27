import http
import types
import unittest
import urllib.parse
from unittest import mock

import pydantic
from tornado import httputil, web

import sprockets_typed

UNSPECIFIED = mock.sentinel.UNSPECIFIED


class RequestHandler(sprockets_typed.TypedRequestHandler, web.RequestHandler):
    pass


class CreateRequestPayload(pydantic.BaseModel):
    name: str
    description: str
    line_items: list[str] = pydantic.Field(default_factory=list)


def create_request_handler(
    *, body: bytes | None = None, content_type: str | None = UNSPECIFIED
) -> RequestHandler:
    application = mock.Mock(spec=web.Application)
    application.ui_methods = {}
    application.ui_modules = {}
    return RequestHandler(
        application=application,
        request=create_request(body=body, content_type=content_type),
    )


def create_request(
    *, body: bytes | None, content_type: str | None = UNSPECIFIED
) -> httputil.HTTPServerRequest:
    request = httputil.HTTPServerRequest('POST' if body else 'GET', '/')
    request.connection = mock.Mock()
    request.body = body or b''
    if content_type is UNSPECIFIED and request.body:
        request.headers['content-type'] = 'application/json'
    elif content_type is not UNSPECIFIED and content_type is not None:
        request.headers['content-type'] = content_type
    return request


class GetRequestAsTests(unittest.TestCase):
    def test_primitive_types(self) -> None:
        expectations = [
            (b'true', True),
            (b'false', False),
            (b'42', 42),
            (b'3.14', 3.14),
            ('"¡Hola!"'.encode(), '¡Hola!'),
            (b'null', None),
        ]
        handler = create_request_handler()
        for body, expected in expectations:
            handler.request = create_request(
                body=body, content_type='application/json'
            )
            try:
                result = handler.get_request_as(type(expected))
            except Exception as error:
                raise AssertionError(
                    f'Failed to parse {body!r} as {type(expected)}'
                ) from error
            self.assertEqual(expected, result)
            self.assertIsInstance(result, type(expected))

    def test_pydantic_model_as_form(self) -> None:
        payload = CreateRequestPayload.model_validate(
            {'name': 'foo', 'description': 'bar', 'line_items': ['one', 'two']}
        )
        handler = create_request_handler(
            body=urllib.parse.urlencode(
                [
                    ('name', payload.name),
                    ('description', payload.description),
                ]
                + [('line_items', v) for v in payload.line_items]
            ).encode('utf-8'),
            content_type='application/x-www-form-urlencoded',
        )

        result = handler.get_request_as(CreateRequestPayload)
        self.assertEqual(payload, result)
        self.assertIsInstance(result, CreateRequestPayload)

    def test_pydantic_model_as_json(self) -> None:
        payload = CreateRequestPayload.model_validate(
            {'name': 'foo', 'description': 'bar'}
        )
        handler = create_request_handler(
            body=payload.model_dump_json().encode('utf-8'),
            content_type='application/json',
        )

        result = handler.get_request_as(CreateRequestPayload)
        self.assertEqual(payload, result)
        self.assertIsInstance(result, CreateRequestPayload)

    def test_type_failures(self) -> None:
        test_cases = [
            (b'"some string"', int),
            (b'"not-none"', types.NoneType),
        ]

        handler = create_request_handler()
        for body, body_cls in test_cases:
            with self.assertRaises(sprockets_typed.RequestValidationError):
                handler.request = create_request(
                    body=body, content_type='application/json'
                )
                handler.get_request_as(body_cls)

    def test_pydantic_model_validation_failure(self) -> None:
        handler = create_request_handler(
            body=b'{"name": "foo", "description": 42}'
        )
        with self.assertRaises(sprockets_typed.RequestValidationError):
            handler.get_request_as(CreateRequestPayload)

    def test_form_data_parsing_failure(self) -> None:
        handler = create_request_handler(
            content_type='application/x-www-form-urlencoded',
            body=b'name=foo&description=bar&description=baz',
        )

        with self.assertRaises(web.HTTPError) as context:
            # content-encoding causes Tornado to fail
            handler.request.headers['content-encoding'] = 'gzip'
            handler.get_request_as(CreateRequestPayload)
        self.assertEqual(
            http.HTTPStatus.UNPROCESSABLE_ENTITY, context.exception.status_code
        )

    def test_unsupported_content_type(self) -> None:
        with self.assertRaises(web.HTTPError) as context:
            handler = create_request_handler(
                content_type='application/unsupported', body=b''
            )
            handler.get_request_as(CreateRequestPayload)
        self.assertEqual(
            http.HTTPStatus.UNSUPPORTED_MEDIA_TYPE,
            context.exception.status_code,
        )

    def test_that_get_request_body_is_called(self) -> None:
        handler = create_request_handler()
        handler.get_request_body = mock.Mock(return_value={'foo': 'bar'})  # type: ignore[attr-defined]
        result = handler.get_request_as(dict)
        self.assertEqual({'foo': 'bar'}, result)
        handler.get_request_body.assert_called_once()  # type: ignore[attr-defined]
