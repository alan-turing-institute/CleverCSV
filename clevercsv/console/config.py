# -*- coding: utf-8 -*-

"""
CleverCSV Command line application config.

We overwrite the default Cleo Config because we want to simplify the UI.

"""
from cleo.io import ConsoleIO

from clikit.api.args.format.argument import Argument
from clikit.api.args.format.option import Option
from clikit.api.config.application_config import ApplicationConfig
from clikit.api.event import ConsoleEvents
from clikit.api.io import Input, Output
from clikit.api.io.flags import VERBOSE
from clikit.api.resolver import ResolvedCommand
from clikit.formatter import AnsiFormatter, DefaultStyleSet, PlainFormatter
from clikit.handler.help import HelpTextHandler
from clikit.io.input_stream import StandardInputStream
from clikit.io.output_stream import ErrorOutputStream, StandardOutputStream
from clikit.resolver.default_resolver import DefaultResolver
from clikit.resolver.help_resolver import HelpResolver
from clikit.ui.components import NameVersion

from ._flags import INTERACT_NONE, INTERACT_NECESSARY, INTERACT_CONFIRM


class Config(ApplicationConfig):
    def configure(self):
        super(Config, self).configure()

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

        self.add_option("ansi", None, Option.NO_VALUE, "Force ANSI output")
        self.add_option(
            "no-ansi", None, Option.NO_VALUE, "Disable ANSI output"
        )
        self.add_option(
            "interactive",
            "i",
            Option.OPTIONAL_VALUE,
            "Allow interaction: "
            '"-i" only interact when needed, '
            '"-ii" always interact for confirmation',
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

        if args.has_token("--no-ansi"):
            output_formatter = error_formatter = PlainFormatter(style_set)
        elif args.has_token("--ansi"):
            output_formatter = error_formatter = AnsiFormatter(style_set, True)
        else:
            if output_stream.supports_ansi():
                output_formatter = AnsiFormatter(style_set)
            else:
                output_formatter = PlainFormatter(style_set)

            if error_stream.supports_ansi():
                error_formatter = AnsiFormatter(style_set)
            else:
                error_formatter = PlainFormatter(style_set)

        # output_formatter = error_formatter = PlainFormatter(style_set)

        io = self.io_class(
            Input(input_stream),
            Output(output_stream, output_formatter),
            Output(error_stream, error_formatter),
        )

        if args.has_token("-v"):
            io.set_verbosity(VERBOSE)

        # could be cleaner to subclass clikit.api.io.Input and implement it
        # similar to verbosity.
        if args.has_token("-ii"):
            io._interactivity = INTERACT_CONFIRM
            io.set_interactive(True)
        elif args.has_token("-i"):
            io._interactivity = INTERACT_NECESSARY
            io.set_interactive(True)
        else:
            io._interactivity = INTERACT_NONE
            io.set_interactive(False)

        return io

    @property
    def io_class(self):
        return ConsoleIO

    @property
    def default_style_set(self):
        return DefaultStyleSet()

    @property
    def default_command_resolver(self):
        return DefaultResolver()

    def resolve_help_command(self, event, event_name, dispatcher):
        args = event.raw_args
        application = event.application

        if args.has_token("-h") or args.has_token("--help"):
            command = application.get_command("help")

            # Enable lenient parsing
            parsed_args = command.parse(args, True)

            event.set_resolved_command(ResolvedCommand(command, parsed_args))
            event.stop_propagation()

    def print_version(self, event, event_name, dispatcher):
        if event.args.is_option_set("version"):
            version = NameVersion(event.command.application.config)
            version.render(event.io)

            event.handled(True)
