#!/usr/bin/env python
# encoding: utf-8

from rally.plugins.openstack import scenario
from rally.task import atomic
from time import  sleep


@scenario.configure(name="TroveLog.log_list")
class LogList(scenario.OpenstackScenario):

    @atomic.action_timer("list_log")
    def _list(self):
        instance, manager = self.context['user_instance'], self.client('trove').instances
        manager.log_list(instance)

    @atomic.action_timer("list_log_as_admin")
    def _list_as_admin(self):
        instance, manager = self.context['admin_instance'], self.admin_client('trove').instances
        manager.log_list(instance)

    def run(self):
        self._list()
        self._list_as_admin()


@scenario.configure(name="TroveLog.log_show")
class LogShow(scenario.OpenstackScenario):

    @atomic.action_timer("log_show")
    def _show(self):
        instance, manager = self.context['user_instance'], self.client('trove').instances
        log = manager.log_list(instance)[0]
        manager.log_show(log)

    @atomic.action_timer("log_show_as_admin")
    def _show_as_admin(self):
        instance, manager = self.context['admin_instance'], self.admin_client('trove').instances
        log = manager.log_list(instance)[0]
        manager.log_show(log.name)


@scenario.configure(name="TroveLog.log_enable")
class LogEnable(scenario.OpenstackScenario):

    @staticmethod
    def _enable(instance, manager, log_status):
        log = manager.list_log(instance)[0]
        if log.status == "Disabled" == log_status:
            pass
        elif log.status == "Ready" == log_status:
            pass
        elif log.status == "Ready" and log_status=="Disables":
            manager.log_enable(instance, log.name)

        manager.log_enable(instance, log.name)
        if manager.log_show(instance, log.name).status != "Ready":
            raise BaseException

    @atomic.action_timer("enable")
    def _log_enable(self, log_status):
        instance, manager = self.context['user_instance'], self.client('trove').instances
        self._enable(instance, manager, log_status)

    @atomic.action_timer("enable")
    def _log_enable_as_admin(self, log_status):
        instance, manager = self.context['admin_instance'], self.admin_client('trove').instances
        self._enable(instance, manager, log_status)

    def run(self, log_status):
        self._log_enable(log_status)
        self._log_enable_as_admin(log_status)


@scenario.configure(name="TroveLog.log_disable")
class LogDisable(scenario.OpenstackScenario):

    @staticmethod
    def disable(instance, log_name, log_status, manager):
        get_status = lambda a, b: b.log_show(a).status
        if log_status == "Disabled" and get_status(log_name, manager) == "Enable":
            manager.log_disable(instance, log_name)
            for i in range(0, 12):
                if get_status(log_name, manager) == "Disabled":
                    break
                else:
                    sleep(5)
            else:
                raise BaseException
        elif log_status == "Publish" != get_status(log_name, manager):
            manager.log_publish(instance, log_name)
            for i in range(0, 12):
                if get_status(log_name, manager) == "Publish":
                    break
                else:
                    sleep(5)
            else:
                raise BaseException

    @atomic.action_timer("disable")
    def _log_disable(self):
        pass

    @atomic.action_timer("disable_as_admin")
    def _log_disable_as_admin(self):
        pass

    def run(self):
        pass
