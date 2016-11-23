import os
import json
import base64
import subprocess
import os, os.path
import shutil
import stat


class WebhookConfig:

    # TODO: is this path good?
    CONFIG_DIR = "/etc/docker-webhook-deployer"
    FILE_PATH = os.path.join(CONFIG_DIR, "webhooks.json")
    TEMPLATE_DIR = "/opt/app/templates"

    def __init__(self):
        self.docker_config = DockerConfigManipulator()

    def token(self):
        tok = os.urandom(32)
        return base64.urlsafe_b64encode(tok).rstrip(b'=').decode('ascii')

    def add_image(self):
        data = {}
        data["deploy_type"] = "image"
        data["image"] = raw_input("image name: ")
        data["container"] = raw_input("container name: ")
        data["port"] = raw_input("port (eg. 80:80): ")
        token = self.add(data)
        if token:
            self.create_shell_script(data, token)

    def add_compose(self, yml_path):
        data = {}
        data["deploy_type"] = "compose"
        data["project"] = raw_input("project name: ")
        token = self.add(data)
        if token:
            data["yml"] = os.path.join(self.CONFIG_DIR, token,
                                       "docker-compose.yml")
            self.create_shell_script(data, token)
            shutil.copy(yml_path, os.path.join(self.CONFIG_DIR, token))

    def add(self, new_data):
        data = self.load()
        token = self.token()

        # docker login
        registry = []
        if raw_input("login required? (y/n): ") == "y":
            while True:
                server = raw_input("server: ")
                if self.docker_config.login(server):
                    registry.append(server)
                if raw_input("login more? (y/n): ") != "y":
                    break
            new_data["registry"] = registry

        # add new data
        print("===> Token: %s" % token)
        data[token] = new_data

        if self.save(data):
            print("Saved!")
            return token
        else:
            return None

    def create_shell_script(self, data, token):
        # create deploy shell script
        os.mkdir(os.path.join(self.CONFIG_DIR, token))
        inputfile = os.path.join(self.TEMPLATE_DIR,
                  "deploy-%s.sh" % data["deploy_type"])
        outputfile = os.path.join(self.CONFIG_DIR, token, "deploy.sh")
        with open(inputfile) as template, open(outputfile, "w+") as script:
            for line in template:
                replaced = line
                for key, value in data.iteritems():
                    if type(value) is str or type(value) is unicode:
                        replaced = replaced.replace("$" + key.upper(),
                                                    value)
                script.write(replaced)
        os.chmod(outputfile, os.stat(outputfile).st_mode | stat.S_IEXEC)

    def remove(self, token):
        data = self.load()
        if token in data:
            if "registry" in data[token]:
                for registry in data[token]["registry"]:
                    print(registry)
                    self.docker_config.logout(registry)
            del data[token]
            shutil.rmtree(os.path.join(self.CONFIG_DIR, token))
            if self.save(data):
                print("Removed!")
        else:
            print("The token does not exist.")

    def show(self):
        print(json.dumps(self.load(), indent=4, sort_keys=True))

    def load(self):
        try:
            with open(self.FILE_PATH, "r") as f:
                data = json.load(f)
        except:
            data = {}
        return data

    def save(self, data):
        try:
            with open(self.FILE_PATH, "w+") as f:
                json.dump(data, f)
        except:
            return False
        return True


class DockerConfigManipulator:

    DOCKER_CONFIG_DIR = "/root/.docker"
    DOCKER_CONFIG = os.path.join(DOCKER_CONFIG_DIR, "config.json")
    DOCKER_CONFIG_ENC = os.path.join(WebhookConfig.CONFIG_DIR, "docker-config.dat")
    DOCKER_CONFIG_KEY = os.path.join(WebhookConfig.CONFIG_DIR, "key.bin")

    def __init__(self):
        try:
            if not os.path.isdir(WebhookConfig.CONFIG_DIR):
                os.mkdir(WebhookConfig.CONFIG_DIR, 0700)
            if not os.path.isdir(self.DOCKER_CONFIG_DIR):
                os.mkdir(self.DOCKER_CONFIG_DIR, 0700)
            if not os.path.isfile(self.DOCKER_CONFIG_KEY):
                subprocess.check_call("openssl rand -base64 128 -out %s" %
                                      self.DOCKER_CONFIG_KEY, shell=True)
        except:
            pass

    def encrypt(self):
        try:
            if os.path.isfile(self.DOCKER_CONFIG):
                subprocess.check_call(
                    "openssl aes-256-cbc -salt -a -in %s -out %s -pass file:%s" %
                    (self.DOCKER_CONFIG,
                     self.DOCKER_CONFIG_ENC,
                     self.DOCKER_CONFIG_KEY),
                    shell=True)
                os.remove(self.DOCKER_CONFIG)
        except:
            pass

    def decrypt(self):
        try:
            if os.path.isfile(self.DOCKER_CONFIG_ENC) and \
                not os.path.isfile(self.DOCKER_CONFIG):
                subprocess.check_call(
                    "openssl aes-256-cbc -d -salt -a -in %s -out %s -pass file:%s" %
                    (self.DOCKER_CONFIG_ENC,
                     self.DOCKER_CONFIG,
                     self.DOCKER_CONFIG_KEY),
                    shell=True)
        except:
            pass

    def login(self, server):
        self.decrypt()
        result = True
        try:
            subprocess.check_call("docker login %s" % server, shell=True)
        except:
            result = False
        self.encrypt()
        return result

    def logout(self, server):
        self.decrypt()
        result = True
        try:
            subprocess.check_call("docker logout %s" % server, shell=True)
        except:
            result = False
        self.encrypt()
        return result
