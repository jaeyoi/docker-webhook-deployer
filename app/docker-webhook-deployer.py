#!/usr/bin/env python
import sys
from webhook.config import WebhookConfig
from webhook import server


def usage():
    print("Usage: docker-webhook-deployer.py {run|add-image|add-compose|remove|list}.")
    sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        usage()

    hook = WebhookConfig()

    if sys.argv[1] == "run":
        server.run(port=7000)
    elif sys.argv[1] == "add-image":
        hook.add_image()
    elif sys.argv[1] == "add-compose"and len(sys.argv) == 3:
        hook.add_compose(sys.argv[2])
    elif sys.argv[1] == "remove" and len(sys.argv) == 3:
        hook.remove(sys.argv[2])
    elif sys.argv[1] == "list":
        hook.show()
    else:
        usage()
