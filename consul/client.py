import random
from urllib2 import URLError
from urlparse import urljoin
from consul import requests
import ec2metadata
import logging
import dns.resolver
from requests import ConsulHTTPException
import sys
from time import sleep
import json
import threading

logger = logging.getLogger('Consul.client')


class ConsulClientException(Exception):
    pass


class ConsulRegistrationFailedException(ConsulClientException):
    pass


class ConsulUpdateFailedException(ConsulClientException):
    pass


class ConsulHeartbeatFailedException(ConsulClientException):
    pass


class ConsulGetFailedException(ConsulClientException):
    pass

class ConsulLogOutFailedException(ConsulClientException):
    pass

class ConsulClient(object):
    def __init__(self, app_name,tags=None,Consul_url=None,service_port=None,check_note=True, check_time_out=None,
                 context="Consul/v2", check_name=None, deregisterCriticalServiceAfter=None,Service_url=None,consul_port=None,
                 ip_address=None, vip_address=None, check_type=None,check_content=None,
                 ttl=None, enableTagOverride=False, health_check_interval=0):
        super(ConsulClient, self).__init__()
        self.app_name = app_name
        self.Consul_url = Consul_url
        self.app_id = Service_url + ':' + str(service_port) + ':' + app_name
        self.tags = tags
        self.service_port = service_port
        # Virtual host name by which the clients identifies this service
        self.check_note = check_note
        self.check_time_out = check_time_out
        self.check_name = check_name
        self.deregisterCriticalServiceAfter = deregisterCriticalServiceAfter
        self.check_type = check_type
        self.check_content = check_content
        self.ttl = ttl
        self.Service_url=Service_url
        self.consul_port=consul_port
        # Prefer a Consul server in same zone or not
        self.enableTagOverride = enableTagOverride
        #if Consul runs on a port that is not 80, this will go into the urls to Consul
        self.health_check_interval = health_check_interval


    def register(self):
        success = False
        service_data = {
            "ID": self.app_id,
            "Name":self.app_name,
            "Tags": self.tags,
            "Address": self.Service_url,
            "Port": self.service_port,
            "EnableTagOverride": self.enableTagOverride,
            "Check":{
                "DeregisterCriticalServiceAfter":self.deregisterCriticalServiceAfter,
                self.check_type:self.check_content,
                "Interval":self.health_check_interval,
                "notes":self.check_note,
                "timeout":self.check_time_out,
            }
        }
        print self.Consul_url + ":" + self.consul_port + "/v1/agent/service/register"
        try:
            r = requests.put("http://" + self.Consul_url + ":" + self.consul_port + "/v1/agent/service/register", json.dumps(service_data),
                                        headers={'Content-Type': 'application/json'})
            r[0].raise_for_status()
            success = True
        except (ConsulHTTPException, URLError):
            pass
        if not success:
            raise ConsulRegistrationFailedException("Did not receive correct reply from any instances"), None, sys.exc_info()[2]

    def get_instances(self):
        return self.host_name+':'+self.app_name+':'+str(self.port)

    def update_status(self, new_status):
        instance_id = get_instances(self)
        if self.data_center == "Amazon":
            instance_id = ec2metadata.get('instance-id')
        success = False
        for Consul_url in self.Consul_urls:
            try:
                r = requests.put(urljoin(Consul_url, "apps/%s/%s/status?value=%s" % (
                    self.app_name,
                    instance_id,
                    new_status
                )))
                r.raise_for_status()
                success = True
                break
            except (ConsulHTTPException, URLError) as e:
                pass
        if not success:
            raise ConsulUpdateFailedException("Did not receive correct reply from any instances"), None, sys.exc_info()[2]

    def heartbeat(self,instance_id):
        while True:
            print 'run'
            if self.data_center == "Amazon":
                instance_id = ec2metadata.get('instance-id')
            success = False
            for i in xrange(len(self.Consul_urls)):
                try:
                    # instance_data["instance"]["healthCheckUrl"] =self.healthCheckUrls[i] 
                    # instance_data["instance"]["statusPageUrl"] = self.statusPageUrls[i]
                    r = requests.put(urljoin(self.Consul_urls[i], "apps/%s/%s" % (self.app_name, instance_id)))
                    r[0].raise_for_status()
                    success = True
                    break
                except (ConsulHTTPException, URLError) as e:
                    pass
            if not success: 
                raise ConsulHeartbeatFailedException("Did not receive correct reply from any instances"), None, sys.exc_info()[2]
            time.sleep(int(self.heartbeatInterval))

    def de_register(self):
        instance_id = get_instances()
        for i in xrange(len(self.Consul_urls)):
            try:
                r = requests.delete(urljoin(self.Consul_urls[i], "apps/%s/%s" % (self.app_name, instance_id)))
                r[0].raise_for_status()
                success = True
            except (ConsulHTTPException, URLError) as e:
                pass
        if not success: 
            raise ConsulLogOutFailedException("Did not de-register correctly from instances"), None, sys.exc_info()[2]

    def get_apps(self):
        return self._get_from_any_instance("apps")

    def get_app(self, app_id):
        return self._get_from_any_instance("apps/%s" % app_id)

    def get_vip(self, vip_address):
        return self._get_from_any_instance("vips/%s" % vip_address)

    def get_svip(self, vip_address):
        return self._get_from_any_instance("svips/%s" % vip_address)

    def get_instance(self, instance_id):
        return self._get_from_any_instance("instances/%s" % instance_id)

    def get_app_instance(self, app_id, instance_id):
        return self._get_from_any_instance("apps/%s/%s" % (app_id, instance_id))

