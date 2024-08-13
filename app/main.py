from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from katago.katago import KataGo, coordinate_to_xy, xy_to_coordinate
from icecream import ic

app = FastAPI()
katago = KataGo(
    "katago",
    "katago/configs/analysis_example.cfg",
    "katago/models/g170-b30c320x2.bin.gz",
)


origins = ["http://localhost", "http://localhost:8000", "null"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/analyse")
async def analyse(data: Request):
    moves = await data.json()
    moves = [[move[0], xy_to_coordinate(move[1], move[2])] for move in moves]
    results = katago.analyse(moves)
    return results
