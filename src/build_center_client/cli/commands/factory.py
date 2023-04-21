from build_center_client.api.api import Api
from build_center_client.api.http import ApiHttpClient


def create_api(server: str, token: str, proxy: str = None, **kwargs):
    return Api(ApiHttpClient(server, token=token, proxy_address=proxy))


def call_cmd_factory(type_, method: str, server: str, token: str, proxy: str, **kwargs):
    return getattr(type_(create_api(server, token, proxy=proxy)), method)(**kwargs)


def create_cmd_factory(type_, method: str):
    # Here we can strip away parameters that we don't want passed down, such as "func" that comes from argparse
    return lambda server, token, proxy, log, func, **kwargs: \
        call_cmd_factory(type_, method, server, token, proxy, **kwargs)
