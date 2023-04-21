import sys
import os
import argparse

from commands.actions import FileArg, FileInputAction, FileOutputAction, \
    StoreKeyValueAction, WebhookEventsAction, WebhookTypeAction
from commands.commands import AccessTokenCommands, AppCommands, AssetCommands, \
    ReleaseCommands, WebhookCommands
from commands.factory import create_cmd_factory
from commands.setup import cmd_setup
from commands.test import cmd_test


local_server_url = "http://localhost:5000"


def setup_apps_parser(root_subparsers):
    parser = root_subparsers.add_parser("apps")
    parser.set_defaults(func=lambda **kwargs: parser.print_help())
    subparsers = parser.add_subparsers(help="sub-commands")

    create_parser = subparsers.add_parser("create")
    create_parser.add_argument("name")
    create_parser.add_argument("--title", required=True)
    create_parser.add_argument("--description")
    create_parser.add_argument("--public", action="store_true")
    create_parser.set_defaults(func=create_cmd_factory(AppCommands, "create"))

    list_parser = subparsers.add_parser("ls")
    list_parser.set_defaults(func=create_cmd_factory(AppCommands, "list"))

    get_parser = subparsers.add_parser("get")
    get_parser.add_argument("id")
    get_parser.set_defaults(func=create_cmd_factory(AppCommands, "get"))

    update_parser = subparsers.add_parser("update")
    update_parser.add_argument(
        "--infile", action=FileInputAction, default=FileArg(sys.stdin.buffer))
    update_parser.set_defaults(func=create_cmd_factory(AppCommands, "update"))

    remove_parser = subparsers.add_parser("rm")
    remove_parser.add_argument("id")
    remove_parser.set_defaults(func=create_cmd_factory(AppCommands, "remove"))


def setup_releases_parser(root_subparsers):
    parser = root_subparsers.add_parser("releases")
    parser.set_defaults(func=lambda **kwargs: parser.print_help())
    subparsers = parser.add_subparsers(help="sub-commands")

    create_parser = subparsers.add_parser("create")
    create_parser.add_argument("version")
    create_parser.add_argument("--app", help="app identifier", required=True)
    create_parser.add_argument("--title")
    create_parser.add_argument("--description")
    create_parser.add_argument("--commit")
    create_parser.set_defaults(
        func=create_cmd_factory(ReleaseCommands, "create"))

    list_parser = subparsers.add_parser("ls")
    list_parser.add_argument("--app", help="app identifier", required=True)
    list_parser.set_defaults(func=create_cmd_factory(ReleaseCommands, "list"))

    get_parser = subparsers.add_parser("get")
    get_parser.add_argument("id")
    get_parser.set_defaults(func=create_cmd_factory(ReleaseCommands, "get"))

    update_parser = subparsers.add_parser("update")
    update_parser.add_argument(
        "--infile", action=FileInputAction, default=FileArg(sys.stdin.buffer))
    update_parser.set_defaults(
        func=create_cmd_factory(ReleaseCommands, "update"))

    remove_parser = subparsers.add_parser("rm")
    remove_parser.add_argument("id")
    remove_parser.set_defaults(
        func=create_cmd_factory(ReleaseCommands, "remove"))


def setup_assets_parser(root_subparsers):
    parser = root_subparsers.add_parser("assets")
    parser.set_defaults(func=lambda **kwargs: parser.print_help())
    subparsers = parser.add_subparsers(help="sub-commands")

    create_parser = subparsers.add_parser("create")
    create_parser.add_argument(
        "file", action=FileInputAction, default=FileArg(sys.stdin.buffer))
    create_parser.add_argument(
        "--release", help="release identifier", required=True)
    create_parser.add_argument("--name")
    create_parser.add_argument(
        "--tag", default=dict(), action=StoreKeyValueAction)
    create_parser.set_defaults(
        func=create_cmd_factory(AssetCommands, "create"))

    list_parser = subparsers.add_parser("ls")
    list_parser.add_argument("--release", help="release identifier",
                             required=True)
    list_parser.set_defaults(func=create_cmd_factory(AssetCommands, "list"))

    get_parser = subparsers.add_parser("get")
    get_parser.add_argument("id")
    get_parser.set_defaults(func=create_cmd_factory(AssetCommands, "get"))

    remove_parser = subparsers.add_parser("rm")
    remove_parser.add_argument("id")
    remove_parser.set_defaults(
        func=create_cmd_factory(AssetCommands, "remove"))

    download_parser = subparsers.add_parser("download")
    download_parser.add_argument("id")
    download_parser.add_argument(
        "--out", action=FileOutputAction, default=FileArg(sys.stdout.buffer))
    download_parser.set_defaults(
        func=create_cmd_factory(AssetCommands, "download"))


