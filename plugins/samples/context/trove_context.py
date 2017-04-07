#!/usr/bin/env python
# encoding: utf-8
from rally.common import logging
from rally import consts
from rally import osclients
from rally.task import context, utils
from time import sleep

LOG = logging.getLogger(__name__)

"""
These Class is created to create trove resource before
you run trove scenario plugin.
The resource can through to scenario_plugin by self.context
"""


@context.configure(name="create_conf", order=1100)
class CreateConfiguration(context.Context):

    CONFIG_SCHEMA = {
        "type": "object",
        "$schema": consts.JSON_SCHEMA,
        "additionalProperties": False,
        "properties": {
            "name": {"type": "string"},
            "values": {"type": "string"},
            "datastore": {"type": "string"},
            "description": {"type": "string"},
            "datastore_version": {"type": "string"}
        }
    }

    def setup(self):

        """
        rally context doesn't use multithreading,
        so we need create resource for every user
        and through it.
        """
        def _user_setup():
            try:
                client = osclients.Clients(self.context['users'][0]["credential"]).trove()
                configuration = client.configurations.create(
                    self.config['name'],
                    open(self.config['values'], 'r').read(),
                    datastore=self.config.get('datastore', 'mysql'),
                    description=self.config.get('description'),
                    datastore_version=self.config.get('datastore_version', '5.5')
                )
                self.context['user_configuration'] = configuration.id
                LOG.debug("User_Configuration_Group With id '%s'" % configuration.id)
            except Exception as e:
                msg = "Can't create user configuration_group: %s" % e
                if logging.is_debug():
                    LOG.exception(msg)
                else:
                    LOG.warning(msg)

        def _admin_setup():
            try:
                client = osclients.Clients(self.context["admin"]["credential"]).trove()
                configuration = client.configurations.create(
                    self.config['name'],
                    open(self.config['values'], 'r').read(),
                    datastore=self.config.get('datastore', 'mysql'),
                    description=self.config.get('description'),
                    datastore_version=self.config.get('datastore_version', '5.5')
                )
                self.context['admin_configuration'] = configuration.id
                LOG.debug("Admin_Configuration_Group With id '%s'" % configuration.id)
            except Exception as e:
                msg = "Can't create admin configuration_group: %s" % e
                if logging.is_debug():
                    LOG.exception(msg)
                else:
                    LOG.warning(msg)

        _user_setup()
        _admin_setup()

    def cleanup(self):
        def _user_cleanup():
            try:
                client = osclients.Clients(self.context['users'][0]['credential']).trove()
                client.configurations.delete(self.context['user_configuration'])
                LOG.debug("Configuration group '%s' deleted" % self.context['user_configuration'])
            except Exception as e:
                msg = "Can't delete user configuration group: %s" % e
                if logging.is_debug():
                    LOG.exception(msg)
                else:
                    LOG.warning(msg)

        def _admin_cleanup():
            try:
                client = osclients.Clients(self.context['admin']['credential']).trove()
                client.configurations.delete(self.context['admin_configuration'])
                LOG.debug("Configuration group '%s' deleted" % self.context['admin_configuration'])
            except Exception as e:
                msg = "Can't delete admin configuration group: %s" % e
                if logging.is_debug():
                    LOG.exception(msg)
                else:
                    LOG.warning(msg)

        _user_cleanup()
        _admin_cleanup()


