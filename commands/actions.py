import argparse
import os
import sys
from typing import IO, Any

from api.api import WebhookEvent, WebhookType


class FileArg:
    def __init__(self, io: IO, path: str = None) -> None:
        self._io = io
        self._path = path

    def path(self) -> str:
        return self._path

    def basename(self) -> str:
        return os.path.basename(self._path)

    def io(self) -> IO:
        return self._io


class FileInputAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None) -> Any:
        # TODO: close file
        values = FileArg(
            sys.stdin) if values == "-" or values is None else FileArg(open(values, "rb"), values)
        setattr(namespace, self.dest, values)


class FileOutputAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None) -> Any:
        # TODO: close file
        values = FileArg(
            sys.stdout.buffer) if values == "-" or values is None else FileArg(open(values, "wb"), values)
        setattr(namespace, self.dest, values)


class WebhookTypeAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None) -> Any:
        values = WebhookType(values)
        setattr(namespace, self.dest, values)


class WebhookEventsAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None) -> Any:
        values = tuple(WebhookEvent(v) for v in values.split(","))
        setattr(namespace, self.dest, values)


class StoreKeyValueAction(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super().__init__(option_strings, dest, nargs,  **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        if not hasattr(namespace, self.dest):
            setattr(namespace, self.dest, dict())
        dest_dict = getattr(namespace, self.dest)
        if not isinstance(values, list):
            values = values,
        for kv_line in values:
            kv = kv_line.split("=")
            dest_dict[kv[0]] = None if len(kv) < 2 else kv[1]
