# -*- coding: utf-8 -*-

"""
CleverCSV Command line application config.

We overwrite the default Cleo Config because we want to simplify the UI.

"""

from cleo.config import ApplicationConfig

from clikit.api.args.format.argument import Argument
from clikit.api.args.format.option import Option
from clikit.api.event import ConsoleEvents
from clikit.api.io import Input
from clikit.api.io import Output
from clikit.api.io.flags import VERBOSE
from clikit.formatter import PlainFormatter
from clikit.handler.help import HelpTextHandler
from clikit.io.input_stream import StandardInputStream
from clikit.io.output_stream import ErrorOutputStream
from clikit.io.output_stream import StandardOutputStream
from clikit.resolver.help_resolver import HelpResolver


class Config(ApplicationConfig):
    def configure(self):
        self.set_io_factory(self.create_io)
        self.add_event_listener(
            ConsoleEvents.PRE_RESOLVE.value, self.resolve_help_command
        )
        self.add_event_listener(
            ConsoleEvents.PRE_HANDLE.value, self.print_version
        )

        self.add_option(
            "help", "h", Option.NO_VALUE, "Display this help message."
        )
        self.add_option(
            "verbose", "v", Option.NO_VALUE, "Enable verbose mode."
        )
        self.add_option(
            "version", "V", Option.NO_VALUE, "Display the application version."
        )

        # added for clevercsv
        self.set_display_name("CleverCSV")
        with self.command("help") as c:
            c.default()
            c.set_description("Display the manual of a command")
            c.add_argument(
                "command",
                Argument.OPTIONAL | Argument.MULTI_VALUED,
                "The command name",
            )
            c.set_handler(HelpTextHandler(HelpResolver()))

    def create_io(
        self,
        application,
        args,
        input_stream=None,
        output_stream=None,
        error_stream=None,
    ):
        if input_stream is None:
            input_stream = StandardInputStream()

        if output_stream is None:
            output_stream = StandardOutputStream()

        if error_stream is None:
            error_stream = ErrorOutputStream()

        style_set = application.config.style_set
        output_formatter = error_formatter = PlainFormatter(style_set)

        io = self.io_class(
            Input(input_stream),
            Output(output_stream, output_formatter),
            Output(error_stream, error_formatter),
        )

        if args.has_token("-v"):
            io.set_verbosity(VERBOSE)

        io.set_interactive(False)
        return io
