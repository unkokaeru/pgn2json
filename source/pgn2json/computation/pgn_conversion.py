"""pgn_conversion.py: Converts PGN files to JSON format."""

import json
from io import StringIO
from os import remove
from pathlib import Path
from tkinter import Tk
from tkinter.filedialog import askopenfilename

import chess
import chess.pgn
from shortuuid import ShortUUID

from . import logger

logger = logger.getChild(__name__)


class PGNConverter:
    """
    Converts a PGN file into a JSON object compatible with the 'chess-study' Obsidian plug-in.

    Attributes
    ----------
    position_flags : dict[str, str]
        Dictionary mapping move types to their respective flags.
    uuid_length : int
        The length of the UUIDs to generate.
    pgn_content : str
        The content of an inputed PGN file.

    Methods
    -------
    convert_to_json() -> dict:
        Converts PGN content into a JSON object.
    """

    def __init__(self, position_flags: dict[str, str], uuid_length: int):
        """
        Constructs the necessary attributes for the PGNConverter object.

        Parameters
        ----------
        position_flags : dict[str, str]
            Dictionary mapping move types to their respective flags.
        uuid_length : int
            The length of the UUIDs to generate.
        """
        self.position_flags = position_flags
        self.uuid_length = uuid_length
        self.pgn_content = self._read_file("Select the PGN file", ".pgn")

    def _read_file(self, user_prompt: str, file_extension: str) -> str:
        """
        Prompts the user for the path of a file, verifying input extension, then reads it.

        Parameters
        ----------
        user_prompt : str
            What to prompt the user to do during file selection.
        file_extension : str
            Expected file extension.

        Returns
        -------
        str
            The content of the selected file.

        Raises
        ------
        ValueError
            Incorrect file type selected.

        Notes
        -----
        Creates and then hides a Tkinter window, which is then used
        to open the file explorer to select a file. This string file
        location is then converted into a Path object and returned,
        after verifying the file's extension type. After this, it
        reads and returns the content of the file. It will then
        remove the read file.
        """
        root = Tk()
        root.withdraw()

        file_path_str = askopenfilename(title=user_prompt)
        file_path_obj = Path(file_path_str)

        if file_path_obj.suffix != file_extension:
            raise ValueError(f"Incorrect file type selected. Expected '{file_extension}'.")

        with open(file_path_obj) as pgn_file:
            file_content = pgn_file.read()

        remove(file_path_obj)
        return file_content

    def _extract_comment(self, node: chess.pgn.GameNode, move: chess.Move) -> str | None:
        """
        Extracts the comment associated with a given move.

        Parameters
        ----------
        node : chess.pgn.GameNode
            The node representing the current position in the game.
        move : chess.Move
            The move for which to extract the comment.

        Returns
        -------
        str or None
            The comment if found, otherwise None.

        Notes
        -----
        This method traverses the variations of a given node until the specified move is found.
        """
        while node.variations:
            next_node = node.variation(0)
            if next_node.move == move:
                return str(next_node.comment).replace("\n", " ") if next_node.comment else None
            node = next_node
        return None

    def _generate_comment(
        self, game_node: chess.pgn.GameNode, move: chess.Move
    ) -> dict[str, str | list[dict[str, str | list[dict[str, str]]]]] | None:
        """
        Generates the comment structure for JSON output.

        Parameters
        ----------
        game_node : chess.pgn.GameNode
            The current game node.
        move : chess.Move
            The move for which to extract the comment.

        Returns
        -------
        dict[str, str | list[dict[str, str | list[dict[str, str]]]]] or None
            The comment structure formatted for JSON output, or None if no comment exists.
        """
        comment = self._extract_comment(game_node, move)
        if comment:
            return {
                "type": "doc",
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": comment,
                            }
                        ],
                    }
                ],
            }
        return None

    def _generate_move_info(
        self,
        board: chess.Board,
        move: chess.Move,
        flags: str,
        before_fen: str,
        after_fen: str,
        game_node: chess.pgn.GameNode,
    ) -> dict:
        """
        Generates the move information to be added to the JSON object.

        Parameters
        ----------
        board : chess.Board
            The chess board object.
        move : chess.Move
            The move to be processed.
        flags : str
            The flags associated with the move.
        before_fen : str
            The FEN string before the move was made.
        after_fen : str
            The FEN string after the move was made.
        game_node : chess.pgn.GameNode
            The node representing the current position in the game.

        Returns
        -------
        dict
            The move information formatted for JSON output.
        """
        piece_moved_obj = board.piece_at(move.from_square)

        if piece_moved_obj is None:
            raise ValueError(
                f"No piece found at {chess.square_name(move.from_square)} for move {move.uci()}."
            )

        piece_moved_str = piece_moved_obj.symbol().lower()
        move_info = {
            "color": "w" if board.turn == chess.BLACK else "b",
            "piece": piece_moved_str,
            "from": chess.square_name(move.from_square),
            "to": chess.square_name(move.to_square),
            "san": board.san(move),
            "flags": flags,
            "lan": move.uci(),
            "before": before_fen,
            "after": after_fen,
            "moveId": ShortUUID().random(length=self.uuid_length),
            "variants": [],
            "shapes": [],
            "comment": self._generate_comment(game_node, move),
        }

        if "c" in flags:
            move_info["captured"] = (
                "p"
                if board.is_en_passant(move)
                else (
                    board.piece_at(move.to_square).symbol().lower()  # type: ignore
                    if board.piece_at(move.to_square)
                    else None
                )
            )

        if "p" in flags:
            move_info["promotion"] = move.uci()[-1]

        return move_info

    def _determine_flags(self, board: chess.Board, move: chess.Move) -> str:
        """
        Determines the flags associated with a move.

        Parameters
        ----------
        board : chess.Board
            The chess board object.
        move : chess.Move
            The move to be evaluated.

        Returns
        -------
        str
            The flags associated with the move.
        """
        if board.is_capture(move):
            if board.is_en_passant(move):
                return self.position_flags["en_passant"]
            return self.position_flags["capture"]

        if board.is_kingside_castling(move):
            return self.position_flags["kingside_castling"]

        if board.is_queenside_castling(move):
            return self.position_flags["queenside_castling"]

        if (
            board.piece_type_at(move.from_square) == chess.PAWN
            and abs(move.from_square - move.to_square) == 16
        ):
            return self.position_flags["pawn_push_double"]

        if move.promotion:
            return self.position_flags["promotion"]

        return self.position_flags["normal"]

    def _save_storage_json(self, json_data: dict, storage_path: Path, file_length: int) -> str:
        """
        Saves to a randomly generated N character long ShortUUID-named json file within the path.

        Parameters
        ----------
        json_data : dict
            The json data to save.
        storage_path : Path
            Where to name the storage file.
        file_length : int
            Length of the ShortUUID to generate.

        Returns
        -------
        str
            The UUID of the saved file.
        """
        uuid = ShortUUID().random(length=file_length)

        save_path: Path = (storage_path / (uuid + ".json")).resolve()

        with open(save_path, "w") as json_file:
            json.dump(json_data, json_file, indent=2)

        return uuid

    def convert_to_json(self, storage_path: Path) -> tuple[str, str]:
        """
        Converts PGN content into a JSON object.

        Parameters
        ----------
        storage_path : Path
            The path to the chess-study storage directory.

        Returns
        -------
        tuple[str, str]
            The UUID of the saved file and the game link.
        """
        game = chess.pgn.read_game(StringIO(self.pgn_content))

        if game is None:
            raise ValueError("No game found in the PGN file.")

        game_url = game.headers["Link"]

        title = (
            f"{game.headers['White']} (White, {game.headers['WhiteElo']})"
            f"VS "
            f"{game.headers['Black']} (Black, {game.headers['BlackElo']})"
        )
        json_data = {"version": "0.0.1", "header": {"title": title}, "moves": []}

        board = game.board()

        for node in game.mainline():
            move = node.move

            before_fen = board.fen()
            flags = self._determine_flags(board, move)

            move_info = self._generate_move_info(
                board, move, flags, before_fen, "", game
            )  # Temporarily use "" as the after_fen

            board.push(move)
            move_info["after"] = board.fen()

            json_data["moves"].append(move_info)  # type: ignore

        saved_filename: Path = self._save_storage_json(
            json_data,
            storage_path,
            self.uuid_length,
        )  # type: ignore

        return str(saved_filename), game_url
