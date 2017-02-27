#!/usr/bin/env python
# encoding: utf-8

from rally.plugins.openstack import scenario
from rally.task import atomic
import paramiko
import time
from os import environ


def check_key(ip, pkey, expectation):
    try:
        client = paramiko.client.SSHClient()
        client.set_missing_host_key_policy(paramiko.client.MissingHostKeyPolicy())
        client.connect(ip, 22, username="root", pkey=pkey)
    except paramiko.ssh_exception.AuthenticationException as e:
        return not expectation
    return expectation


@scenario.configure(name="EayunNova.server_bind_publickey")
class BindPublicKey(scenario.OpenStackScenario):
    def _boot_server(self, **kwargs):
        if kwargs["is_admin"]:
            client = self.admin_clients("nova")
        else:
            client = self.clients("nova")
        flavor = client.flavors.get(kwargs.pop("flavor"))
        server = client.servers.create(image=None, flavor=flavor, **kwargs)
        time.sleep(90)
        server.add_floating_ip(self.context["floatingip"]["floating_ip_address"])
        return server

    def _delete_server(self, server, force_delete=True):
        if force_delete:
            server.force_delete()
        else:
            server.delete()

    def change_key(self, server, userdata):
        self.clients("nova").servers.set_meta(server, {"reset_sshkeys": str(time.time())})
        server.change_userdata(userdata)

    @atomic.action_timer("add_key_active")
    def _add_key_active(self, **kwargs):
        server = self._boot_server(is_admin=False, **kwargs)
        private_key = open(environ['HOME'] + '/.ssh/id_rsa', 'r'),
        new_userdata = open("./first_key.txt", 'r')
        self.change_key(server, new_userdata)
        import pdb;pdb.set_trace()
        if check_key(self.context["floatingip"]["floating_ip_address"], private_key, False):
            print ("Test Sucessful")
        else:
            raise Exception
        self._delete_server(server)

    def _add_key_active_as_admin(self):
        pass

    def run(self, **kwargs):
        userdata = open('./only_password.txt', 'r')
        nics=[
            {
                "net-id": self.context["nets"][0][0]["id"]
            }
        ]
        self._add_key_active(nics=nics, userdata=userdata, **kwargs)
