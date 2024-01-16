# PGN to JSON Conversion Script

## Overview
`pgn2json.py` is a Python script designed to convert Portable Game Notation (PGN) files into JSON format. The primary purpose of this conversion is to facilitate the integration of chess game data with the 'chess-study' plugin for Obsidian. This script utilizes several libraries to parse PGN files and generate structured JSON data, making it easier to study and analyze chess games within the Obsidian environment.

## Features
- Parses PGN files and converts them into a JSON structure.
- Extracts key information from the PGN files, including player names, ELO ratings, moves, comments, and flags.
- Generates unique identifiers for each move, aiding in individual move analysis.
- Supports various flags for chess moves, such as capture, en passant, castling, pawn double move, and promotion.
- Automatically handles file operations for reading PGN files and saving the corresponding JSON output.

## Requirements
- Python 3.x
- Libraries: `chess`, `io`, `json`, `shortuuid`, `os`, `typing`

## Installation
Ensure Python 3 and the necessary libraries are installed on your system. Clone or download the script from the repository, and place it in your desired directory.

## Usage
1. Store the PGN files in the designated directory (default: `C:\Users\wills\Downloads`).
2. Run the script. It will automatically find and process all `.pgn` files in the specified directory.
3. The script converts each PGN file into a JSON file, saving them in the specified storage location (default: `C:\Users\wills\Documents\GitHub\digital-garden\content\.obsidian\plugins\chess-study\storage`).
4. Once the conversion is complete, the script provides a `chessStudyId` for each converted file, which can be used in the 'chess-study' plugin.
5. The original PGN files are deleted after conversion.

## Configuration
- `SAV_LOC`: The save location for JSON files.
- `PGN_LOC`: The location where PGN files are stored.
- `POS_FLAGS`: Dictionary of flags for various chess moves.

## Note
The script is configured with specific file paths for PGN and JSON storage locations. Modify these paths in the `main()` function to suit your directory structure.

## License
Specify the license under which the script is distributed.

## Author
William Fayers, unkokaeru
