# Copyright 1999 - 2023. Plesk International GmbH. All rights reserved.
from .action import ActiveAction

import os

from common import util


def _is_service_exists(service):
    return os.path.exists(os.path.join("/usr/lib/systemd/system/", service))


class RulePleskRelatedServices(ActiveAction):

    def __init__(self):
        self.name = "rule plesk services"
        plesk_known_systemd_services = [
            "crond.service",
            "dovecot.service",
            "drwebd.service",
            "fail2ban.service",
            "httpd.service",
            "mailman.service",
            "mariadb.service",
            "mysqld.service",
            "named-chroot.service",
            "plesk-ext-monitoring-hcd.service",
            "plesk-ip-remapping.service",
            "plesk-ssh-terminal.service",
            "plesk-task-manager.service",
            "plesk-web-socket.service",
            "psa.service",
            "sw-collectd.service",
            "sw-cp-server.service",
            "sw-engine.service",
        ]
        self.plesk_systemd_services = [service for service in plesk_known_systemd_services if _is_service_exists(service)]

        # We don't remove postfix service when remove it during qmail installation
        # so we should choose the right smtp service, otherwise they will conflict
        if _is_service_exists("qmail.service"):
            self.plesk_systemd_services.append("qmail.service")
        else:
            self.plesk_systemd_services.append("postfix.service")

    def _prepare_action(self):
        util.logged_check_call(["/usr/bin/systemctl", "stop"] + self.plesk_systemd_services)
        util.logged_check_call(["/usr/bin/systemctl", "disable"] + self.plesk_systemd_services)

    def _post_action(self):
        util.logged_check_call(["/usr/bin/systemctl", "enable"] + self.plesk_systemd_services)
        # Don't do startup because the services will be started up after reboot at the end of the script anyway.

    def _revert_action(self):
        util.logged_check_call(["/usr/bin/systemctl", "enable"] + self.plesk_systemd_services)
        util.logged_check_call(["/usr/bin/systemctl", "start"] + self.plesk_systemd_services)

    def estimate_prepare_time(self):
        return 10

    def estimate_post_time(self):
        return 5

    def estimate_revert_time(self):
        return 10


class AddUpgradeSystemdService(ActiveAction):

    def __init__(self, script_path):
        self.name = "adding centos2alma resume service"
        self.script_path = script_path
        self.service_name = 'plesk-centos2alma.service'
        self.service_file_path = os.path.join('/etc/systemd/system', self.service_name)
        self.service_content = '''
[Unit]
Description=First boot service for upgrade process from CentOS 7 to AlmaLinux8.
After=network.target network-online.target

[Service]
Type=simple
# want to run it once per boot time
RemainAfterExit=yes
ExecStart={script_path} -s finish

[Install]
WantedBy=multi-user.target
'''

    def _prepare_action(self):
        with open(self.service_file_path, "w") as dst:
            dst.write(self.service_content.format(script_path=self.script_path))

        util.logged_check_call(["/usr/bin/systemctl", "enable", self.service_name])

    def _post_action(self):
        if os.path.exists(self.service_file_path):
            util.logged_check_call(["/usr/bin/systemctl", "disable", self.service_name])

            os.remove(self.service_file_path)

    def _revert_action(self):
        if os.path.exists(self.service_file_path):
            util.logged_check_call(["/usr/bin/systemctl", "disable", self.service_name])

            os.remove(self.service_file_path)


class StartPleskBasicServices(ActiveAction):

    def __init__(self):
        self.name = "starting plesk services"
        self.plesk_basic_services = [
            "mariadb.service",
            "mysqld.service",
            "plesk-task-manager.service",
            "plesk-web-socket.service",
            "sw-cp-server.service",
            "sw-engine.service",
        ]
        self.plesk_basic_services = [service for service in self.plesk_basic_services if _is_service_exists(service)]

    def _enable_services(self):
        util.logged_check_call(["/usr/bin/systemctl", "enable"] + self.plesk_basic_services)
        util.logged_check_call(["/usr/bin/systemctl", "start"] + self.plesk_basic_services)

    def _prepare_action(self):
        pass

    def _post_action(self):
        self._enable_services()

    def _revert_action(self):
        self._enable_services()