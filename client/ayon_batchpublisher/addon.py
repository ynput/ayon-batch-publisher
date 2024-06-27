from ayon_core.addon import click_wrap

from ayon_core.addon import AYONAddon, IHostAddon, ITrayAction


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
        self.show_dialog()

    def cli(self, click_group):
        click_group.add_command(cli_main)

    def _create_dialog(self):
        # # Don't recreate dialog if already exists
        # if self._dialog is not None:
        #     return

        from importlib import reload

        import ayon_batchpublisher.controller
        import ayon_batchpublisher.ui.batch_publisher_model
        import ayon_batchpublisher.ui.batch_publisher_delegate
        import ayon_batchpublisher.ui.batch_publisher_view
        import ayon_batchpublisher.ui.window

        # TODO: These lines are only for testing current branch
        reload(ayon_batchpublisher.controller)
        reload(ayon_batchpublisher.ui.batch_publisher_model)
        reload(
            ayon_batchpublisher.ui.batch_publisher_delegate)
        reload(ayon_batchpublisher.ui.batch_publisher_view)
        reload(ayon_batchpublisher.ui.window)

        self._dialog = ayon_batchpublisher.ui.window. \
            BatchPublisherWindow()

    def show_dialog(self):
        """Show dialog with connected modules.
        This can be called from anywhere but can also crash in headless mode.
        There is no way to prevent addon to do invalid operations if he's
        not handling them.
        """
        # Make sure dialog is created
        self._create_dialog()
        # Show dialog
        self._dialog.show()


@click_wrap.group(
    BatchPublisherAddon.name, help="BatchPublisher related commands.")
def cli_main():
    pass


@cli_main.command()
def launch():
    """Launch BatchPublisher tool UI."""
    print("LAUNCHING BATCH PUBLISHER")
    from ayon_batchpublisher.ui import window
    window.main()
