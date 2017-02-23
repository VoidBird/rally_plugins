#!/usr/bin/env python
# encoding: utf-8

from rally.plugins.openstack import scenario
from rally.task import atomic
from time import sleep
from novaclient import utils


@scenario.configure(name="EayunNova.attach_and_detach")
class Interface(scenario.OpenStackScenario):

    def _get_port_id(self, ip):
        ports = self.clients("neutron").list_ports()['ports']
        for port in ports:
            fixed_ips = port['fixed_ips']
            for fixed_ip in fixed_ips:
                if fixed_ip['ip_address'] == ip:
                    return port['id']
        else:
            raise Exception

    def _get_ip(self, server_id):
        server = self.clients("nova", "1.1").servers.get(server_id)
        ip = server.networks.values()[0][0]
        return ip

    def _attach(self, server_id, net_id):
        self.clients("nova", "1.1").servers.interface_attach(server=server_id, port_id=None, net_id=net_id, fixed_ip=None)

    def _detach(self, server_id, port_id):
        self.clients("nova", "1.1").servers.interface_detach(server_id, port_id)

    def _attach_and_detach(self, server_id, net_id):
        ip = self._get_ip(server_id)
        port_id = self._get_port_id(ip)
        self._detach(server_id, port_id)
        self._attach(server_id, port_id)

    def _suspend_server(self, server_id):
        self.clients("nova", "1.1").servers.suspend()

    def _resume_server(self, server_id):
        self.clients("nova", "1.1").servers.resume()

    def _test_states(self, server_id):
        for i in range(0, 20):
            state = self.clients("nova").get('server_id')
            if state == 'SUSPEND':
                sleep(1)
                continue
            elif state == 'ACTIVE':
                continue

    def _test(self, server_id, net_id):
        self._attach_and_detach(server_id, net_id)
        self._test_states(server_id)

    def run(self, server_id, net_id, attach_times, detach_times):
        self._test(server_id, net_id, attach_times, detach_times)

