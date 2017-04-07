#!/usr/bin/env python
# encoding: utf-8

from rally.plugins.openstack import scenario
from rally.task import atomic


@scenario.configure(name="TroveSecgroup.list_secgroup")
class ListSecgroup(scenario.OpenStackScenario):

    @atomic.action_timer("list_secgroup")
    def _list_secgroup(self):
        self.clients("trove").security_groups.list()

    @atomic.action_timer("list_secgroup_as_admin")
    def _list_secgroup_as_admin(self):
        self.admin_clients("trove").security_groups.list()

    def run(self):
        self._list_secgroup()
        self._list_secgroup_as_admin()


@scenario.configure(name="TroveSecgroup.list_secgroup_rules")
class ListSecgroupRules(scenario.OpenStackScenario):
    """
    You need create_instance context plugin to create a secgroup before run this scenario
    """

    @atomic.action_timer("list_secgroup_rules")
    def _list_secgroup_rules(self):
        manager = self.clients("trove").security_groups
        group = manager.list()[0]
        manager.get(group)

    @atomic.action_timer("list_secgroup_rules_as_admin")
    def _list_secgroup_rules_as_admin(self):
        manager = self.admin_clients("trove").security_groups
        group = manager.list()[0]
        manager.get(group)

    def run(self):
        self._list_secgroup_rules()
        self._list_secgroup_rules_as_admin()


@scenario.configure(name="TroveSecgroup.show_secgroup")
class ShowSecgroup(scenario.OpenStackScenario):

    @atomic.action_timer("show_secgroup_rules")
    def _show_secgroup_rules(self):
        manager = self.clients("trove").security_groups
        group = manager.list()[0]
        manager.get(group)

    @atomic.action_timer("show_secgroup_rules_as_admin")
    def _show_secgroup_rules_as_admin(self):
        manager = self.admin_clients("trove").security_groups
        group = manager.list()[0]
        manager.get(group)

    def run(self):
        self._show_secgroup_rules()
        self._show_secgroup_rules_as_admin()


@scenario.configure(name="TroveSecgroup.add_secgroup_rule")
class AddRule(scenario.OpenStackScenario):

    @atomic.action_timer("add_rule")
    def _add_rule(self, cidr):
        group = self.clients("trove").security_groups.list()[0]
        return self.clients("trove").security_group_rules.create(group.id, cidr)

    @atomic.action_timer("add_rule_as_admin")
    def _add_rule_as_admin(self, cidr):
        group = self.admin_clients("trove").security_groups.list()[0]
        return self.admin_clients("trove").security_group_rules.create(group.id, cidr)

    def run(self, cidr):
        self._add_rule(cidr)
        self._add_rule_as_admin(cidr)


@scenario.configure(name="TroveSecgroup.delete_secgroup_rule")
class DeleteRule(AddRule):

    @atomic.action_timer("delete_rule")
    def _delete_rule(self, cidr):
        rule = self._add_rule(cidr)
        self.clients("trove").security_groups_rules.delete(rule)

    @atomic.action_timer("delete_rule_as_admin")
    def _delete_rule_as_admin(self, cidr):
        rule = self._add_rule_as_admin(cidr)
        self.admin_clients("trove").security_groups_rules.delete(rule)

    def run(self, cidr):
        self._delete_rule(cidr)
        self._delete_rule_as_admin(cidr)
