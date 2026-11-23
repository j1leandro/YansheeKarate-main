#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import time
import YanAPI

ARQUIVO_POSES = "poses.json"

SERVOS_PERNAS = [
    "RightHipLR", "RightHipFB", "RightKneeFlex", "RightAnkleFB", "RightAnkleUD",
    "LeftHipLR", "LeftHipFB", "LeftKneeFlex", "LeftAnkleFB", "LeftAnkleUD"
]

SERVOS_BRACOS = [
    "RightShoulderRoll", "RightShoulderFlex", "RightElbowFlex",
    "LeftShoulderRoll", "LeftShoulderFlex", "LeftElbowFlex"
]

TODOS_SERVOS = SERVOS_PERNAS + SERVOS_BRACOS + ["NeckLR"]


def carregar_poses():
    if not os.path.exists(ARQUIVO_POSES):
        return {}
    with open(ARQUIVO_POSES, "r") as f:
        return json.load(f)


def salvar_poses(poses):
    with open(ARQUIVO_POSES, "w") as f:
        json.dump(poses, f, indent=4, sort_keys=True)


def capturar_pose():
    YanAPI.set_servos_mode("program", SERVOS_PERNAS)
    print("\n[ETAPA 1] PERNAS SOLTAS (segure o tronco do robo).")
    input("Posicione as pernas na base da defesa e pressione ENTER...")
    YanAPI.set_servos_mode("work", SERVOS_PERNAS)
    time.sleep(0.5)

    YanAPI.set_servos_mode("program", SERVOS_BRACOS)
    print("\n[ETAPA 2] PERNAS TRAVADAS | BRACOS SOLTOS.")
    input("Posicione os bracos na defesa e pressione ENTER para gravar...")

    res = YanAPI.get_servos_angles(TODOS_SERVOS)
    YanAPI.set_servos_mode("work", TODOS_SERVOS)

    if res.get("code") != 0:
        print("Erro ao ler servos: {}".format(res.get("msg")))
        return None
    return res["data"]


def main():
    YanAPI.yan_api_init("127.0.0.1")
    YanAPI.sync_play_motion(name="Reset")
    poses = carregar_poses()

    try:
        while True:
            print("\n=== GRAVADOR DE POSES ===")
            print("1 - Gravar nova pose (pernas + bracos)")
            print("2 - Testar pose salva")
            print("3 - Listar poses salvas")
            print("4 - Resetar robo")
            print("0 - Sair")
            opcao = input("Escolha: ").strip()

            if opcao == "1":
                nome = input("Nome da pose (ex: gedan_barai_esq): ").strip()
                if not nome:
                    continue
                angulos = capturar_pose()
                if angulos:
                    poses[nome] = angulos
                    salvar_poses(poses)
                    print("Pose '{}' salva em {}.".format(nome, ARQUIVO_POSES))

            elif opcao == "2":
                if not poses:
                    print("Nenhuma pose salva.")
                    continue
                print("Poses: {}".format(", ".join(sorted(poses.keys()))))
                nome = input("Nome da pose para testar: ").strip()
                if nome in poses:
                    YanAPI.sync_play_motion(name="Reset")
                    time.sleep(1)
                    YanAPI.sync_set_servo_rotate(poses[nome], runtime=1200)
                    print("Pose '{}' executada.".format(nome))
                else:
                    print("Pose nao encontrada.")

            elif opcao == "3":
                print("Poses salvas: {}".format(sorted(poses.keys())))

            elif opcao == "4":
                YanAPI.sync_play_motion(name="Reset")

            elif opcao == "0":
                break
    finally:
        YanAPI.set_servos_mode("work", TODOS_SERVOS)


if __name__ == "__main__":
    main()