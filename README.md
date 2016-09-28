python-consul version - 1.1M
=============

The goal of this project is to provide an easy-to-use client interface to consul,
a middle-tier load balancer open sourced .

It's fairly straight forward to use once you hve setup Eureka itself. Consider the following script (to be run):

```python

from consul.client import ConsulClient
import os

SERVER_PORT = os.getenv('SERVER_PORT')
HOST_ADDRESS = os.getenv('HOST_ADDRESS')
CONSUL_ADDRESS = os.getenv('CONSUL_ADDRESS')
CONSUL_PORT = os.getenv('CONSUL_PORT')
TAGS = [os.getenv('TAGS')]
ec = ConsulClient("testService",
                app_id="test1",
                tags=TAGS,
                Consul_url=CONSUL_ADDRESS,
                service_port=int(SERVER_PORT),
                check_note="test check",
                check_time_out="10s",
                context="Consul/v2",
                check_name="test name",
                deregisterCriticalServiceAfter="90m",
                Service_url=HOST_ADDRESS,
                consul_port=CONSUL_PORT,
                ip_address=None,
                vip_address=None,
                check_type="TCP",
                check_content="172.16.33.161:8080",
                ttl=None,
                enableTagOverride=False,
                health_check_interval="10s")

print ec.register()

```
