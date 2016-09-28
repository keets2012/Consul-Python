
from consul.client import ConsulClient
import logging

logging.basicConfig()


sc = ConsulClient("testService",
                tags=["mater","v1"],Consul_url="172.16.30.254",service_port=8080,check_note="test check", check_time_out="10s",
                 context="Consul/v2", check_name="test name", deregisterCriticalServiceAfter="90m",Service_url="172.16.33.75",consul_port="8500",
                 ip_address=None, vip_address=None, check_type="TCP",check_content="172.16.33.75:8080",
                 ttl=None, enableTagOverride=False, health_check_interval="10s")
print sc.register()
