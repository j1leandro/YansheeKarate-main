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
        "tts": None,
        "rosto_inicio": "mal",
        "rosto_final": None
    },
    {
        "nome": "gedan_barai_2",
        "fator_meio": 0.75,
        "runtime_meio": 1200,
        "runtime_final": 200,
        "pausa": 0.0,
        "tts": "KIAI!",
        "rosto_inicio": "mal",
        "rosto_final": "kiai"
    }
]