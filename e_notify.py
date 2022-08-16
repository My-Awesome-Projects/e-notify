#!/usr/bin/python
from src.logger import get_logger
import configparser as cp
import argparse
import src.notify as notify
import os

logger = get_logger()
conf = cp.ConfigParser()


def config_target(args):

    for conf_key in conf._sections:
        for section_key in conf[conf_key]:
            if getattr(args, section_key) is not None:
                conf[conf_key][section_key] = getattr(args, section_key)
                args.logger.debug(
                    f"Changed the configuration pair : {section_key} = {getattr(args, section_key)}"
                )

    with open("conf.ini", "w") as conf_fp:
        conf.write(conf_fp)


def notify_target(args):

    # Make sure the process exists first
    try:
        os.kill(args.pid, 0)
    except ProcessLookupError:
        raise ProcessLookupError(f"The Process with PID : {args.pid} does not exist")

    notify(args)


if __name__ == "__main__":
    # Read the configuration files
    conf.read("conf.ini")

    # Instantiate the main parser and subparsers
    parser = argparse.ArgumentParser("E-mail notifier")
    subparser = parser.add_subparsers(help="Utilities")

    # parser for config
    conf_parser = subparser.add_parser(
        "config", help="Command line utility to modify the config file"
    )

    for conf_key in conf._sections:
        for section_key in conf[conf_key]:
            conf_parser.add_argument(f"--{section_key}")

    conf_parser.set_defaults(func=config_target)

    # parser for notify
    notif_parser = subparser.add_parser(
        "notify", help="notifier, which is the main utility of the program"
    )
    notif_parser.add_argument(
        "--pid", type=int, dest="pid", required=True, help="PID of the process to watch"
    )
    notif_parser.add_argument(
        "--attach",
        type=str,
        dest="attachments",
        help="File to attach to the mail once the process has terminated",
    )

    # TODO : Check the mail address with a regex
    recipients = notif_parser.add_mutually_exclusive_group()
    recipients.add_argument(
        "--to",
        type=str,
        dest="to",
        nargs="*",
        help="Receiver(s) of the mail, must be a valid e-mail address",
    )
    recipients.add_argument(
        "--destlist",
        type=argparse.FileType("r"),
        dest="destlist",
        help="File containing a list of receivers, ONE PER LINE",
    )
    notif_parser.set_defaults(func=notify_target)

    # Call the default function for the subcommand
    args = parser.parse_args()

    # Checks that one of the [config, notify] options was used
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()
