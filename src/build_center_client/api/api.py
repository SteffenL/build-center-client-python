from typing import Dict, IO, List, Optional, TypeVar, Union
from dataclasses import dataclass
import posixpath
from enum import Enum, IntFlag

from .base_endpoints import \
    CreateResourceEndpoint, \
    CreateResourceWithFileEndpoint, \
    DeleteResourceEndpoint, \
    GetResourceEndpoint, \
    ListResourceEndpoint, \
    UpdateResourceEndpoint
from .http import ApiHttpClient


TEndpoint = TypeVar("TEndpoint")


class HashAlgorithm(Enum):
    SHA256 = "sha256"


class AccessFlags(IntFlag):
    NONE = 0
    ADMIN = 1
    READ = 2
    WRITE = 4


@dataclass
class Asset:
    name: str

    id: Optional[str] = None
    created_at: Optional[int] = None
    content_size: Optional[int] = None
    content_hash_algorithm: Optional[HashAlgorithm] = None
    content_hash: Optional[str] = None
    tags: Dict[str, Optional[str]] = None
    url: Optional[str] = None

    _client: ApiHttpClient = None
    _raw: str = None

    def raw(self) -> str:
        return self._raw

    def download(self, io: IO):
        download_url = posixpath.join(self.url, "download")
        return self._client.get(download_url, "application/octet-stream", out_stream=io)


class AssetEndpoint(CreateResourceWithFileEndpoint[Asset],
                    ListResourceEndpoint[Asset],
                    GetResourceEndpoint[Asset],
                    DeleteResourceEndpoint):

    def create_with_file(self, name: str, file: IO, tags: Dict[str, str] = None):
        tags = None if tags is None else [tag[0] if len(tag) == 1 or tag[1] is None else (
            "%s=%s" % (tag[0], tag[1])) for tag in tags.items()]
        return super().create_with_file(name, file, tag=tags)

    def __init__(self, url: str, client: ApiHttpClient) -> None:
        CreateResourceWithFileEndpoint.__init__(
            self, url, client, response_type=Asset)
        ListResourceEndpoint.__init__(
            self, url, client, response_type=Asset)
        GetResourceEndpoint.__init__(
            self, url, client, response_type=Asset)
        DeleteResourceEndpoint.__init__(self, url, client)


@dataclass
class Release:
    version: str

    id: Optional[str] = None
    created_at: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    commit: Optional[str] = None
    prerelease: bool = False
    published: bool = False
    url: Optional[str] = None
    app_id: Optional[str] = None

    _client: ApiHttpClient = None
    _assets: AssetEndpoint = None
    _raw: str = None

    def raw(self) -> str:
        return self._raw

    def assets(self) -> Union[CreateResourceWithFileEndpoint[Asset],
                              ListResourceEndpoint[Asset]]:
        if self._assets is None:
            self._assets = AssetEndpoint(
                posixpath.join(self.url, "assets"), self._client)
        return self._assets


class ReleaseEndpoint(CreateResourceEndpoint[Release, Release],
                      ListResourceEndpoint[Release],
                      GetResourceEndpoint[Release],
                      UpdateResourceEndpoint[Release, Release],
                      DeleteResourceEndpoint):
    def __init__(self, url: str, client: ApiHttpClient) -> None:
        CreateResourceEndpoint.__init__(
            self, url, client, request_type=Release, response_type=Release)
        ListResourceEndpoint.__init__(
            self, url, client, response_type=Release)
        GetResourceEndpoint.__init__(
            self, url, client, response_type=Release)
        UpdateResourceEndpoint.__init__(
            self, url, client, request_type=Release, response_type=Release)
        DeleteResourceEndpoint.__init__(self, url, client)


class WebhookType(Enum):
    DISCORD = "discord"


class WebhookEvent(Enum):
    RELEASE_PUBLISHED = "release_published"
    PRERELEASE_PUBLISHED = "prerelease_published"


@dataclass
class Webhook:
    type: WebhookType
    url: str
    events: List[WebhookEvent]

    id: Optional[str] = None
    created_at: Optional[int] = None

    _client: ApiHttpClient = None
    _raw: str = None

    def raw(self) -> str:
        return self._raw


