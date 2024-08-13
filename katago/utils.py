import json
from re import L


def dict_to_oneliner_string(data: dict) -> str:
    return json.dumps(data).replace("\n", "") + "\n"


def format_raw_string(string_data: str) -> list[dict]:
    splitted_data = string_data.split("info ")[1:]
    moves = [move.strip().split(" ") for move in splitted_data]
    keys = [
        "move",
        "visits",
        "utility",
        "winrate",
        "scoreMean",
        "scoreStdev",
        "scoreLead",
        "scoreSelfplay",
        "prior",
        "lcb",
        "utilityLcb",
        "weight",
    ]

    optional_keys = [
        "isSymmetryOf",
        "order",
        "pv",
    ]
    data = []
    for move in moves:
        result = {}
        for i, key in zip(range(1, 24, 2), keys):
            result[key] = move[i]

        if move[24] == "isSymmetryOf":
            result["isSymmetryOf"] = move[25]
            result["order"] = move[27]
            result["pv"] = move[29:]
        else:
            result["order"] = move[25]
            result["pv"] = move[27:]

        data.append(result)

    return data
