import os
from time import time
import logging
import platform

from build_center_client.api.api import AccessFlags, WebhookEvent, WebhookType
from .factory import create_api


initial_access_token_id = "initial"
logger = logging.getLogger("buildcenter.test")


def cmd_test(skip_delete: str = None, **kwargs):
    initial_api = create_api(**kwargs)

    admin_rw_token = initial_api.access_tokens.create(
        enabled=True, access=AccessFlags.ADMIN | AccessFlags.READ | AccessFlags.WRITE,
        description="Global admin read/write token")
    logger.info(
        f"Created global access token {admin_rw_token.id}")

    admin_rw_api_create_args = dict(**kwargs)
    # Avoid duplicate keyword argument
    admin_rw_api_create_args["token"] = admin_rw_token.value
    admin_rw_api = create_api(**admin_rw_api_create_args)

    app = admin_rw_api.apps.create(
        name=f"myapp-{time()}", title=f"My App {(time())}")
    logger.info(f"Created app {app.id}")

    release = app.releases().create(version="1.0.0")
    logger.info(f"Created release {release.id} for app {app.id}")

    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_files", "sample_file.txt"), "rb") as f:
        asset = release.assets().create_with_file(
            "file.txt",
            f,
            tags={"arch": platform.machine(), "os": platform.system()}
        )
        logger.info(f"Created asset {asset.id} for release {release.id}")

    webhook = app.webhooks().create(type=WebhookType.DISCORD,
                                    url="http://localhost:5000/webhook-test",
                                    events=(WebhookEvent.RELEASE_PUBLISHED,
                                            WebhookEvent.PRERELEASE_PUBLISHED))
    logger.info(f"Created webhook {webhook.id} for app {app.id}")

    if not skip_delete:
        for app in admin_rw_api.apps.list():
            app = admin_rw_api.apps.get(app.id)

            for webhook in app.webhooks().list():
                webhook = admin_rw_api.webhooks.get(webhook.id)
                logger.info(f"Deleting webhook {webhook.id} for app {app.id}")
                admin_rw_api.webhooks.delete(webhook.id)

            for release in app.releases().list():
                release = admin_rw_api.releases.get(release.id)

                for asset in release.assets().list():
                    asset = admin_rw_api.assets.get(asset.id)
                    logger.info(
                        f"Deleting asset {asset.id} for release {release.id}")
                    admin_rw_api.assets.delete(asset.id)

                logger.info(f"Deleting release {release.id} for app {app.id}")
                admin_rw_api.releases.delete(release.id)

            for access_token in app.tokens().list():
                access_token = admin_rw_api.access_tokens.get(access_token.id)
                logger.info(
                    f"Deleting access token {access_token.id} for app {app.id}")
                admin_rw_api.access_tokens.delete(access_token.id)

            logger.info(f"Deleting app {app.id}")
            admin_rw_api.apps.delete(app.id)

        for access_token in admin_rw_api.access_tokens.list():
            access_token = admin_rw_api.access_tokens.get(access_token.id)
            if access_token.id != initial_access_token_id:
                logger.info(f"Deleting global access token {access_token.id}")
                initial_api.access_tokens.delete(access_token.id)
