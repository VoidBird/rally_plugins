#!/usr/bin/env python
# encoding: utf-8

from rally.plugins.openstack import scenario
from rally.task import atomic


@scenario.configure(name="EayunNova.list")
class NovaList(scenario.OpenStackScenario):

    @atomic.action_timer("list_instance")
    def _list_instance(self):
        self.clients("nova").servers.list()

    def _list_instance_as_admin(self):
        self.clients("nova").servers.list()

    def run(self):
        self. _list_instance()


@scenario.configure(name="EayunNova.boot_and_delete")
class NovaBootAndDelete(scenario.OpenStackScenario):

    def __init__(self, context=None, admin_clients=None, clients=None):
        self.servers = {}
        super(NovaBootAndDelete, self).__init__(context, admin_clients, clients)

    @atomic.action_timer("boot_server")
    def _boot_server(self, *args, **kwargs):
        self.servers['user'] = self.clients("nova").servers.create(*args, **kwargs)

    def _delete_server(self, force_delete=False):
        if not force_delete:
            self.clients("nova").servers.delete()
        else:
            self.clients("nova").servers.force_delete()

    def run(self, name, image, flavor, meta=None, files=None,
            reservation_id=None, min_count=None,
            max_count=None, security_groups=None, userdata=None,
            key_name=None, availability_zone=None,
            block_device_mapping=None, block_device_mapping_v2=None,
            nics=None, scheduler_hints=None,
            config_drive=None, disk_config=None, force_delete=False,
            **kwargs):

        boot_args = [name, image, flavor]
        boot_kwargs = dict(meta=meta, files=files, reservation_id=reservation_id,
                           min_count=min_count, max_count=max_count,
                           security_groups=security_groups, userdata=userdata,
                           key_name=key_name, availability_zone=availability_zone,
                           block_device_mapping=block_device_mapping,
                           block_device_mapping_v2=block_device_mapping_v2,
                           nics=nics, scheduler_hints=scheduler_hints,
                           config_drive=config_drive, disk_config=disk_config, **kwargs)

        self._boot_server(*boot_args, **boot_kwargs)
        # self._delete_server(force_delete)
