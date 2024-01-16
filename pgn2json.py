"""A script to convert a PGN into a JSON file for the Obsidian plug-in 'chess-study'."""

# Imports

import chess
import chess.pgn
import io
import json
import shortuuid
import os
import typing


def parse_pgn_to_json(
    pgn: str, POS_FLAGS: dict[str, str]
) -> dict[str, typing.Any] | None:
    """
    Parses a PGN file into a JSON object.
    :param pgn: The PGN file to parse.
    :param POS_FLAGS: The possible move flags in the plug-in.
    :return: The JSON object.
    """

    # Parse the PGN file
    pgn_io = io.StringIO(pgn)
    game = chess.pgn.read_game(pgn_io)

    # Prepare the header for the JSON object
    title = f"{game.headers['White']} (White, {game.headers['WhiteElo']}) VS {game.headers['Black']} (Black, {game.headers['BlackElo']})"
    json_data = {"version": "0.0.1", "header": {"title": title}, "moves": []}

    # Process each move
    board = game.board()
    for move in game.mainline_moves():
        san_move = board.san(move)
        lan_move = move.uci()
        before_fen = board.fen()

        # Get the flags for the move
        flags = POS_FLAGS["normal"]
        if board.is_capture(move):
            if board.is_en_passant(move):
                flags = POS_FLAGS["en_passant"]
            else:
                flags = POS_FLAGS["capture"]
        if board.is_kingside_castling(move):
            flags = POS_FLAGS["kingside_castling"]
        if board.is_queenside_castling(move):
            flags = POS_FLAGS["queenside_castling"]
        if (
            board.piece_type_at(move.from_square) == chess.PAWN
            and abs(move.from_square - move.to_square) == 16
        ):
            flags = POS_FLAGS["pawn_push_double"]
        if move.promotion:
            flags += POS_FLAGS["promotion"]

        # Get the piece that was captured
        if board.is_capture(move):
            if board.is_en_passant(move):
                piece_captured = "p"
            else:
                piece_captured = board.piece_at(move.to_square).symbol().lower()

        # Get the piece that was moved
        piece_moved = board.piece_at(move.from_square).symbol().lower()

        # Make the move on the board
        board.push(move)
        after_fen = board.fen()

        # Add the move to the JSON object, depending on the flags
        if "c" in flags:
            move_info: dict[str, typing.Any] = {
                "color": "b" if board.turn == chess.WHITE else "w",
                "piece": piece_moved,
                "from": chess.square_name(move.from_square),
                "to": chess.square_name(move.to_square),
                "san": san_move,
                "flags": flags,
                "lan": lan_move,
                "before": before_fen,
                "after": after_fen,
                "captured": piece_captured,
                "moveId": shortuuid.ShortUUID().random(length=21),
                "variants": [],
                "shapes": [],
                "comment": {
                    "type": "doc",
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {"type": "text", "text": extract_comment(game, move)}
                            ],
                        }
                    ],
                }
                if extract_comment(game, move)
                else None,
            }
        if "p" in flags:
            move_info = {
                "color": "b" if board.turn == chess.WHITE else "w",
                "piece": piece_moved,
                "from": chess.square_name(move.from_square),
                "to": chess.square_name(move.to_square),
                "san": san_move,
                "flags": flags,
                "lan": lan_move,
                "before": before_fen,
                "after": after_fen,
                "promotion": lan_move[-1],
                "moveId": shortuuid.ShortUUID().random(length=21),
                "variants": [],
                "shapes": [],
                "comment": {
                    "type": "doc",
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {"type": "text", "text": extract_comment(game, move)}
                            ],
                        }
                    ],
                }
                if extract_comment(game, move)
                else None,
            }
        if "c" not in flags and "p" not in flags:
            move_info = {
                "color": "b" if board.turn == chess.WHITE else "w",
                "piece": piece_moved,
                "from": chess.square_name(move.from_square),
                "to": chess.square_name(move.to_square),
                "san": san_move,
                "flags": flags,
                "lan": lan_move,
                "before": before_fen,
                "after": after_fen,
                "moveId": shortuuid.ShortUUID().random(length=21),
                "variants": [],
                "shapes": [],
                "comment": {
                    "type": "doc",
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {"type": "text", "text": extract_comment(game, move)}
                            ],
                        }
                    ],
                }
                if extract_comment(game, move)
                else None,
            }

        json_data["moves"].append(move_info)

    return json_data


def extract_comment(node, move: chess.Move) -> str | None:
    """
    Extracts the comment for a move.
    :param node: The game object.
    :param move: The move to extract the comment for.
    :return: The comment for the move, or None if there is no comment.
    """

    # Iterate through the variations until the move is found
    while node.variations:
        next_node = node.variation(0)
        # If the move is found, return the comment
        if next_node.move == move:
            # Replace newlines with spaces
            return (
                str(next_node.comment).replace("\n", " ") if next_node.comment else None
            )
        node = next_node
    return None


def main() -> None:
    """
    The main function.
    :return: None
    """

    # Constants
    SAV_LOC = "C:\\Users\\wills\\Documents\\GitHub\\digital-garden\\content\\.obsidian\\plugins\\chess-study\\storage\\"
    PGN_LOC = "C:\\Users\\wills\\Downloads\\"
    POS_FLAGS: dict[str, str] = {
        "normal": "n",
        "capture": "c",
        "en_passant": "e",
        "kingside_castling": "k",
        "queenside_castling": "q",
        "pawn_push_double": "b",
        "promotion": "p",
    }

    # Load a list of PGN files (".pgn") from the PGN_LOC directory
    pgn_files: list[str] = [
        f
        for f in os.listdir(PGN_LOC)
        if os.path.isfile(os.path.join(PGN_LOC, f)) and f.endswith(".pgn")
    ]

    # Print the PGN files found
    print("PGN files found:")
    for pgn_file in pgn_files:
        print(f" - {pgn_file}")

    # Convert each PGN file to a JSON file
    print("Corresponding chessStudyIds: ")
    for pgn_file in pgn_files:
        # Load the PGN file and convert it to JSON
        with open(PGN_LOC + pgn_file, "r") as f:
            json_output = parse_pgn_to_json(f.read(), POS_FLAGS)

        # Generate a random file name
        file_name = shortuuid.ShortUUID().random(length=21)

        # Save the JSON file
        with open(SAV_LOC + file_name + ".json", "w") as f:
            json.dump(json_output, f, indent=2)

        # Print the chessStudyId
        print(f"```chessStudy\n chessStudyId: {file_name}\n```\n")

        # Delete the PGN file
        os.remove(PGN_LOC + pgn_file)


if __name__ == "__main__":
    main()
