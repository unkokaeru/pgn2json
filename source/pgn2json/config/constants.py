"""constants.py: Constants for the application."""

from pathlib import Path
from typing import Literal


class Constants:
    """
    Constants for the application.

    Notes
    -----
    This class contains constants used throughout the application.
    By storing constants in a single location, it is easier to
    manage and update them. Constants should be defined as class
    attributes and should be named in uppercase with underscores
    separating words. Constants should use type hints to indicate
    to the user what type of data they should store.
    """

    # Logging constants
    POSSIBLE_LOGGING_LEVELS = Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]
    LOGGING_LEVEL_LOGFILE_DEFAULT: POSSIBLE_LOGGING_LEVELS = "DEBUG"
    LOGGING_LEVEL_CONSOLE_DEFAULT: POSSIBLE_LOGGING_LEVELS = "INFO"
    LOGGING_LOGFILE_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOGGING_CONSOLE_FORMAT: str = "%(message)s"
    LOGGING_TIMESTAMP_FORMAT: str = "%Y-%m-%d_%H-%M-%S"
    LOGGING_DATE_FORMAT: str = "[%X]"
    LOGGING_TRACEBACKS: bool = True

    # API response constants
    SUCCESS_CODE: int = 200
    SUCCESS_TEXT: str = "OK"
    FORBIDDEN_CODE: int = 403

    # Default values
    DEFAULT_LOG_SAVE_PATH: Path = Path("pgn2json_log.txt")
    DEFAULT_JSON_SAVE_FOLDER: Path = Path(".obsidian/plugins/chess-study/storage/")

    # Chess constants
    POSITION_FLAGS: dict[str, str] = {
        "normal": "n",
        "capture": "c",
        "en_passant": "e",
        "kingside_castling": "k",
        "queenside_castling": "q",
        "pawn_push_double": "b",
        "promotion": "p",
    }
    UUID_LENGTH: int = 21
