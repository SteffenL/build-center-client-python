from typing import Generic, IO, List, TypeVar
from dacite.config import Config
from dacite import from_dict
import posixpath
from enum import Enum
import json

from api.http import ApiHttpClient


TRequest = TypeVar("TRequest")
TResponse = TypeVar("TResponse")


class CreateResourceWithFileEndpoint(Generic[TResponse]):
    def __init__(self, url: str, client: ApiHttpClient, response_type: TResponse = None, **kwargs) -> None:
        self._create_with_file_url = url
        self._create_with_file_client = client
        self._create_with_file_response_type = response_type

    def create_with_file(self, name: str, file: IO, **kwargs):
        res_object, res_raw = self._create_with_file_client.post_with_files(
            self._create_with_file_url, files={"file": (name, file)}, data=kwargs)
        resource = from_dict(
            data_class=self._create_with_file_response_type, data=res_object, config=Config(cast=[Enum]))
        resource._client = self._create_with_file_client
        resource._raw = json.dumps(json.loads(res_raw), indent=2)
        return resource


class CreateResourceEndpoint(Generic[TRequest, TResponse]):
    def __init__(self, url: str, client: ApiHttpClient, request_type: TRequest = None, response_type: TResponse = None, **kwargs) -> None:
        self._create_url = url
        self._create_client = client
        self._create_request_type = request_type
        self._create_response_type = response_type

    def create(self, *args, **kwargs) -> TResponse:
        input_resource = self._create_request_type(*args, **kwargs)
        res_object, res_raw = self._create_client.post(
            self._create_url, input_resource)
        if isinstance(res_object, str):
            return json.dumps(json.loads(res_object), indent=2)
        resource = from_dict(
            data_class=self._create_response_type, data=res_object, config=Config(cast=[Enum]))
        resource._client = self._create_client
        resource._raw = json.dumps(json.loads(res_raw), indent=2)
        return resource


class UpdateResourceEndpoint(Generic[TRequest, TResponse]):
    def __init__(self, url: str, client: ApiHttpClient, request_type: TRequest = None, response_type: TResponse = None, **kwargs) -> None:
        self._update_url = url
        self._update_client = client
        self._update_request_type = request_type
        self._update_response_type = response_type

    def update(self, *args, **kwargs) -> TResponse:
        input_resource = self._update_request_type(*args, **kwargs)
        url = input_resource.url if input_resource.url else self._update_url
        res_object, res_raw = self._update_client.put(
            url, input_resource)
        if isinstance(res_object, str):
            return json.dumps(json.loads(res_object), indent=2)
        resource = from_dict(
            data_class=self._update_response_type, data=res_object, config=Config(cast=[Enum]))
        resource._client = self._update_client
        resource._raw = json.dumps(json.loads(res_raw), indent=2)
        return resource


class GetResourceEndpoint(Generic[TResponse]):
    def __init__(self, url: str, client: ApiHttpClient, response_type: TResponse = None, **kwargs) -> None:
        self._get_url = url
        self._get_client = client
        self._get_response_type = response_type

    def get(self, id: str, out_stream: IO = None) -> TResponse:
        if out_stream is None:
            res_object, res_raw = self._get_client.get(
                posixpath.join(self._get_url, id))
            if isinstance(res_object, str):
                return json.dumps(json.loads(res_object), indent=2)
            resource = from_dict(data_class=self._get_response_type,
                                 data=res_object, config=Config(cast=[Enum]))
            resource._client = self._get_client
            resource._raw = json.dumps(json.loads(res_raw), indent=2)
            return resource
        else:
            self._get_client.get(posixpath.join(
                self._get_url, id), out_stream=out_stream)


class ListResourceEndpoint(Generic[TResponse]):
    def __init__(self, url: str, client: ApiHttpClient, response_type: TResponse = None, **kwargs) -> None:
        self._list_url = url
        self._list_client = client
        self._list_response_type = response_type

    def list(self) -> List[TResponse]:
        res_objects, res_raws = self._list_client.get(self._list_url)
        resources = []
        for res_object, res_raw in zip(res_objects, json.loads(res_raws)):
            res_raw = json.dumps(res_raw, indent=2)
            resource = from_dict(data_class=self._list_response_type,
                                 data=res_object,
                                 config=Config(cast=[Enum]))
            resource._client = self._list_client
            resource._raw = res_raw
            resources.append(resource)
        return resources


class DeleteResourceEndpoint:
    def __init__(self, url: str = None, client: ApiHttpClient = None, **kwargs) -> None:
        self._delete_url = url
        self._delete_client = client

    def delete(self, id: str):
        self._delete_client.delete(posixpath.join(self._delete_url, id))
