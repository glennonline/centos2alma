from .action import Action

import subprocess
import os


class RulePleskRelatedServices(Action):

    def __init__(self):
        self.name = "rule plesk services"
        plesk_known_systemd_services = [
            "crond.service",
            "dovecot.service",
            "fail2ban.service",
            "httpd.service",
            "mailman.service",
            "mariadb.service",
            "named-chroot.service",
            "plesk-ext-monitoring-hcd.service",
            "plesk-ip-remapping.service",
            "plesk-ssh-terminal.service",
            "plesk-task-manager.service",
            "plesk-web-socket.service",
            "postfix.service",
            "psa.service",
            "sw-collectd.service",
            "sw-cp-server.service",
            "sw-engine.service",
        ]
        self.plesk_systemd_services = [service for service in plesk_known_systemd_services if self._is_service_exsists(service)]

    def _is_service_exsists(self, service):
        return os.path.exists(os.path.join("/usr/lib/systemd/system/", service))

    def _prepare_action(self):
        subprocess.check_call(["systemctl", "stop"] + self.plesk_systemd_services)
        subprocess.check_call(["systemctl", "disable"] + self.plesk_systemd_services)

    def _post_action(self):
        subprocess.check_call(["systemctl", "enable"] + self.plesk_systemd_services)
        subprocess.check_call(["systemctl", "start"] + self.plesk_systemd_services)
