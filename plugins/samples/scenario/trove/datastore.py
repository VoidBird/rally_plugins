#!/usr/bin/env python
# encoding: utf-8

from rally.plugins.openstack import scenario
from rally.task import atomic
from pdb import set_trace


@scenario.configure(name="EayunTrove.list_datastore")
class ListDatastore(scenario.OpenStackScenario):

    @atomic.action_timer("list_datastore")
    def _list_all_datastores(self):
        self.clients("trove").datastores.list()

    @atomic.action_timer("list_datastore_as_admin")
    def _list_all_datastores_as_admin(self):
        self.admin_client("trove").datastores.list()

    def run(self):
        self._list_all_datastores()
        self._list_all_datastores_as_admin()


@scenario.configure(name="EayunTrove.show_datastore")
class ShowDatastore(scenario.OpenStackScenario):

    @atomic.action_timer("show_datastore")
    def _show_datastore(self):
        client = self.clients("trove")
        set_trace()
        client.datastores.get(client.datastores.list()[0])

    @atomic.action_timer("show_datastore_as_admin")
    def _show_datastore_as_admin(self):
        client = self.admin_clients("trove")
        client.datastores.get(client.datastores.list()[0])

    def run(self):
        self._show_datastore()
        self._show_datastore_as_admin()


@scenario.configure(name="EayunTrove.list_datastore_version")
class ListDatastoreVersion(scenario.OpenStackScenario):

    @atomic.action_timer("list_datastore_version")
    def _list_datastore_version(self):
        client = self.clients("trove")
        datastore = client.datastores.list()[0]
        set_trace()
        client.datastore_versions.list(datastore)

    @atomic.action_timer("list_datastore_as_admin")
    def _list_all_datastores_as_admin(self):
        client = self.admin_clients("trove")
        datastore = client.datastores.list()[0]
        client.datastore_versions.list(datastore)

    def run(self):
        self._list_all_datastores()
        self._list_all_datastores_as_admin()
