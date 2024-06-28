from ayon_core.addon import click_wrap

from ayon_core.addon import AYONAddon, IHostAddon, ITrayAction
from ayon_core.lib import get_ayon_launcher_args
from ayon_core.lib.execute import run_detached_process


class BatchPublisherAddon(AYONAddon, IHostAddon, ITrayAction):
    label = "Batch Publisher"
    name = "batchpublisher"
    host_name = "batchpublisher"

    def initialize(self, modules_settings):
        # UI which must not be created at this time
        self._dialog = None

    def tray_init(self):
        return

    def on_action_trigger(self):
        self.run_batchpublisher()

    def cli(self, click_group):
        click_group.add_command(cli_main.to_click_obj())

    def run_batchpublisher(self):
        args = get_ayon_launcher_args(
            "addon", self.name, "launch"
        )
        run_detached_process(args)


@click_wrap.group(
    BatchPublisherAddon.name, help="BatchPublisher related commands.")
def cli_main():
    pass


@cli_main.command()
def launch():
    """Launch BatchPublisher tool UI."""
    print("LAUNCHING BATCH PUBLISHER")
    from ayon_batchpublisher import ui

    ui.main()
