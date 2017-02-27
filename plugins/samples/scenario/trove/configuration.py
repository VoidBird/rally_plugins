#!/usr/bin/env python
# encoding: utf-8
from rally.plugins.openstack import scenario
from rally.task import atomic


@scenario.configure(name="TroveConfiguration.list_configurations")
class ListConfigurations(scenario.OpenStackScenario):

    @atomic.action_timer("list_configurations")
    def _list_configurations(self):
        self.clients("trove").configurations.list()

    @atomic.action_timer("list_configurations_as_admin")
    def _list_configurations_as_admin(self):
        self.admin_clients("trove").configurations.list()

    def run(self):
        self._list_configurations()
        self._list_configurations_as_admin()


@scenario.configure(name="TroveConfiguration.create_and_delete_configuration")
class CreateDeleteConfigurations(scenario.OpenStackScenario):

    @atomic.action_timer("create_configuration")
    def _create_configuration(self, **kwargs):
        self.conf = self.clients("trove").configurations.create(**kwargs)

    @atomic.action_timer("create_configuration_as_admin")
    def _create_configuration_as_admin(self, **kwargs):
        self.admin_conf = self.admin_clients("trove").configurations.create(**kwargs)

    @atomic.action_timer("delete_configuration")
    def _delete_configuration(self):
        self.clients("trove").configurations.delete(self.conf.id)

    @atomic.action_timer("_delete_configurations_as_admin")
    def _delete_configuration_as_admin(self):
        self.admin_clients("trove").configurations.delete(self.admin_conf.id)

    def run(self, **kwargs):
        """
        :param string name
        :param string value
        :param string description
        :param string datastore
        :param string datastore_version
        """
        kwargs['values'] = open(kwargs['values'], 'r').read()
        self._create_configuration(**kwargs)
        self._delete_configuration()
        self._create_configuration_as_admin(**kwargs)
        self._delete_configuration_as_admin()


@scenario.configure(name="TroveConfiguration.show_configuration")
class ShowConfiguration(scenario.OpenStackScenario):

    @atomic.action_timer("show_configuration")
    def _show_conf(self):
        manager = self.clients("trove").configurations
        for configuration in manager.list():
            # self.context use deepcopy, you can't use Configurations type directly
            if configuration.id == self.context['user_configuration']['id']:
                break
        else:
            raise Exception
        manager.get(configuration)

    @atomic.action_timer("show_configuration_as_admin")
    def _show_conf_as_admin(self):
        manager = self.admin_clients("trove").configurations
        for configuration in manager.list():
            # self.context use deepcopy, you can't use Configurations type directly
            if configuration.id == self.context['admin_configuration']['id']:
                break
        else:
            raise Exception
        manager.get(configuration)

    def run(self):
        self._show_conf()
        self._show_conf_as_admin()


@scenario.configure(name="TroveConfiguration.list_instances_with_configuration")
class ListInstancesWithConf(scenario.OpenStackScenario):

    @atomic.action_timer("list_instance_with_conf")
    def _list_instances_with_conf(self):

        manager = self.clients("trove").configurations
        for configuration in manager.list():
            if configuration.id == self.context['user_configuration']['id']:
                break
        else:
            raise Exception
        manager.instances(configuration)

    def _list_instances_with_conf_as_admin(self):
        manager = self.admin_clients("trove").configurations
        for configuration in manager.list():
            if configuration.id == self.context['admin_configuration']['id']:
                break
        else:
            raise Exception
        manager.instances(configuration)

    def run(self, **kwargs):
        self._list_instances_with_conf()
        self._list_instances_with_conf_as_admin()
