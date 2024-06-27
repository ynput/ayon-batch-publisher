import os

import pyblish.api

from ayon_core.host import HostBase, IPublishHost


ROOT_DIR = os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)
))


class BatchPublisherHost(HostBase, IPublishHost):
    name = "batchpublisher"

    def install(self):
        os.environ["AYON_HOST_NAME"] = self.name

        pyblish.api.register_host("batchpublisher")
