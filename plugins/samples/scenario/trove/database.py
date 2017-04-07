#!/usr/bin/env python
# encoding: utf-8

from rally.plugins.openstack import scenario
from rally.task import atomic
from utils import check_ready


@scenario.configure(name="TroveDatabase.list_databases")
class ListDatabase(scenario.OpenStackScenario):

    @atomic.action_timer("list_databases")
    def _list_databases(self):
        self.clients("trove").databases.list(self.context["user_instance"])

    @atomic.action_timer("list_databases_as_admin")
    def _list_databases_as_admin(self):
        self.admin_clients("trove").databases.list(self.context["admin_instance"])

    def run(self):
        self._list_databases()
        self._list_databases_as_admin()


@scenario.configure(name="TroveDatabase.create_databases")
class CreateDatabase(scenario.OpenStackScenario):

    @atomic.action_timer("create_databases")
    def _create_database(self, body):
        client = self.clients("trove")
        instance = client.instances.get(self.context['user_instance'])
        check_ready(instance, client.instances)
        client.databases.create(instance, body)

    @atomic.action_timer("create_database_as_admin")
    def _create_database_as_admin(self, body):
        client = self.clients("trove")
        instance = client.instances.get(self.context['admin_instance'])
        check_ready(instance, client.instances)
        client.databases.create(instance, body)

    def run(self, databases):
        self._create_database(databases)
        self._create_database_as_admin(databases)


@scenario.configure(name="TroveDatabase.delete_database")
class Delete(scenario.OpenStackScenario):

    @atomic.action_timer("delete_inexistent_database")
    def _delete(self, name):
        self.clients("trove").databases.delete(self.context["user_instance"], name)

    @atomic.action_timer("delete_inexistent_database_as_admin")
    def _delete_as_admin(self, name):
        self.admin_clients("trove").databases.delete(self.context["admin_instance"], name)

    def run(self, db_name):
        self._delete(db_name)
        self._delete_as_admin(db_name)
