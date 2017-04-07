#!/usr/bin/env python
# encoding: utf-8
from rally.plugins.openstack import scenario
from rally.task import atomic, utils
from troveclient.utils import print_dict, print_list
from utils import change_status, check_ready


@scenario.configure(name="TroveConfiguration.list_configurations")
class ListConfigurations(scenario.OpenStackScenario):

    @atomic.action_timer("list_configurations")
    def _list_configurations(self):
        confs = self.clients("trove").configurations.list()
        print_list(confs)

    @atomic.action_timer("list_configurations_as_admin")
    def _list_configurations_as_admin(self):
        confs = self.admin_clients("trove").configurations.list()
        print_list(confs)

    def run(self):
        self._list_configurations()
        self._list_configurations_as_admin()


@scenario.configure(name="TroveConfiguration.list_default_conf")
class DefaultConf(scenario.OpenStackScenario):

    @atomic.action_timer("list_configurations")
    def _list_defaut_conf(self):
        instance = self.context['user_instance']
        conf = self.clients("trove").instances.configuration(instance)
        print_dict(conf.to_dict())

    @atomic.action_timer("list_configurations_as_admin")
    def _list_default_conf_as_admin(self):
        instance = self.context['admin_instance']
        conf = self.admin_clients("trove").instances.configuration(instance)
        print_dict(conf.to_dict())

    def run(self):
        self._list_defaut_conf()
        self._list_default_conf_as_admin()


@scenario.configure(name="TroveConfiguration.create_conf")
class CreateDeleteConfigurations(scenario.OpenStackScenario):

    @atomic.action_timer("create_configuration")
    def _create_configuration(self, **kwargs):
        self.conf = self.clients("trove").configurations.create(**kwargs)

    @atomic.action_timer("create_configuration_as_admin")
    def _create_configuration_as_admin(self, **kwargs):
        self.admin_conf = self.admin_clients("trove").configurations.create(**kwargs)

    def _delete_configuration(self):
        self.clients("trove").configurations.delete(self.conf)

    def _delete_configuration_as_admin(self):
        self.admin_clients("trove").configurations.delete(self.admin_conf)

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
        conf = manager.get(self.context['user_configuration'])
        print_dict(conf.to_dict())

    @atomic.action_timer("show_configuration_as_admin")
    def _show_conf_as_admin(self):
        manager = self.admin_clients("trove").configurations
        conf = manager.get(self.context['admin_configuration'])
        print_dict(conf.to_dict())

    def run(self):
        self._show_conf()
        self._show_conf_as_admin()


@scenario.configure(name="TroveConfiguration.list_instances_with_configuration")
class ListInstancesWithConf(scenario.OpenStackScenario):

    @atomic.action_timer("list_instance_with_conf")
    def _list_instances_with_conf(self):

        manager = self.clients("trove").configurations
        instance = manager.instances(self.context['user_configuration'])
        print_dict(instance.to_dict())

    def _list_instances_with_conf_as_admin(self):
        manager = self.admin_clients("trove").configurations
        instance = manager.instances(self.context['admin_configuration'])
        print_dict(instance.to_dict())

    def run(self, **kwargs):
        self._list_instances_with_conf()
        self._list_instances_with_conf_as_admin()


@scenario.configure(name="TroveConfiguration.attach_conf")
class AttachConf(scenario.OpenStackScenario):

    @atomic.action_timer("attach_conf")
    def _attach(self, status):
        client = self.clients("trove")
        manager = client.instances
        instance, conf = manager.get(self.context['user_instance']), self.context['user_configuration']
        change_status(instance, client, status)
        manager.modify(instance, conf)

    @atomic.action_timer("attach_conf_as_admin")
    def _attach_as_admin(self, status):
        client = self.clients("trove")
        manager = client.instances
        instance, conf = manager.get(self.context['admin_instance']), self.context['admin_configuration']
        change_status(instance, client, status)
        manager.modify(instance, conf)

    def run(self, status):
        self._attach(status)
        self._attach_as_admin(status)


@scenario.configure(name="TroveConfiguration.delete_conf")
class DeleteConf(scenario.OpenStackScenario):

    @atomic.action_timer("delete")
    def _delete(self):
        self.clients("trove").configurations.delete(
            self.context['user_configuration'])

    @atomic.action_timer("delete_as_admin")
    def _delete_as_admin(self):
        self.admin_clients("trove").configurations.delete(
            self.context['admin_configuration'])

    def run(self):
        self._delete()
        self._delete_as_admin()


@scenario.configure(name="TroveConfiguration.conf_param_list")
class ParamList(scenario.OpenStackScenario):

    @atomic.action_timer("list")
    def _list(self, datastore, version):
        params = self.client("trove").config_parameters.parameters(datastore, version)
        print_list(params)

    @atomic.action_timer("list_as_admin")
    def _list_as_admin(self, datastore, version):
        params = self.client("trove").config_parameters.parameters(datastore, version)
        print_list(params)

    def run(self, datastore, version):
        self._list(datastore, version)
        self._list_as_admin(datastore, version)


@scenario.configure(name="TroveConfiguration.conf_param_show")
class ParamShow(scenario.OpenStackScenario):

    @atomic.action_timer("show")
    def _show(self, datastore, version, key):
        param = self.client("trove").config_parameters.get_parameter(datastore, version, key)
        print_dict(param)

    @atomic.action_timer("show_as_admin")
    def _show_as_admin(self, datastore, version, key):
        param = self.client("trove").config_parameters.get_parameter(datastore, version, key)
        print_dict(param)

    def run(self):
        self._show()
        self._show_as_admin()


@scenario.configure(name="TroveConfiguration.update_conf")
class UpdateConf(scenario.OpenStackScenario):

    @staticmethod
    def _update(instance, conf, client, status, **kwargs):
        c_manager = client.configurations
        i_manager = client.instances
        instance = i_manager.get(instance)

        c_manager.update(conf, **kwargs)
        if status == "ACTIVE":
            check_ready(instance)
        elif status == "RESTART_REQUIRED":
            utils.wait_for_status(instance, update_resource=i_manager.get,
                                  ready_statuse=[status])
            i_manager.restart(instance)
            check_ready(instance)

        print_dict(c_manager.get(conf).to_dict())

    @atomic.action_timer("update_conf")
    def _update_conf(self, status, **kwargs):
        client = self.clients('trove')
        self._update(
            instance=self.context['user_instance'],
            conf=self.context['user_configuration'],
            client=client, status=client, **kwargs)

    @atomic.action_timer("update_conf_as_admin")
    def _update_conf_as_admin(self, status, **kwargs):
        client = self.admin_clients('trove')
        self._update(
            instance=self.context.get('admin_instance'),
            conf=self.context['admin_configuration'],
            client=client, status=status, **kwargs
        )

    def run(self, status=None, **kwargs):
        # values, name=None, description=None
        self._update_conf(status, **kwargs)
        self._update_conf_as_admin(status, **kwargs)