def setup_access_token_parser(root_subparsers):
    parser = root_subparsers.add_parser("tokens")
    parser.set_defaults(func=lambda **kwargs: parser.print_help())
    subparsers = parser.add_subparsers(help="sub-commands")

    create_parser = subparsers.add_parser("create")
    create_parser.add_argument("--app", help="app identifier")
    create_parser.add_argument("--description")
    create_parser.add_argument("--validity-duration")
    create_parser.add_argument("--enabled", action="store_true")
    create_parser.add_argument("--access", required=True, type=int)
    create_parser.set_defaults(
        func=create_cmd_factory(AccessTokenCommands, "create"))

    list_parser = subparsers.add_parser("ls")
    list_parser.add_argument("--app", help="app identifier")
    list_parser.set_defaults(
        func=create_cmd_factory(AccessTokenCommands, "list"))

    get_parser = subparsers.add_parser("get")
    get_parser.add_argument("id")
    get_parser.set_defaults(
        func=create_cmd_factory(AccessTokenCommands, "get"))

    remove_parser = subparsers.add_parser("rm")
    remove_parser.add_argument("id")
    remove_parser.set_defaults(
        func=create_cmd_factory(AccessTokenCommands, "remove"))


def setup_webhook_parser(root_subparsers):
    parser = root_subparsers.add_parser("webhooks")
    parser.set_defaults(func=lambda **kwargs: parser.print_help())
    subparsers = parser.add_subparsers(help="sub-commands")

    create_parser = subparsers.add_parser("create")
    create_parser.add_argument("--app", help="app identifier")
    create_parser.add_argument(
        "--type", required=True, action=WebhookTypeAction)
    create_parser.add_argument("--url", required=True)
    create_parser.add_argument(
        "--events", required=True, action=WebhookEventsAction)
    create_parser.set_defaults(
        func=create_cmd_factory(WebhookCommands, "create"))

    list_parser = subparsers.add_parser("ls")
    list_parser.add_argument("--app", help="app identifier", required=True)
    list_parser.set_defaults(func=create_cmd_factory(WebhookCommands, "list"))

    get_parser = subparsers.add_parser("get")
    get_parser.add_argument("id")
    get_parser.set_defaults(func=create_cmd_factory(WebhookCommands, "get"))

    remove_parser = subparsers.add_parser("rm")
    remove_parser.add_argument("id")
    remove_parser.set_defaults(
        func=create_cmd_factory(WebhookCommands, "remove"))


def setup_root_parser():
    root_parser = argparse.ArgumentParser(
        description="Python client for Build Center API")
    root_parser.add_argument(
        "--log", help="log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
    root_parser.add_argument(
        "--server", help="Server URL, alternatively set with environment variable BC_SERVER",
        default=os.environ.get("BC_SERVER", local_server_url))
    root_parser.add_argument(
        "--proxy", help="proxy server address (host:port)")
    root_parser.add_argument(
        "--token", help="API access token, alternatively set with environment variable BC_TOKEN",
        default=os.environ.get("BC_TOKEN", None))
    root_parser.set_defaults(func=lambda **kwargs: root_parser.print_help())

    root_subparsers = root_parser.add_subparsers(help="sub-commands")

    setup_parser = root_subparsers.add_parser("setup")
    setup_parser.set_defaults(func=cmd_setup)

    test_parser = root_subparsers.add_parser("test")
    test_parser.set_defaults(func=cmd_test)
    test_parser.add_argument("--skip-delete", help="skip deleting resources upon completion",
                             action="store_true")

    setup_apps_parser(root_subparsers)
    setup_releases_parser(root_subparsers)
    setup_assets_parser(root_subparsers)
    setup_access_token_parser(root_subparsers)
    setup_webhook_parser(root_subparsers)

    return root_parser


def parse_args():
    parser = setup_root_parser()
    args = parser.parse_args()
    return args
