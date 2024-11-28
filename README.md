# Goban Watcher

## Tools
- `open_camera.py`: Template to open camera and display the video feed in a window
- `labelling.py`: Script to label data in `images/raw`.
- `sgf_downloader.py`: Downloads sgf and png from [OGS](https://online-go.com)
- `game.py`: Implementation of game logic
- `katago_parser.py`: Add connection Katago endpoint

## Training
- `0_classification.ipynb`: Notebook to classify each intersection
- `1_prediction_corners.ipynb`: Notebook to predict the corners of the board. (Should be used to normalize the board to a topdown view)

## Main Scripts
- `baduk.py`: Working gui using `game.py`
