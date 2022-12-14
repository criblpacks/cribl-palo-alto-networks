import socket


class Facility:
    KERN, USER, MAIL, DAEMON, AUTH, SYSLOG, LPR, NEWS, UUCP, CRON, AUTHPRIV, FTP = range(12)
    LOCAL0, LOCAL1, LOCAL2, LOCAL3, LOCAL4, LOCAL5, LOCAL6, LOCAL7 = range(16, 24)


class Level:
    EMERG, ALERT, CRIT, ERR, WARNING, NOTICE, INFO, DEBUG = range(8)


class PROTOCOL:
    UDP, TCP = range(2)


class Syslog:
    """A syslog client that logs to a remote server.

    Example:
    >>> log = Syslog(host="foobar.example")
    >>> log.send("hello", Level.WARNING)
    """

    def __init__(self, host="localhost", port=514, facility=Facility.LOCAL0):
        self.host = host
        self.port = port
        self.facility = facility
        self._udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def close(self):
        self._udp_socket.close()
        self._tcp_socket.close()

    def _send_tcp(self, data):
        self._tcp_socket.sendto(data.encode('ascii'), (self.host, self.port))
        self._tcp_socket.close()

    def _send_udp(self, data):
        self._udp_socket.sendto(data.encode('ascii'), (self.host, self.port))
        self._tcp_socket.close()

    def send(self, message, level=Level.INFO, protocol=PROTOCOL.UDP):
        data = "<%d>%s" % (level + self.facility * 8, message)

        if protocol == PROTOCOL.UDP:
            self._send_udp(data)
        else:
            self._send_tcp(data)

    def send_raw(self, message, protocol=PROTOCOL.UDP):
        data = "%s" % message

        if protocol == PROTOCOL.UDP:
            self._send_udp(data)
        else:
            self._send_tcp(data)

    def info(self, message):
        self.send(message, Level.INFO)

    def warn(self, message):
        self.send(message, Level.WARNING)

    def notice(self, message):
        self.send(message, Level.NOTICE)

    def error(self, message):
        self.send(message, Level.ERR)
