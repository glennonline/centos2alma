from .action import Action

import subprocess


class DoConvert(Action):
    def __init__(self):
        self.name = "do converation with leapp"

    def _prepare_action(self):
        subprocess.check_call(["leapp", "preupgrade"])
        subprocess.check_call(["leapp", "upgrade"])

    def _post_action(self):
        pass
