from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from katago.katago_analyse import KataGo


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
    return katago.analyse(await data.json())