@context.configure(name="create_trove_instance", order=1101)
class CreateInstance(context.Context):

    CONFIG_SCHEMA = {
        "type": "object",
        "$schema": consts.JSON_SCHEMA,
        "additionalProperties": False,
        "properties": {
            "name": {"type": "string"},
            "flavor_id": {"type": "string"},
            "volume": {
                "type": "object",
                "properties": {
                    "type": {"type": "string"},
                    "size": {
                        "type": "number",
                        "minimum": 1,
                        "maximum": 10
                    }
                }
            },
            "databases": {
                "type": "array",
                "additionalItems": True,
                "items": {
                    "type": "object"
                }
            },
            "users": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "password": {"type": "string"},
                        "databases": {
                            "type": "array",
                            "additionalItems": True,
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"}
                                }
                            }
                        },
                    }
                }
            },
            "restorePoint": {"type": "string"},
            "availability_zone": {"type": "string"},
            "datastore": {"type": "string"},
            "datastore_version": {"type": "string"},
            "nics": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "net-id": {"type": "string"}
                    }
                }
            },
            "configuration": {"type": "boolean"},
        }
    }

    def setup(self):
        # necessery parms
        kwargs = {
            "name": self.config["name"],
            "flavor_id": self.config["flavor_id"],
            "datastore": self.config["datastore"],
            "datastore_version": self.config["datastore_version"],
            "volume": self.config["volume"]
        }
        # optional parms
        databases = self.config.get("databases")
        users = self.config.get("users")
        availability_zone = self.config.get("availability_zone")

        if databases:
            kwargs["databases"] = databases
        if users:
            kwargs["users"] = users
        if availability_zone:
            kwargs["availability_zone"] = availability_zone

        def _user_setup():
            try:
                if self.config.get("configuration"):
                    kwargs["configuration"] = self.context['user_configuration']
                if self.context.get("user_network"):
                    kwargs["nics"] = []
                    kwargs["nics"].append({'net-id': self.context['user_network']})

                manager = osclients.Clients(self.context["users"][0]["credential"]).trove().instances
                self.user_instance = manager.create(**kwargs)
                self.context["user_instance"] = self.user_instance.id
                LOG.debug("User Instance With id '%s'" % self.user_instance.id)
            except Exception as e:
                msg = "Can't Create user configuration group: %s" % e
                if logging.is_debug():
                    LOG.exception(msg)
                else:
                    LOG.warning(msg)

        def _admin_setup():
            try:
                if self.config.get("configuration"):
                    kwargs["configuration"] = self.context['admin_configuration']
                if self.context.get("admin_network"):
                    kwargs["nics"] = []
                    kwargs["nics"].append({'net-id': self.context['admin_network']})

                manager = osclients.Clients(self.context["admin"]["credential"]).trove().instances
                self.admin_instance = manager.create(**kwargs)
                self.context["admin_instance"] = self.admin_instance.id
                LOG.debug("Admin Instance With id '%s'" % self.admin_instance.id)
            except Exception as e:
                msg = "Can't Create admin instance group: %s" % e
                if logging.is_debug():
                    LOG.exception(msg)
                else:
                    LOG.warning(msg)

        sleep(60)
        _user_setup()
        _admin_setup()

    def cleanup(self):

        def _delete(instance):
            utils.wait_for_status(
                instance, ['ACTIVE', 'ERROR'], ['SHUTDOWN'],
                update_resource=utils.get_from_manager(),
                timeout=3600,
                check_interval=5
            )

            try:
                instance.delete()
            except Exception as e:
                instance.force_delete()

            utils.wait_for_status(
                instance, ready_statuse=['deleted'],
                check_deletion=True,
                update_resource=utils.get_from_manager(),
                timeout=600, check_interval=10)

        def _user_cleanup():
            try:
                _delete(self.user_instance)
                LOG.debug("user instance '%s' deleted" % self.user_instance.id)
            except Exception as e:
                msg = "can't delete user instance: %s" % e
                if logging.is_debug():
                    LOG.exception(msg)
                else:
                    LOG.warning(msg)

        def _admin_cleanup():
            try:
                _delete(self.user_instance)
                LOG.debug("admin instance '%s' deleted" % self.admin_instance.id)
            except Exception as e:
                msg = "can't delete admin instance : %s" % e
                if logging.is_debug():
                    LOG.exception(msg)
                else:
                    LOG.warning(msg)

        _user_cleanup()
        _admin_cleanup()
        sleep(30)


@context.configure(name="create_trove_backups", order=1102)
class CreateBackups(context.Context):

    CONFIG_SCHEMA = {
        "type": "array",
        "$schema": consts.JSON_SCHEMA,
        "additionalItems": False,
        "items": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "name": {"type": "string"},
                "description": {"type": "string"},
            }
        }
    }

    @staticmethod
    def _check_ready(instance, manager):
        while True:
            status = manager.get(instance).status
            if status == "ACTIVE":
                break
            elif status == "ERROR":
                raise BaseException
            elif status in ("BUILD", "BACKUP"):
                continue
            else:
                raise BaseException

    def setup(self):
        user_instance, admin_instance = self.context['user_instance'], self.context['admin_instance']
        u_client = osclients.Clients(self.context['users'][0]['credential']).trove()
        a_client = osclients.Clients(self.context['admin']['credential']).trove()

        def user_backup():
            try:
                self.context['user_backups'] = []
                for back in self.config:
                    backup = u_client.backups.create(
                        user_instance,
                        name=back.get("name"),
                        description=back.get("description"))
                    self._check_ready(user_instance, u_client.instances)
                    self.context['user_backups'].append(backup.id)
                    LOG.debug("User backup With id '%s'" % backup.id)
            except Exception as e:
                msg = "can't create user backup : %s" % e
                if logging.is_debug():
                    LOG.exception(msg)
                else:
                    LOG.warning(msg)

        def admin_backup():
            try:
                self.context['admin_backups'] = []
                for back in self.config:
                    backup = a_client.backups.create(
                        admin_instance,
                        name=back.get("name"),
                        description=back.get("description"))
                    self._check_ready(admin_instance, a_client.instances)
                    self.context['admin_backups'].append(backup.id)
                    LOG.debug("Admin backup With id '%s'" % backup.id)
            except Exception as e:
                msg = "can't create admin backup : %s" % e
                if logging.is_debug():
                    LOG.exception(msg)
                else:
                    LOG.warning(msg)

        user_backup()
        admin_backup()

    def cleanup(self):
        u_client = osclients.Clients(self.context['users'][0]['credential']).trove()
        a_client = osclients.Clients(self.context['admin']['credential']).trove()

        for backup in self.context['user_backup']:
            try:
                u_client.backup.delete(backup)
                LOG.debug("User backup %s is deleted" % backup)
            except Exception as e:
                msg = "can't delete user backup : %s" % e
                if logging.is_debug():
                    LOG.exception(msg)
                else:
                    LOG.warning(msg)

        for backup in self.context['admin_backup']:
            try:
                a_client.backup.delete(backup)
                LOG.debug("Admin backup %s is deleted" % backup)
            except Exception as e:
                msg = "can't delete admin backup : %s" % e
                if logging.is_debug():
                    LOG.exception(msg)
                else:
                    LOG.warning(msg)
