import json

ARQUIVO_POSES = "poses.json"


def carregar_poses():
    with open(ARQUIVO_POSES, "r") as f:
        return json.load(f)


sequencia_defesa = [
    {
        "nome": "gedan_barai",
        "fator_meio": 0.75,
        "runtime_meio": 1000,
        "runtime_final": 200,
        "pausa": 0.6,
        "tts": None
    },
    {
        "nome": "gedan_barai_2",
        "fator_meio": 0.75,
        "runtime_meio": 1200,
        "runtime_final": 200,
        "pausa": 0.0,
        "tts": "KIAI!"
    }
]

coreografia_heian_shodan = [
    {"movimento": "Reset", "pausa": 2},
    {"movimento": "OneStepTurnLeft", "pausa": 1},
    {"movimento": "LeftTackle", "pausa": 1},
    {"movimento": "OneStepForward", "pausa": 1},
    {"movimento": "RightHitForward", "pausa": 1},
    {"movimento": "TurnRight1", "pausa": 1},
    {"movimento": "RightTackle", "pausa": 1},
    {"movimento": "OneStepForward", "pausa": 1},
    {"movimento": "LeftHitForward", "pausa": 1},
    {"movimento": "OneStepTurnLeft", "pausa": 1},
    {"movimento": "LeftTackle", "pausa": 1},
    {"movimento": "OneStepForward", "pausa": 0.5},
    {"movimento": "RightSidePunch", "pausa": 0.5},
    {"movimento": "OneStepForward", "pausa": 0.5},
    {"movimento": "LeftSidePunch", "pausa": 0.5},
    {"movimento": "OneStepForward", "pausa": 0.5},
    {"movimento": "Fight_RHit", "pausa": 1},
    {"movimento": "TurnLeft1", "pausa": 1},
    {"movimento": "LeftTackle", "pausa": 1},
    {"movimento": "OneStepForward", "pausa": 1},
    {"movimento": "RightHitForward", "pausa": 2},
    {"movimento": "Reset", "pausa": 0}
]