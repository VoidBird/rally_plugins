#!/usr/bin/env python
# encoding: utf-8

from rally.plugins.openstack import scenario
from rally.task import atomic, utils
from utils import check_ready, change_status
from time import sleep


@scenario.configure(name="TroveInstance.list_instance")
class ListInstance(scenario.OpenStackScenario):

    @atomic.action_timer("list_instance")
    def _list_instance(self):
        self.clients("trove").instances.list()

    @atomic.action_timer("list_instance_as_admin")
    def _list_instance_as_admin(self):
        self.admin_clients("trove").instances.list()

    def run(self):
        self._list_instance()
        self._list_instance_as_admin()


@scenario.configure(name="TroveInstance.create_instance")
class CreateInstance(scenario.OpenStackScenario):

    @staticmethod
    def _create(kw, manager):
        instance = manager.create(**kw)
        try:
            check_ready(instance)
        finally:
            try:
                instance.delete()
            except Exception:
                instance.force_delete()

            utils.wait_for_status(
                instance, ready_statuses=['deleted'],
                update_resource=utils.get_from_manager(),
                timeout=600, check_deletion=True,
                check_interval=10)

            sleep(20)

    @atomic.action_timer("create_instance")
    def _create_instace(self, **kwargs):

        if kwargs.get('configuration', self.context.get("user_configuration")):
            kwargs["configuration"] = kwargs.get("configuration", self.context.get("user_configuration"))

        kwargs["nics"] = kwargs.get("nics", [{"net-id": self.context["user_network"]}])

        manager = self.clients("trove").instances
        self._create(kwargs, manager)

    @atomic.action_timer("create_instance_as_admin")
    def _create_instace_as_admin(self, **kwargs):

        if kwargs.get('configuration', self.context.get("admin_configuration")):
            kwargs["configuration"] = kwargs.get("configuration", self.context.get("admin_configuration"))

        kwargs["nics"] = kwargs.get("nics", [{"net-id": self.context["admin_network"]}])

        manager = self.admin_clients("trove").instances
        self._create(kwargs, manager)

    def run(self, **kwargs):
        """
        :param name:the name of instance:necessery
        :param flavor_id:the flavor's id of instance:necessery
        :param volume:the size(type, optional):dict:default None
        :param databases:the list of conf which is used to create database:list:default None
        :param users:the list of datastore's user:list:default None
        :param restorePoint
        :param availability_zone
        :param datastore:the name of datastore:default None
        :param datastore_version:the version of datastore:default None
        :param nics:the network of instance:default None
        :param configuration:the id of configuration_group which use in create:default None
        :param replica_of
        :param slave_of
        """
        if self.context.get("volume_type"):
            kwargs["volume"]["type"] = self.context.get("volume_type")
        self._create_instace(**kwargs)
        self._create_instace_as_admin(**kwargs)
        sleep(30)


@scenario.configure(name="TroveInstance.show_instance")
class ShowInstance(scenario.OpenStackScenario):

    @atomic.action_timer("show_instance")
    def _show_instance(self):
        manager = self.clients("trove").instances
        instance = manager.get(self.context["user_instance"])
        check_ready(instance)

    @atomic.action_timer("show_instance_as_admin")
    def _show_instance_as_admin(self):
        manager = self.admin_clients("trove").instances
        instance = manager.get(self.context["admin_instance"])
        check_ready(instance)

    def run(self):
        self._show_instance()
        self._show_instance_as_admin()


@scenario.configure(name="TroveInstance.update_instance")
class UpdateInstance(scenario.OpenStackScenario):

    @atomic.action_timer(name="update_instance")
    def _update_instance(self, **kwargs):
        if self.context.get("user_configuration"):
            kwargs["configuration"] = self.context["user_configuration"]
        manager = self.clients("trove").instances
        instance = manager.get(self.context["user_instance"])
        check_ready(instance)
        self.clients("trove").instances.edit(instance, **kwargs)

    @atomic.action_timer(name="update_instance_as_admin")
    def _update_instance_as_admin(self, **kwargs):
        if self.context.get("admin_configuration"):
            kwargs["configuration"] = self.context["admin_configuration"]
        manager = self.admin_clients("trove").instances
        instance = manager.get(self.context["admin_instance"])
        check_ready(instance)
        self.admin_clients("trove").instances.edit(instance, **kwargs)

    def run(self, name=None, configuration=None, remove_configuration=False, detach_replica_source=False):
        """
        :param name:update the name of instance:string
        :param configuration:update the id of configuration which belong to instance
        ::without remove_configuration=Ture:string
        :param remove_configuration:remove the configuration of instance:boolean
        :param detach_replica_source
        """
        kwargs = {
            "name": name,
            "configuration": configuration,
            "remove_configuration": remove_configuration,
            "detach_replica_source": detach_replica_source
        }
        self._update_instance(**kwargs)
        self._update_instance_as_admin(**kwargs)


