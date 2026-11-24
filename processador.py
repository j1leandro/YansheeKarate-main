import time
import YanAPI


def interpolar_pose(origem, destino, fator):
    pose_meio = {}
    for servo, angulo_final in destino.items():
        angulo_inicial = origem.get(servo, angulo_final)
        pose_meio[servo] = int(round(angulo_inicial + (angulo_final - angulo_inicial) * fator))
    return pose_meio


def aguardar(segundos, verificar_parada=None):
    fim = time.monotonic() + segundos
    while time.monotonic() < fim:
        if verificar_parada and verificar_parada():
            return True
        time.sleep(0.02)
    return False


def resetar_robo(tela=None):
    if tela:
        tela.mostrar_rosto("feliz")
    YanAPI.stop_voice_tts()
    YanAPI.stop_play_motion()
    YanAPI.sync_play_motion(name="Reset")


def executar_sequencia_poses(sequencia, poses, verificar_parada=None, tela=None):
    for passo in sequencia:
        nome = passo["nome"]
        if nome not in poses:
            print("Aviso: Pose '{}' nao encontrada.".format(nome))
            continue

        if tela and passo.get("rosto_inicio"):
            tela.mostrar_rosto(passo["rosto_inicio"])

        destino = poses[nome]
        res_atual = YanAPI.get_servos_angles(list(destino.keys()))
        origem = res_atual["data"] if res_atual.get("code") == 0 else destino

        pose_meio = interpolar_pose(origem, destino, passo["fator_meio"])

        print("Executando {} (equilibrio)...".format(nome))
        YanAPI.set_servos_angles(pose_meio, runtime=passo["runtime_meio"])
        if aguardar(passo["runtime_meio"] / 1000.0, verificar_parada):
            resetar_robo(tela)
            return False

        if tela and passo.get("rosto_final"):
            tela.mostrar_rosto(passo["rosto_final"])

        if passo.get("tts"):
            YanAPI.start_voice_tts(tts=passo["tts"], interrupt=True)

        print("Executando {} (finalizacao)...".format(nome))
        YanAPI.set_servos_angles(destino, runtime=passo["runtime_final"])
        if aguardar(passo["runtime_final"] / 1000.0, verificar_parada):
            resetar_robo(tela)
            return False

        pausa = passo.get("pausa", 0)
        if pausa > 0 and aguardar(pausa, verificar_parada):
            resetar_robo(tela)
            return False

    return True