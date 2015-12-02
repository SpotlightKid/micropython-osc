import socket

INET_ADDRSTRLEN = 16
INET6_ADDRSTRLEN = 46

inet_ntoa = getattr(socket, 'inet_ntoa', None)
if not inet_ntoa:
    import ffilib
    inet_ntoa = ffilib.libc().func("s", "inet_ntoa", "p")


inet_ntop = getattr(socket, 'inet_ntop', None)
if not inet_ntop:
    import ffilib
    _inet_ntop = ffilib.libc().func("s", "inet_ntop", "iPpi")

    def inet_ntop(af, addr):
        buf = bytearray(INET_ADDRSTRLEN if af == socket.AF_INET else
                        INET6_ADDRSTRLEN)
        res = _inet_ntop(af, addr, buf, INET_ADDRSTRLEN)
        return res


def get_hostport(addr):
    if isinstance(addr, tuple):
        return addr

    af, addr, port = socket.sockaddr(addr)
    return inet_ntop(af, addr), port


def pack_addr(addr):
    if isinstance(addr, (bytes, bytearray)):
        return addr

    if len(addr) != 2:
        raise NotImplementedError("Only IPv4/v6 supported")

    addrinfo = socket.getaddrinfo(addr[0], addr[1], socket.AF_INET)
    return addrinfo[0][4]
