#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Show a grid of buttons, which send MIDI program change messages via OSC.

This is intended to run under Pythonista, a Python environment for iOS.

It could be easily made to run with other GUI toolkits, either via a
compability wrapper for Pythonista's 'ui' module or by re-implementing the
GUI parts of the code.

"""


from __future__ import print_function

import logging
import ui

from uosc.threadedclient import ThreadedClient


log = logging.getLogger("oscpanel")

OSC_HOST = '192.168.42.151'
OSC_PORT = 12101
NCOLS = 5
NROWS = 7
OFFSET = 16
XSPACING = 16
YSPACING = 16
BWIDTH = 184
BHEIGHT = 80
BCOLOR = 1.00, 1.00, 0.00
BFONT = 'DINAlternate-Bold'
BFONTSIZE = 20
BFONTCOLOR = 0.50, 0.00, 0.25

ICONS = {
    'osc_active': ui.Image.named('ionicons-social-rss-24'),
    'osc_inactive': ui.Image.named('ionicons-social-rss-outline-24'),
}


def contains(box, pos):
    # Touch coordinates are relative to view, which started the touch
    return (0 <= pos[0] < box[2] and 0 <= pos[1] < box[3])


class OscButton(ui.View):
    """Delegate for Button to implement different touch behaviour"""

    def __init__(self, x, y, handler):
        self.value = y * NCOLS + x
        self.x = OFFSET + x * (BWIDTH + XSPACING)
        self.y = OFFSET + y * (BHEIGHT + YSPACING)
        self.width = BWIDTH
        self.height = BHEIGHT

        btn = ui.Button()
        btn.frame = (0, 0, self.width, self.height)
        btn.background_color = BCOLOR
        btn.border_width = 0
        btn.corner_radius = 8
        btn.touch_enabled = False
        self.add_subview(btn)

        title = "Program %02i" % self.value
        lbl = ui.Label()
        lbl.text = title
        lbl.frame = (10, 0, BWIDTH - 20, BHEIGHT - 20)
        lbl.text_color = BFONTCOLOR
        lbl.font = (BFONT, BFONTSIZE)
        lbl.alignment = ui.ALIGN_LEFT
        self.add_subview(lbl)

        self.touch_enabled = True
        self.multitouch_enabled = False
        self.action = handler

    def touch_began(self, touch):
        # Called when a touch begins.
        btn = self.subviews[0]
        btn.background_color = 1.00, 0.80, 0.40

    def touch_ended(self, touch):
        # Called when a touch ends.
        btn = self.subviews[0]
        btn.background_color = BCOLOR

        if contains(self.frame, touch.location):
            self.action(self)


class OscPanelView(ui.View):
    def __init__(self):
        self.client = ThreadedClient(OSC_HOST, OSC_PORT)
        self._osc_active = False
        self.program = None

    def did_load(self):
        self.create_gui()
        self.client.start()

    def will_close(self):
        self.client.close()

    def create_gui(self):
        self.btn_osc_activity = ui.ButtonItem(
            image=ICONS['osc_inactive'], enabled=False)
        self.right_button_items = [
            self.btn_osc_activity
        ]
        for y in range(NROWS):
            for x in range(NCOLS):
                self.add_button(x, y, self.button_activated)

    def add_button(self, x, y, handler):
        self.add_subview(OscButton(x, y, handler))

    def osc_active(self):
        if not self._osc_active:
            self._osc_active = True
            self.btn_osc_activity.image = ICONS['osc_active']
            ui.delay(self.osc_inactive, 0.1)

    def osc_inactive(self):
        if self._osc_active:
            self._osc_active = False
            self.btn_osc_activity.image = ICONS['osc_inactive']

    def button_activated(self, sender):
        self.osc_active()
        log.info("Program: %02i" % sender.value)

        if sender.value != self.program:
            self.program = sender.value
            try:
                self.client.send('/midi', ('m', (0, 0xC0, self.program, 0)))
            except Exception as exc:
                import traceback
                traceback.print_exc()


def main(args=None):
    logging.basicConfig(level=logging.DEBUG if '-v' in args else logging.INFO,
                        format="%(levelname)s: %(message)s")
    view = ui.load_view('oscpanel')
    view.present('fullscreen')


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv[1:]) or 0)
