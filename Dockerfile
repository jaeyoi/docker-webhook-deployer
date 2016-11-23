FROM jaeyoi/docker-with-compose

EXPOSE 7000

ADD app /opt/app

ENTRYPOINT ["/opt/app/docker-webhook-deployer.py"]
CMD ["run"]
