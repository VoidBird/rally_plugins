#!/usr/bin/env python
# encoding: utf-8
from rally.common import logging
from rally import consts
from rally import osclients
from rally.task import context

LOG = logging.getLogger(__name__)


@context.configure(name="create_conf", order=1100)
class CreateConfigurations(context.Context):

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
                self.context['user_configuration'] = configuration.to_dict()
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
                self.context['admin_configuration'] = configuration.to_dict()
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
                client.configurations.delete(self.context['user_configuration']['id'])
                LOG.debug("Configuration group '%s' deleted" % self.context['user_configuration']['id'])
            except Exception as e:
                msg = "Can't delete user configuration group: %s" % e
                if logging.is_debug():
                    LOG.exception(msg)
                else:
                    LOG.warning(msg)

        def _admin_cleanup():
            try:
                client = osclients.Clients(self.context['admin']['credential']).trove()
                client.configurations.delete(self.context['admin_configuration']['id'])
                LOG.debug("Configuration group '%s' deleted" % self.context['admin_configuration']['id'])
            except Exception as e:
                msg = "Can't delete admin configuration group: %s" % e
                if logging.is_debug():
                    LOG.exception(msg)
                else:
                    LOG.warning(msg)

        _user_cleanup()
        _admin_cleanup()
