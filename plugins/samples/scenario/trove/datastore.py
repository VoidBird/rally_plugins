#!/usr/bin/env python
# encoding: utf-8

from rally.plugins.openstack import scenario
from rally.task import atomic


@scenario.configure(name="EayunTrove.list_datastores")
class ListDatastore(scenario.OpenStackScenario):

    @atomic.action_timer("list_datastores")
    def _list_all_datastores(self):
        self.clients("trove").datastores.list()

    @atomic.action_timer("list_datastores_as_admin")
    def _list_all_datastores_as_admin(self):
        self.admin_clients("trove").datastores.list()

    def run(self):
        self._list_all_datastores()
        self._list_all_datastores_as_admin()


@scenario.configure(name="EayunTrove.show_datastore")
class ShowDatastore(scenario.OpenStackScenario):

    @atomic.action_timer("show_datastore")
    def _show_datastore(self):
        client = self.clients("trove")
        datastore = client.datastores.list()[0]
        client.datastores.get(datastore)

    @atomic.action_timer("show_datastore_as_admin")
    def _show_datastore_as_admin(self):
        client = self.admin_clients("trove")
        datastore = client.datastores.list()[0]
        client.datastores.get(datastore)

    def run(self):
        self._show_datastore()
        self._show_datastore_as_admin()


@scenario.configure(name="EayunTrove.list_datastore_version")
class ListDatastoreVersion(scenario.OpenStackScenario):

    @atomic.action_timer("list_datastore_version")
    def _list_datastore_version(self):
        client = self.clients("trove")
        datastore = client.datastores.list()[0]
        client.datastore_versions.list(datastore.id)

    @atomic.action_timer("list_datastore_version_as_admin")
    def _list_datastore_version_as_admin(self):
        client = self.admin_clients("trove")
        datastore = client.datastores.list()[0]
        client.datastore_versions.list(datastore.id)

    def run(self):
        self._list_datastore_version()
        self._list_datastore_version_as_admin()


@scenario.configure(name="EayunTrove.show_datastore_version")
class ShowDatastoreVersion(scenario.OpenStackScenario):

    @atomic.action_timer("show_datastore_version")
    def _show_datastore_version(self):
        client = self.clients("trove")
        datastore = client.datastores.list()[0]
        datastore_version = client.datastore_versions.list(datastore.id)[0]
        client.datastore_versions.get_by_uuid(datastore_version.id)

    @atomic.action_timer("show_datastore_version_as_admin")
    def _show_datastore_version_as_admin(self):
        client = self.admin_clients("trove")
        datastore = client.datastores.list()[0]
        datastore_version = client.datastore_versions.list(datastore.id)[0]
        client.datastore_versions.get_by_uuid(datastore_version.id)

    def run(self):
        self._show_datastore_version()
        self._show_datastore_version_as_admin()
