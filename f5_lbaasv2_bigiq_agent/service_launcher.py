from oslo_service import service
from oslo_service import systemd


class F5ServiceLauncher(service.ServiceLauncher):

    def __init__(self, conf):
        super(F5ServiceLauncher, self).__init__(conf)

    def handle_signal(self):
        self.signal_handler.add_handler('SIGTERM', self._graceful_shutdown)
        self.signal_handler.add_handler('SIGINT', self._fast_exit)
        self.signal_handler.add_handler('SIGHUP', self._reload_service)
        self.signal_handler.add_handler('SIGALRM', self._on_timeout_exit)

    def wait(self):
        systemd.notify_once()
        while True:
            self.handle_signal()
            status, signo = self._wait_for_exit_or_signal()
            if not service._is_sighup_and_daemon(signo):
                break
            self.restart()

        self.services.wait()
        return status
