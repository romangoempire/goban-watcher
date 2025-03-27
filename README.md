# Goban Watcher


## Prerequisites

1. Install and use `Python 3.12.8`.
2. Install requirements with `pip install -r requirements.txt`.
3. Install KataGo. Check if `katago` command works. If not check official [KataGo](https://github.com/lightvector/KataGo) repo.
4. Install a KataGo model from [here](https://katagotraining.org/networks/). During development a model with the architecture of `b28c512nbt` was used.
    1. Rename the model file to `b28c512nbt.bin.gz` 
    2. Move it into `katago/models/`.
    3. Validate that this command works:
        ```shell
        katago analysis -config "katago/configs/analysis_example.cfg" -model "katago/models/b28c512nbt.bin.gz"
        ```
5. To change the camera edit the index in `cap = cv2.VideoCapture(0)` in `main.py`.
6. To start the application run: `python3 main.py`
