import subprocess
import os
import threading
from .config import WebhookConfig, DockerConfigManipulator


class WebhookExecutor:

    def deploy(self, token):
        hook_config = WebhookConfig().load()
        if token in hook_config:
            conf = hook_config[token]

            def runInThread():
                docker_config = DockerConfigManipulator()
                docker_config.decrypt()
                try:
                    subprocess.call(os.path.join(WebhookConfig.CONFIG_DIR,
                                                 token, "deploy.sh"))
                except:
                    pass
                docker_config.encrypt()
                return
            thread = threading.Thread(target=runInThread)
            thread.start()

            return True
        else:
            return False
