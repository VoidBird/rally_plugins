#!/usr/bin/env python
# encoding: utf-8

from rally.plugins.openstack import scenario
from rally.task import atomic
from utils import change_status, check_ready


def _check_backup_status(backup, manager, status):
    while True:
        b_status = manager.get(backup).status
        if b_status == status:
            break
        elif b_status == "FAILED":
            raise BaseException
        else:
            continue


@scenario.configure(name="list_backups")
class ListBackup(scenario.OpenStackScenario):

    @atomic.action_timer("list_backups")
    def _list_backup(self, limit=None, marker=None, datastore=None):
        self.clients("trove").backups.list(limit, marker, datastore)

    @atomic.action_timer("list_backups_as_admin")
    def _list_backup_as_admin(self, limit=None, marker=None, datastore=None):
        self.admin_clients("trove").backups.list(limit, marker, datastore)

    def run(self, limit=None, marker=None, datastore=None):
        self._list_backup(limit, marker, datastore)
        self._list_backup_as_admin(limit, marker, datastore)


@scenario.configure(name="create_full_backup")
class CreateFullBackup(scenario.OpenStackScenario):

    @staticmethod
    def _create(instance, client, status, **kwargs):
        b_manager, i_manager = client.backups, client.instances
        change_status(instance, client, status)
        backup = b_manager.create(instance=instance['id'], **kwargs)
        check_ready(instance['id'], i_manager)
        b_manager.delete(backup)

    @atomic.action_timer("create_full_backup")
    def _create_backup(self, **kwargs):
        client = self.clients("trove")
        instance = self.context['user_instance']
        self._create(client, instance, **kwargs)

    @atomic.action_timer("create_full_backup_as_admin")
    def _create_backup_as_admin(self, **kwargs):
        client = self.admin_clients("trove")
        instance = self.context['admin_instance']
        self._create(client, instance, **kwargs)

    def run(self, status, **kwargs):
        self._create_backup(status=status, **kwargs)
        self._create_backup_as_admin(status=status, **kwargs)


@scenario.configure(name="create_incremental_backup")
class CreateIncrementalBackup(scenario.OpenStackScenario):

    @atomic.action_timer("create_incremental_backup")
    def _create(self, name, description=None, parent=None,
                backup=None, incremental=True):
        manager = self.clients("trove").backups

        if parent:
            for full_backup in self.context['user_backups']:
                if full_backup['name'] == parent:
                    parent_id = full_backup['id']

        manager.create(
            name, self.context["user_instance"]["id"],
            description, parent_id, backup, incremental)

    @atomic.action_timer("create_incremental_backup_as_admin")
    def _create_as_admin(self, name, description=None, parent=None,
                         backup=None, incremental=True):
        manager = self.clients("trove").backups

        if parent:
            for full_backup in self.context['user_backups']:
                if full_backup['name'] == parent:
                    parent_id = full_backup['id']

        manager.create(
            name, self.context["user_instance"]["id"],
            description, parent_id, backup, incremental)

    def run(self, **kwargs):
        self._create(**kwargs)
        self._create_as_admin(**kwargs)
