from time import sleep_ms
from encoder import Encoder
from uosc.client import Client


UPDATE_DELAY = const(50)
OSC_SERVER = '192.168.42.151'
OSC_PORT = const(12101)
OSC_TOPIC = '/midi'
MIDI_CC = const(7)


def main():
    enc = Encoder(pin_clk=12, pin_dt=14, clicks=4, accel=5, max_val=127)
    osc = Client(OSC_SERVER, OSC_PORT)

    oldval = 0
    try:
        while True:
            val = enc.value
            if oldval != val:
                oldval = val

                osc.send(OSC_TOPIC, ('m', (0, 0xB0, MIDI_CC, val)))

            enc.cur_accel = max(0, enc.cur_accel - enc.accel)
            sleep_ms(UPDATE_DELAY)
    except Exception as exc:
        enc.close()
        print(exc)


if __name__ == '__main__':
    main()
