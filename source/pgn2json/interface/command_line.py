"""command_line.py: Command line interface for the application."""

import logging
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from typing import Any

from ..config.constants import Constants
from . import __version__

logger = logging.getLogger(__name__)


def command_line_interface() -> dict[str, Any]:
    """
    Takes arguments from the command line and returns them as a dictionary.

    Returns
    -------
    dict[str, Any]
        A dictionary containing the arguments passed to the application.
    """
    argparser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter
    )  # Automatically generates help messages

    argparser.add_argument(
        "--log_output_path",
        "-l",
        action="store",
        type=str,
        required=False,
        default=Constants.DEFAULT_LOG_SAVE_PATH,
        help="Path to save the log file, should end in .txt.",
    )  # Path to save the log file

    argparser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        required=False,
        help="Increase logging verbosity.",
    )  # Increase logging verbosity

    argparser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )  # Display the version number

    argparser.add_argument(
        "--save_folder",
        "-s",
        action="store",
        type=str,
        required=False,
        default=Constants.DEFAULT_JSON_SAVE_FOLDER,
        help="Folder to save the JSON files.",
    )  # Folder to save the JSON files

    parsed_args = argparser.parse_args()

    # Create a dictionary to return the parsed arguments
    arguments: dict[str, Any] = {
        "log_output_path": parsed_args.log_output_path,
        "verbose": parsed_args.verbose,
        "save_folder": Constants.DEFAULT_JSON_SAVE_FOLDER,
    }

    logger.debug(f"Arguments: {arguments}")

    return arguments
