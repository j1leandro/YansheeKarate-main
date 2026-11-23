import sys
import time
import RPi.GPIO as GPIO
import YanAPI
from movimentos import carregar_poses, sequencia_defesa
from processador import executar_sequencia_poses, resetar_robo

LED_R = 6
LED_G = 13
LED_B = 16

KEY1 = 5
KEY2 = 4


def configurar_gpio():
    GPIO.setmode(GPIO.BCM)
    for pino in (LED_R, LED_G, LED_B):
        GPIO.setup(pino, GPIO.OUT, initial=GPIO.LOW)
    for pino in (KEY1, KEY2):
        GPIO.setup(pino, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def set_led(r, g, b):
    GPIO.output(LED_R, r)
    GPIO.output(LED_G, g)
    GPIO.output(LED_B, b)


def botao_pressionado(pino):
    if GPIO.input(pino) == GPIO.LOW:
        time.sleep(0.03)
        if GPIO.input(pino) == GPIO.LOW:
            while GPIO.input(pino) == GPIO.LOW:
                time.sleep(0.02)
            return True
    return False


def main():
    YanAPI.yan_api_init("127.0.0.1")

    if len(sys.argv) > 1 and sys.argv[1] == "gravar":
        import gravar_pose
        gravar_pose.main()
        return

    poses = carregar_poses()
    configurar_gpio()

    try:
        set_led(1, 0, 0)
        resetar_robo()
        set_led(0, 1, 0)
        print("Pronto! KEY1 = Iniciar | KEY2 = Parar e Reset | Ctrl+C = Sair")

        while True:
            if botao_pressionado(KEY1):
                set_led(0, 0, 1)
                concluido = executar_sequencia_poses(
                    sequencia_defesa,
                    poses,
                    verificar_parada=lambda: botao_pressionado(KEY2)
                )
                if not concluido:
                    set_led(0, 1, 0)
            elif botao_pressionado(KEY2):
                set_led(1, 0, 0)
                resetar_robo()
                set_led(0, 1, 0)
            time.sleep(0.02)

    except KeyboardInterrupt:
        print("\nEncerrando...")
    finally:
        set_led(0, 0, 0)
        GPIO.cleanup()


if __name__ == "__main__":
    main()