class WebhookEndpoint(CreateResourceEndpoint[Webhook, Webhook],
                      ListResourceEndpoint[Webhook],
                      GetResourceEndpoint[Webhook],
                      DeleteResourceEndpoint):
    def __init__(self, url: str, client: ApiHttpClient) -> None:
        CreateResourceEndpoint.__init__(
            self, url, client, request_type=Webhook, response_type=Webhook)
        ListResourceEndpoint.__init__(
            self, url, client, response_type=Webhook)
        GetResourceEndpoint.__init__(
            self, url, client, response_type=Webhook)
        DeleteResourceEndpoint.__init__(self, url, client)


@dataclass
class AccessToken:
    enabled: bool
    access: AccessFlags

    id: Optional[str] = None
    description: Optional[str] = None
    value: Optional[str] = None
    created_at: Optional[int] = None
    expires_at: Optional[int] = None
    app_id: Optional[str] = None
    url: Optional[str] = None

    _client: ApiHttpClient = None
    _raw: str = None

    def raw(self) -> str:
        return self._raw


@dataclass
class CreateAccessTokenCommand:
    enabled: bool
    access: AccessFlags

    app_id: Optional[str] = None
    description: Optional[str] = None
    validity_duration: Optional[int] = None


class AccessTokenEndpoint(CreateResourceEndpoint[CreateAccessTokenCommand, AccessToken],
                          ListResourceEndpoint[AccessToken],
                          GetResourceEndpoint[AccessToken],
                          DeleteResourceEndpoint):
    def __init__(self, url: str, client: ApiHttpClient) -> None:
        CreateResourceEndpoint.__init__(
            self, url, client, request_type=CreateAccessTokenCommand, response_type=AccessToken)
        ListResourceEndpoint.__init__(
            self, url, client, response_type=AccessToken)
        GetResourceEndpoint.__init__(
            self, url, client, response_type=AccessToken)
        DeleteResourceEndpoint.__init__(self, url, client)


@dataclass
class App:
    name: str
    title: str

    id: Optional[str] = None
    created_at: Optional[int] = None
    description: Optional[str] = None
    public: bool = False
    url: Optional[str] = None

    _client: ApiHttpClient = None
    _releases: ReleaseEndpoint = None
    _webhooks: WebhookEndpoint = None
    _tokens: AccessTokenEndpoint = None
    _raw: str = None

    def raw(self) -> str:
        return self._raw

    def releases(self) -> Union[CreateResourceEndpoint[Release, Release],
                                ListResourceEndpoint[Release]]:
        if self._releases is None:
            self._releases = ReleaseEndpoint(
                posixpath.join(self.url, "releases"), self._client)
        return self._releases

    def webhooks(self) -> Union[CreateResourceEndpoint[Webhook, Webhook],
                                ListResourceEndpoint[Webhook]]:
        if self._webhooks is None:
            self._webhooks = WebhookEndpoint(
                posixpath.join(self.url, "webhooks"), self._client)
        return self._webhooks

    def tokens(self) -> Union[CreateResourceEndpoint[CreateAccessTokenCommand, AccessToken],
                              ListResourceEndpoint[AccessToken]]:
        if self._tokens is None:
            self._tokens = AccessTokenEndpoint(
                posixpath.join(self.url, "tokens"), self._client)
        return self._tokens


class AppEndpoint(CreateResourceEndpoint[App, App],
                  ListResourceEndpoint[App],
                  GetResourceEndpoint[App],
                  UpdateResourceEndpoint[App, App],
                  DeleteResourceEndpoint):
    def __init__(self, url: str, client: ApiHttpClient) -> None:
        CreateResourceEndpoint.__init__(
            self, url, client, request_type=App, response_type=App)
        ListResourceEndpoint.__init__(
            self, url, client, response_type=App)
        GetResourceEndpoint.__init__(self, url, client, response_type=App)
        UpdateResourceEndpoint.__init__(
            self, url, client, request_type=App, response_type=App)
        DeleteResourceEndpoint.__init__(self, url, client)


class Api:
    def __init__(self, client: ApiHttpClient) -> None:
        self.apps = AppEndpoint("admin/apps", client)
        self.releases: Union[GetResourceEndpoint[Release],
                             DeleteResourceEndpoint] = ReleaseEndpoint("admin/releases", client)
        self.assets: Union[GetResourceEndpoint[Asset],
                           DeleteResourceEndpoint] = AssetEndpoint("admin/assets", client)
        self.access_tokens = AccessTokenEndpoint("admin/access-tokens", client)
        self.webhooks: Union[GetResourceEndpoint[AccessToken],
                             DeleteResourceEndpoint] = WebhookEndpoint("admin/webhooks", client)
