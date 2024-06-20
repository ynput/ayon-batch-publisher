import os
from nxtools import logging

from ayon_server.addons import BaseServerAddon


BATCHPUBLISHER_ADDON_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__))
)


class BatchPublisherAddon(BaseServerAddon):

    frontend_scopes: dict[str, dict[str, str]] = {"settings": {}}

    def initialize(self):
        logging.info("BatchPublisherAddon INIT")

    async def setup(self):
        pass
