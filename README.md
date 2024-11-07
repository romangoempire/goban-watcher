# Goban Watcher



## First tests
- `detection_test.py`: Test few filters on the image to see how they perform
- `movement_detection.py`: A video feed where all unchanged pixels are black and changed pixels are white

## Tools
- `open_camera.py`: Template to open camera and display the video feed in a window
- `labelling.py`: Script to label data in `images/raw`.
- `sgf_downloader.py`: Downloads sgf and png from [OGS](https://online-go.com)


## Training
- `0_classification.ipynb`: Notebook to classify each intersection
- `src/1_predcition_corners.ipynb`: Notebook to predict the corners of the board. (Should be used to normalize the board to a topdown view)