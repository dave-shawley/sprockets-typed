import http
import json
import types
import typing

import pydantic
from tornado import httputil, web

from sprockets_typed import exceptions


class TypedRequestHandler(web.RequestHandler):
    """Handles HTTP requests with deserialization and validation support.

    This class is designed to extend Tornado's web.RequestHandler by
    adding convenient methods for deserializing incoming request bodies
    and validating them against specified types. It supports multiple
    content types, including JSON, and leverages the flexibility of
    pydantic for type validation.

    """

    def __deserialize_with_tornado(
        self, content_type: str
    ) -> dict[str, list[str] | str | None] | None:
        """Deserialize with tornado.httputil

        Returns: `None` if no deserialization was possible.
        """
        parsed_args: dict[str, list[bytes]] = {}
        try:
            httputil.parse_body_arguments(
                content_type,
                self.request.body,
                parsed_args,
                {},
                self.request.headers,
            )
        except httputil.HTTPInputError as error:
            raise web.HTTPError(
                http.HTTPStatus.UNPROCESSABLE_ENTITY
            ) from error
        else:
            if parsed_args:
                output: dict[str, list[str] | str | None] = {}
                for k, v in parsed_args.items():
                    match len(v):
                        case 0:
                            output[k] = None
                        case 1:
                            output[k] = v[0].decode('utf-8')
                        case _:
                            output[k] = [item.decode('utf-8') for item in v]
                return output

        return None

    def _deserialize_body(self) -> object | None:
        # support sprockets.mixins.mediatype
        if hook := getattr(self, 'get_request_body', None):
            return typing.cast('object', hook())

        content_type = self.request.headers.get(
            'content-type', 'binary/octet-stream'
        )

        parsed_data = self.__deserialize_with_tornado(content_type)
        if parsed_data is not None:
            return parsed_data

        # the most naive JSON deserialization ever
        mime_type, _, _ = content_type.partition(';')
        if mime_type == 'application/json' or mime_type.endswith('+json'):
            return typing.cast('object', json.loads(self.request.body))

        # Give up ... if you want something more here, then install
        # sprockets.mixins.mediatype.
        raise exceptions.RequestValidationError(
            http.HTTPStatus.UNSUPPORTED_MEDIA_TYPE
        )

    def get_request_as[T](self, body_cls: type[T]) -> T | None:
        """Deserialize and validate the request body.

        Deserializes the body of the request and validates it against the
        provided type. The method ensures that the request body is properly
        validated or raises an error if it cannot be validated or is
        incompatible with the specified type.

        Args:
            body_cls (type[T]): The target class type to which the body
                should be validated. Can be a subclass of pydantic.BaseModel
                or any other type.

        Returns:
            T | None: The deserialized and validated request body of the
                specified type, or None if the target class type is NoneType
                and the body is empty.

        Raises:
            RequestValidationError: If the body cannot be deserialized,
                validated, or does not match the specified class type.

        """
        body = self._deserialize_body()
        if body_cls is types.NoneType or body_cls is None:
            if body == b'' or body is None:
                return None
            raise exceptions.RequestValidationError(
                http.HTTPStatus.UNPROCESSABLE_ENTITY
            )

        if issubclass(body_cls, pydantic.BaseModel):
            try:
                return body_cls.model_validate(body)
            except pydantic.ValidationError as error:
                raise exceptions.RequestValidationError(
                    http.HTTPStatus.UNPROCESSABLE_ENTITY
                ) from error

        if isinstance(body, body_cls):
            return body

        raise exceptions.RequestValidationError(
            http.HTTPStatus.UNPROCESSABLE_ENTITY
        )
