import subprocess
import time

subprocess.run(["xset", "dpms", "force", "off"])
time.sleep(15)
subprocess.run(["xset", "dpms", "force", "on"])
