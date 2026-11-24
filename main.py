import sys
import time
from smbus2 import SMBus
import RPi.GPIO as GPIO
import YanAPI
from movimentos import carregar_poses, sequencia_defesa
from processador import executar_sequencia_poses, resetar_robo

I2C_BUS = 1
OLED_ADDR = 0x3C
MODELO_OLED = "SSD1306"

LED_R = 6
LED_G = 13
LED_B = 16

KEY1 = 5
KEY2 = 4


class TelaOLED(object):
    def __init__(self, modelo=MODELO_OLED):
        self.modelo = modelo
        self.deslocamento = 2 if modelo == "SH1106" else 0
        self.buffer = bytearray(128 * 8)
        self.bus = SMBus(I2C_BUS)
        self._inicializar()

    def _comando(self, comandos):
        for valor in comandos:
            self.bus.write_byte_data(OLED_ADDR, 0x00, valor)

    def _inicializar(self):
        comandos = [0xAE, 0xD5, 0x80, 0xA8, 0x3F, 0xD3, 0x00, 0x40]
        if self.modelo == "SSD1306":
            comandos += [0x8D, 0x14, 0x20, 0x02]
        else:
            comandos += [0xAD, 0x8B]
        comandos += [
            0xA1, 0xC8, 0xDA, 0x12, 0x81, 0xCF, 0xD9,
            0xF1 if self.modelo == "SSD1306" else 0x22,
            0xDB, 0x40, 0xA4, 0xA6, 0xAF
        ]
        self._comando(comandos)
        time.sleep(0.1)

    def limpar(self):
        self.buffer = bytearray(128 * 8)

    def pixel(self, x, y, cor=1):
        if 0 <= x < 128 and 0 <= y < 64:
            idx = x + (y // 8) * 128
            if cor:
                self.buffer[idx] |= (1 << (y % 8))
            else:
                self.buffer[idx] &= ~(1 << (y % 8))

    def retangulo(self, x, y, w, h, cor=1):
        for px in range(x, x + w):
            for py in range(y, y + h):
                self.pixel(px, py, cor)

    def linha(self, x0, y0, x1, y1, espessura=1):
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.retangulo(x0, y0, espessura, espessura, 1)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def atualizar(self):
        for pagina in range(8):
            self._comando([
                0xB0 + pagina,
                self.deslocamento & 0x0F,
                0x10 | (self.deslocamento >> 4)
            ])
            base = pagina * 128
            for inicio in range(0, 128, 16):
                dados = list(self.buffer[base + inicio:base + inicio + 16])
                self.bus.write_i2c_block_data(OLED_ADDR, 0x40, dados)

    def mostrar_rosto(self, expressao):
        self.limpar()
        if expressao == "feliz":
            self.retangulo(34, 14, 14, 14)
            self.retangulo(80, 14, 14, 14)
            for x in range(42, 87):
                dx = (x - 64) / 22.0
                y = int(50 - (dx * dx) * 10)
                self.retangulo(x, y, 2, 3)

        elif expressao == "mal":
            self.linha(26, 12, 52, 22, 3)
            self.linha(102, 12, 76, 22, 3)
            self.retangulo(36, 22, 12, 10)
            self.retangulo(80, 22, 12, 10)
            self.linha(44, 48, 84, 48, 3)

        elif expressao == "kiai":
            self.linha(24, 10, 54, 22, 4)
            self.linha(104, 10, 74, 22, 4)
            self.retangulo(36, 22, 12, 8)
            self.retangulo(80, 22, 12, 8)
            self.retangulo(44, 38, 40, 20, 1)
            self.retangulo(50, 42, 28, 12, 0)

        self.atualizar()

    def fechar(self):
        self.limpar()
        self.atualizar()
        self.bus.close()


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
    tela = TelaOLED()

    try:
        set_led(1, 0, 0)
        resetar_robo(tela)
        set_led(0, 1, 0)
        print("Pronto! KEY1 = Iniciar | KEY2 = Parar e Reset | Ctrl+C = Sair")

        while True:
            if botao_pressionado(KEY1):
                set_led(0, 0, 1)
                concluido = executar_sequencia_poses(
                    sequencia_defesa,
                    poses,
                    verificar_parada=lambda: botao_pressionado(KEY2),
                    tela=tela
                )
                if not concluido:
                    set_led(0, 1, 0)
            elif botao_pressionado(KEY2):
                set_led(1, 0, 0)
                resetar_robo(tela)
                set_led(0, 1, 0)
            time.sleep(0.02)

    except KeyboardInterrupt:
        print("\nEncerrando...")
    finally:
        tela.fechar()
        set_led(0, 0, 0)
        GPIO.cleanup()


if __name__ == "__main__":
    main()