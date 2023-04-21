from typing import Any, Dict, IO, Tuple, Union
import requests
from dataclasses import asdict, dataclass
import posixpath
import humps
import re
from enum import Enum
import logging


logger = logging.getLogger("buildcenter.common.http")


def diff_dicts(first: dict, second: dict) -> dict:
    first_items = set(first.items())
    second_items = set(second.items())
    diff_items = second_items.difference(first_items)
    diff = dict(diff_items)
    return diff


def check_response_body_for_error(data: object):
    if not isinstance(data, dict):
        return
    error = data.get("error", None)
    if error:
        message = error.get("message", None)
        if message:
            raise Exception(message)


@dataclass
class ContentType:
    mime: str
    charset: str

    def __init__(self, mime: str, params: dict) -> None:
        self.mime = mime
        self.charset = params.get("charset", "utf-8")

    def parse(line: str):
        parts = line.split(";", 1)
        mime = parts[0]
        if len(parts) > 1:
            params = parts[1].split(",")
            params = dict(map(lambda x: x.strip().split("="), params))
        else:
            params = {}
        return ContentType(mime, params)


def is_same_content_type(first: Union[str, ContentType], second: Union[str, ContentType]) -> bool:
    if first is None != second is None:
        return False
    if first is None and second is None:
        return True
    if isinstance(first, str):
        first = ContentType.parse(first)
    if isinstance(second, str):
        second = ContentType.parse(second)
    return first == second


class ApiHttpClient:
    def __init__(self, base_url: str, token: str = None, proxy_address: str = None) -> None:
        self._base_url = base_url
        self._token = token
        self._proxy_address = proxy_address

    def dict_factory(self, entries):
        def convert(value):
            # Use value of enum object
            if isinstance(value, Enum):
                return value.value
            # Convert all elements of a tuple
            if isinstance(value, tuple):
                return tuple(convert(v) for v in value)
            # Convert all elements of a list
            if isinstance(value, list):
                return [convert(v) for v in value]
            return value
        # Remove "private" properties based on property name prefix
        return dict([(k, convert(v)) for (k, v) in entries if not k.startswith("_")])

    def request(self, method: str, url: str, accept: str, content_type: str = None,
                data: Any = None, files: Dict[str, Tuple[str, IO]] = None,
                out_stream: IO = None) -> any:
        headers = {}
        self._add_authorization_header(headers)
        self._add_accept_header(accept, headers)
        json_data = None
        if files is None:
            content_type = self._add_content_type_header(
                method, content_type, headers)
            if method.upper() in ["POST", "PUT", "PATCH"]:
                data = None if data is None else humps.camelize(
                    asdict(data, dict_factory=self.dict_factory)) if not isinstance(data, dict) else data
                req_is_json = is_same_content_type(
                    content_type, "application/json")
                json_data = data if req_is_json else None
                data = None if req_is_json else data
        url = posixpath.join(self._base_url, url) if re.match(
            "^(https?)?://", url) is None else url
        proxies = None if self._proxy_address is None else {
            "http": f"http://{self._proxy_address}",
            "https": f"https://{self._proxy_address}"
        }
        logger.debug("> %s %s %s", method, url, json_data)
        r = requests.request(method, url, headers=headers,
                             json=json_data, data=data, files=files, proxies=proxies,
                             stream=out_stream is not None)
        logger.debug("< %s", r.content)
        if r.status_code == 400:
            raise Exception("Bad request")
        if r.status_code == 401:
            raise Exception("Unauthorized")
        if r.status_code == 403:
            raise Exception("Forbidden")
        if r.status_code == 404:
            raise Exception("Not found")
        if "Content-Type" in r.headers:
            response_content_type = ContentType.parse(
                r.headers["Content-Type"])
            if response_content_type is not None and accept is not None and not is_same_content_type(response_content_type, accept):
                raise Exception("Received content with unexpected type")
            if out_stream is not None:
                for chunk in r.iter_content(chunk_size=1024*1024):
                    if chunk:
                        out_stream.write(chunk)
                return None
            elif response_content_type.mime == "application/json":
                response_json = r.json()
                check_response_body_for_error(response_json)
                return (humps.decamelize(response_json), r.text)

    def post_with_files(self, url: str, files: Dict[str, Tuple[str, IO]], data: Any = None, accept: str = None) -> str:
        return self.request("POST", url, accept, data=data, files=files)

    def post(self, url: str, data: Any, accept: str = None) -> str:
        return self.request("POST", url, accept, data=data)

    def put(self, url: str, data: Any, accept: str = None) -> str:
        return self.request("PUT", url, accept, data=data)

    def patch(self, url: str, data: Any, accept: str = None) -> str:
        return self.request("PATCH", url, accept, data=data)

    def get(self, url: str, accept: str = None, out_stream: IO = None) -> str:
        return self.request("GET", url, accept, out_stream=out_stream)

    def delete(self, url: str, accept: str = None) -> None:
        self.request("DELETE", url, accept)

    def _add_authorization_header(self, headers: dict):
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"

    def _add_accept_header(self, accept, headers: dict):
        headers["Accept"] = "application/json" if accept is None else accept

    def _add_content_type_header(self, method: str, content_type: str, headers: dict):
        if method.upper() in ["POST", "PUT", "PATCH"]:
            content_type = "application/json" if content_type is None else content_type
            headers["Content-Type"] = content_type
            return content_type
        return None