@scenario.configure(name="TroveInstance.remove_configuration")
class RemoveConf(scenario.OpenStackScenario):

    @atomic.action_timer(name="remove_conf")
    def _update_instance(self):
        manager = self.clients("trove").instances
        instance = manager.get(self.context["user_instance"])
        check_ready(instance)
        self.clients("trove").instances.edit(instance, remove_configuration=True)

    @atomic.action_timer(name="remove_conf_as_admin")
    def _update_instance_as_admin(self):
        manager = self.admin_clients("trove").instances
        instance = manager.get(self.context["admin_instance"])
        check_ready(instance)
        self.admin_clients("trove").instances.edit(instance, remove_configuration=True)

    def run(self):
        self._update_instance()
        self._update_instance_as_admin()


@scenario.configure(name="TroveInstance.restart_instance")
class RestartInstance(scenario.OpenStackScenario):

    @staticmethod
    def _restart(instance, client, status):
        instance = client.instances.get(instance)

        change_status(instance, status,
                      client.configurations if status == "RESTART_REQUIRED" else None)

        instance.restart
        utils.wait_for(instance, ready_statuse=["REBOOT"],
                       update_resource=client.instances.get)
        check_ready(instance)

    @atomic.action_timer("restart_instance")
    def _restart_instance(self, status):
        client= self.clients("trove")
        self._restart(self.context['user_instance'], client, status)

    @atomic.action_timer("restart_instance_as_admin")
    def _restart_instance_as_admin(self, status):
        client= self.admin_clients("trove")
        self._restart(self.context['admin_instance'], client, status)

    def run(self, status):
        self._restart_instance(status)
        self._restart_instance_as_admin(status)


@scenario.configure(name="TroveInstance.delete_instance")
class DeleteInstance(scenario.OpenStackScenario):

    def __init__(self, context=None, admin_clients=None, clients=None):
        super(DeleteInstance, self).__init__(context, admin_clients, clients)
        self.force_delete = False

    @staticmethod
    def _delete(instance, client, status, force_delete=False):
        instance = client.instances.get(instance)
        change_status(instance, client, status)
        if not force_delete:
            client.instances.delete(instance)
        else:
            client.instances.force_delete(instance)

    @atomic.action_timer("delete_instance")
    def _delete_instance(self, status):
        client = self.clients("trove")
        instance = self.context["user_instance"]
        self._delete(instance, client, status, self.force_delete)

    @atomic.action_timer("delete_instance_as_admin")
    def _delete_instance_as_admin(self, status):
        client = self.admin_clients("trove").instances
        instance = self.context["admin_instance"]
        self._delete(instance, client, status, self.force_delete)

    def run(self, status):
        self._delete_instance(status)
        self._delete_instance_as_admin(status)


@scenario.configure(name="TroveInstance.force_delete")
class ForceDelete(DeleteInstance):

    def __init__(self, context=None, admin_clients=None, clients=None):
        super(DeleteInstance, self).__init__(context, admin_clients, clients)
        self.force_delete = True


@scenario.configure(name="TroveInstance.resize_instance")
class ResizeInstance(scenario.OpenStackScenario):

    @staticmethod
    def _resize(instance, client, status, flavor_id):
        instance = client.instances.get(instance)
        change_status(instance, client, status)
        client.instances.resize_instance(instance, flavor_id)
        utils.wait_for(instance,
                       update_resource=client.instances.get, ready_statuse=["RESIZE"])
        check_ready(instance)

    @atomic.action_timer("resize_instance")
    def _resize_instance(self, status, flavor_id):
        client = self.clients("trove")
        instance = self.context['user_instance']
        self._resize(instance, client, status, flavor_id)

    @atomic.action_timer("resize_instance_as_admin")
    def _resize_instance_as_admin(self, status, flavor_id):
        client = self.admin_clients("trove")
        instance = self.context['admin_instance']
        self._resize(instance, client, status, flavor_id)

    def run(self, status, flavor_id):
        self._resize_instance(status, flavor_id)
        self._resize_instance_as_admin(status, flavor_id)


@scenario.configure(name="TroveInstance.resize_volume")
class ResizeVolume(scenario.OpenStackScenario):

    @staticmethod
    def _resize(instance, client, status, size):
        instance = client.instances.get(instance)
        change_status(instance, client, status)
        client.instances.resize_volume(instance['id'], size)
        utils.wait_for(instance,
                       update_resource=client.instances.get, ready_statuse=["RESIZE"])
        check_ready(instance)

    @atomic.action_timer("resize_volume")
    def _resize_instance(self, status, size):
        client = self.clients("trove")
        instance = self.context['user_instance']
        self._resize(instance, client, status, size)

    @atomic.action_timer("resize_volume_as_admin")
    def _resize_instance_as_admin(self, status, size):
        client = self.admin_clients("trove")
        instance = self.context['admin_instance']
        self._resize(instance, client, status, size)

    def run(self, status, size):
        self._resize_instance(status, size)
        self._resize_instance_as_admin(status, size)
