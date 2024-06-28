import os
from nxtools import logging

from ayon_server.addons import BaseServerAddon

from .settings import BatchpublisherSettings, DEFAULT_BATCHPUBLISHER_SETTING


BATCHPUBLISHER_ADDON_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__))
)


class BatchPublisherAddon(BaseServerAddon):
    settings_model = BatchpublisherSettings
    frontend_scopes: dict[str, dict[str, str]] = {"settings": {}}

    def initialize(self):
        logging.info("BatchPublisherAddon INIT")

    async def get_default_settings(self):
        settings_model_cls = self.get_settings_model()
        return settings_model_cls(**DEFAULT_BATCHPUBLISHER_SETTING)

    async def setup(self):
        pass
