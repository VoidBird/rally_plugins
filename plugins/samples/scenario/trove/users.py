#!/usr/bin/env python
# encoding: utf-8

from rally.plugins.openstack import scenario
from rally.task import atomic
from troveclient.utlis import print_dict


@scenario.configure(name="TroveUsers.list_users")
class ListUsers(scenario.OpenstackScenario):

    @atomic.action_timer("list_users")
    def _list_users(self):
        self.clients("trove").users.list(self.context['user_instance'])

    @atomic.action_timer("list_users_as_admin")
    def _list_users_as_admin(self):
        self.admin_clients("trove").users.list(self.context["admin_instance"])

    def run(self):
        self._list_users()
        self._list_users_as_admin()


@scenario.configure(name="TroveUsers.create_user")
class CreateUser(scenario.OpenstackScenario):
    @atomic.action_timer("create_user")
    def _create_user(self, users):
        manager = self.clients("trove").users
        instance = self.context['user_instance']
        users = manager.create(instance, users)
        manager.delete(users)

    @atomic.action_timer('create_user_as_admin')
    def _create_user_as_admin(self, users):
        manager = self.admin_clients("trove").users
        instance = self.context['admin_instance']
        users = manager.create(instance, users)
        manager.delete(users)

    def run(self, users):
        self._create_user(users)
        self._create_user_as_admin(users)


@scenario.configure(name="TroveUsers.show_user")
class ShowUsers(scenario.OpenstackScenario):

    @atomic.action_timer("show_user")
    def _show(self, user_name):
        instance = self.context['user_instance']
        user = self.clients.users.show(instance, user_name)
        print_dict(user.to_dict())

    @atomic.action_timer("show_user")
    def _show_as_admin(self, user_name):
        instance = self.context['admin_instance']
        user = self.admin_clients.users.show(instance, user_name)
        print_dict(user.to_dict())

    def run(self, user):
        self._show(user)
        self._show_as_admin(user)


@scenario.configure(name="TroveUsers.delete_user")
class DeleteUser(scenario.OpenstackScenario):

    @atomic.action_timer("delete")
    def _delete(self, user):
        self.clients('trove').users.delete(self.context['user_instance'], user)

    @atomic.action_timer("delete_as_admin")
    def _delete_as_admin(self, user):
        self.admin_clients('trove').users.delete(self.context['admin_instance'], user)

    def run(self):
        self._delete()
        self._delete_as_admin()


@scenario.configure(name="TroveUsers.user_show_access")
class ShowAccess(scenario.OpenstackScenario):

    @atomic.action_timer('show')
    def _show(self, username):
        self.clients('trove').users.list_access(self.context['user_instance'], username)

    @atomic.action_timer('show')
    def _show_as_admin(self, username):
        self.admin_clients('trove').users.list_access(self.context['admin_instance'], username)

    def run(self, username):
        self._show(username)
        self._show_as_admin(username)


@scenario.configure(name="TroveUsers.user_grant_access")
class GrantAccess(scenario.OpenstackScenario):

    @atomic.action_timer("grant")
    def _grant(self, username, databases):
        self.clients("trove").users.grant(
            self.context['user_instance'], username, databases)

    @atomic.action_timer("grant_as_admin")
    def _grant_as_admin(self, username, databases):
        self.admin_clients("trove").users.grant(
            self.context['admin_instance'], username, databases)

    def run(self, username, databases):
        self._grant(username, databases)
        self._grant_as_admin(username, databases)


@scenario.configure(name="TroveUsers.user_revoke_access")
class RevokeAccess(scenario.OpenstackScenario):

    @atomic.action_timer("remoke")
    def _remoke(self, username, databases):
        self.clients("trove").users.remoke(
            self.context['user_instance'], username, databases)

    @atomic.action_timer("remoke_as_admin")
    def _remoke_as_admin(self, username, databases):
        self.admin_clients("trove").users.remoke(
            self.context['admin_instance'], username, databases)

    def run(self, username, databases):
        self._remoke(username, databases)
        self._remoke_as_admin(username, databases)


@scenario.configure(name="TroveUsers.update_users")
class UpdateUser(scenario.OpenstackScenario):

    @atomic.action_timer("update")
    def _update(self, *args):
        self.clients("trove").update_attributes(
            self.context['user_instance'], *args)

    @atomic.action_timer("update_as_admin")
    def _update_as_admin(self, *args):
        self.clients("trove").update_attributes(
            self.context['user_instance'], *args)

    def run(self, username, newuserattr):
        self._update(username, newuserattr)
        self._update(username, newuserattr)


@scenario.configure(name="TroveUsers.root_enable")
class RootEnable(scenario.OpenstackScenario):

    @staticmethod
    def _enable(manager, instance, enable):
        if not enable:
            manager.create_instance_root(instance)
            if manager.is_root_enabled() == False:
                raise BaseException
            else:
                manager.disable_instance_root(instance)
        else:
            manager.disable_instance_root(instance)
            if manager.is_root_enabled == True:
                raise BaseException
            else:
                manager.create_instance_root(instance)

    @atomic.action_timer("enable")
    def _root_enable(self, enable):
        manager = self.clients("trove").root
        instance = self.context['user_instance']
        self._enable(manager, instance, enable)

    @atomic.action_timer("enable")
    def _root_enable_as_admin(self, enable):
        manager = self.admin_clients("trove").root
        instance = self.context['admin_instance']
        self._enable(manager, instance, enable)

    def run(self, enable):
        self._root_enable(enable)
        self._root_enable_as_admin(enable)
