import socket

INET_ADDRSTRLEN = 16


inet_ntoa = getattr(socket, 'inet_ntoa', None)
if not inet_ntoa:
    import ffilib
    inet_ntoa = ffilib.libc().func("s", "inet_ntoa", "p")

inet_ntop = getattr(socket, 'inet_ntop', None)
if not inet_ntop:
    import ffilib
    _inet_ntop = ffilib.libc().func("s", "inet_ntop", "iPpi")

    def inet_ntop(af, addr):
        buf = bytearray(INET_ADDRSTRLEN)
        res = _inet_ntop(af, addr, buf, INET_ADDRSTRLEN)
        return res

def get_hostport(addr):
    af, addr, port = socket.sockaddr(addr)
    return inet_ntop(af, addr), port
