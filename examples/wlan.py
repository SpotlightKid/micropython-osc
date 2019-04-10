def do_connect(ssis, password, tries=5):
    from network import WLAN, STA_IF
    from time import sleep
    sta_if = WLAN(STA_IF)

    if not sta_if.isconnected():
        sta_if.active(True)
        sta_if.connect(ssid, password)

        for i in range(tries):
            print('Connecting to network (try {})...'.format(i+1))
            if sta_if.isconnected():
                print('network config:', sta_if.ifconfig())
                break

            sleep(1)
        else:
            print("Failed to connect in {} seconds.".format(tries))
