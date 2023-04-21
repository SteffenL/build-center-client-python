from typing import IO, Dict, Generic, Iterable, List, Sequence, TypeVar
import humps
import json

from build_center_client.api.api import AccessFlags, AccessTokenEndpoint, Api, AppEndpoint, \
    AssetEndpoint, ReleaseEndpoint, WebhookEndpoint, WebhookEvent, WebhookType
from build_center_client.api.encoding import ApiJsonEncoder
from .actions import FileArg


TEndpoint = TypeVar("TEndpoint")


class CommandsBase(Generic[TEndpoint]):
    def __init__(self, api: Api):
        self._api = api

    def create(self, **kwargs):
        endpoint = self._get_endpoint()
        print(ApiJsonEncoder.encode(endpoint.create(**kwargs)))

    def list(self, **kwargs):
        endpoint = self._get_endpoint()
        print(ApiJsonEncoder.encode(endpoint.list()))

    def get(self, id: str, **kwargs):
        endpoint = self._get_endpoint()
        print(ApiJsonEncoder.encode(endpoint.get(id)))

    def remove(self, id: str, **kwargs):
        endpoint = self._get_endpoint()
        endpoint.delete(id)

    def update(self, infile: FileArg):
        return self.update_from_io(infile.io())

    def update_from_io(self, io: IO):
        endpoint = self._get_endpoint()
        res = humps.decamelize(json.load(io))
        if isinstance(res, Sequence):
            sequence = tuple(
                map(lambda res_item: endpoint.update(**res_item), res))
            print(ApiJsonEncoder.encode(sequence))
        else:
            print(ApiJsonEncoder.encode(endpoint.update(**res)))

    def _get_endpoint(self) -> TEndpoint:
        return self._get_endpoint_impl(self._api)

    def _get_endpoint_impl(self) -> TEndpoint:
        raise Exception("Not implemented yet")


class AppCommands(CommandsBase[AppEndpoint]):
    def __init__(self, api: Api):
        super().__init__(api)

    def create(self, name: str, title: str, description: str = None, public: bool = False):
        return super().create(name=name, title=title, description=description, public=public)

    def _get_endpoint_impl(self, api) -> any:
        return api.apps


class ReleaseCommands(CommandsBase[ReleaseEndpoint]):
    def __init__(self, api: Api):
        super().__init__(api)

    def create(self, app: str, version: str, title: str = None, description: str = None,
               commit: str = None):
        app_ = self._api.apps.get(app)
        print(ApiJsonEncoder.encode(app_.releases().create(
            version=version, title=title, description=description,
            commit=commit, app_id=app_.id)))

    def list(self, app: str):
        app_ = self._api.apps.get(app)
        print(ApiJsonEncoder.encode(app_.releases().list()))

    def _get_endpoint_impl(self, api) -> any:
        return api.releases


class AssetCommands(CommandsBase[AssetEndpoint]):
    def __init__(self, api: Api):
        super().__init__(api)

    def create(self, release: str, file: FileArg, name: str = None, tag: Dict[str, str] = None):
        release_ = self._api.releases.get(release)
        print(ApiJsonEncoder.encode(release_.assets().create_with_file(
            name=file.basename() if name is None else name, file=file.io(),
            tags=tag)))

    def list(self, release: str):
        release_ = self._api.releases.get(release)
        print(ApiJsonEncoder.encode(release_.assets().list()))

    def download(self, id: str, out: FileArg):
        endpoint = self._get_endpoint()
        asset = endpoint.get(id)
        asset.download(out.io())

    def _get_endpoint_impl(self, api) -> any:
        return api.assets


class AccessTokenCommands(CommandsBase[AccessTokenEndpoint]):
    def __init__(self, api: Api):
        super().__init__(api)

    def create(self, app: str, access: AccessFlags,
               description: str = None, validity_duration: int = None,
               enabled: bool = False):
        if app is None:
            token = self._api.access_tokens.create(description=description, access=access,
                                                   validity_duration=validity_duration,
                                                   enabled=enabled)
        else:
            app_ = self._api.apps.get(app)
            token = app_.tokens().create(description=description, access=access,
                                         validity_duration=validity_duration,
                                         enabled=enabled)
        print(ApiJsonEncoder.encode(token))

    def list(self, app: str = None):
        if app is None:
            tokens = self._api.access_tokens.list()
        else:
            app_ = self._api.apps.get(app)
            tokens = app_.tokens().list()
        print(ApiJsonEncoder.encode(tokens))

    def _get_endpoint_impl(self, api) -> any:
        return api.access_tokens


class WebhookCommands(CommandsBase[WebhookEndpoint]):
    def __init__(self, api: Api):
        super().__init__(api)

    def create(self, app: str, type: WebhookType, url: str, events: List[WebhookEvent]):
        app_ = self._api.apps.get(app)
        print(ApiJsonEncoder.encode(app_.webhooks().create(
            type=type, url=url, events=events)))

    def list(self, app: str):
        app_ = self._api.apps.get(app)
        print(ApiJsonEncoder.encode(app_.webhooks().list()))

    def _get_endpoint_impl(self, api) -> any:
        return api.webhooks
