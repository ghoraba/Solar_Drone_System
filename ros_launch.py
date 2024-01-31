import os
import sys
import subprocess
import time
import re

import lib.log as log_man
import lib.settings as set_man


MODULE_ID = 'ros_launch'

settings_obj = set_man.get_settings()

# validate network configs
network_config: dict[str, str] = settings_obj['networking']

log_man.print_log(MODULE_ID, 'INFO', 'checking network configs')

for machine_name, machine_ip in network_config.items():
    if machine_ip in ['', '127.0.0.1']:
        continue

    log_man.print_log(MODULE_ID, 'DEBUG',
                       f"checking host {machine_name} with IP {machine_ip}")

    proc_exit_code = os.system(f"ping -4 -c 1 {machine_ip}")

    if proc_exit_code != 0:
        log_man.print_log(
            MODULE_ID, 'ERROR', f"host {machine_name} with IP {machine_ip} is offline")
        sys.exit()