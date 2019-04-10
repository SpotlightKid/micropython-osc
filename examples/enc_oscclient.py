from machine import Pin
from time import sleep_ms
from encoder import Encoder
from uosc.client import Client


UPDATE_DELAY = const(50)
OSC_SERVER = '192.168.42.1'
OSC_PORT = const(12101)
OSC_TOPIC = '/midi'
MIDI_CC_ENC = const(7)
MIDI_CC_SW = const(64)
PIN_CLK = const(4)
PIN_DT = const(0)
PIN_SW = const(2)


def main():
    enc = Encoder(pin_clk=PIN_CLK, pin_dt=PIN_DT, clicks=4, accel=5, max_val=127)
    osc = Client(OSC_SERVER, OSC_PORT)
    sw = Pin(PIN_SW, Pin.IN, None)

    oldval = 0
    oldsw = 1
    try:
        while True:
            if enc.value != oldval:
                osc.send(OSC_TOPIC, ('m', (0, 0xB0, MIDI_CC_ENC, enc.value)))
                oldval = enc.value

            enc.cur_accel = max(0, enc.cur_accel - enc.accel)

            if sw() != oldsw:
                osc.send(OSC_TOPIC, ('m', (0, 0xB0, MIDI_CC_SW, 0 if sw() else 127)))
                oldsw = sw()

            sleep_ms(UPDATE_DELAY)
    except Exception as exc:
        enc.close()
        print(exc)


if __name__ == '__main__':
    main()
