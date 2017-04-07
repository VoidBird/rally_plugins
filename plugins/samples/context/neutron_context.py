#!/usr/bin/env python
# encoding: utf-8

from rally.common import logging
from rally import consts
from rally import osclients
from rally.task import context
from time import sleep

LOG = logging.getLogger(__name__)


@context.configure(name="create_network", order=800)
class CreateNetWorkContext(context.Context):
    CONFIG_SCHEMA = {
        "type": "object",
        "$schema": consts.JSON_SCHEMA,
        "additionalProperties": False,
        "properties": {
            "name": {"type": "string"}
        },
    }

    def setup(self):

        def _user_setup():
            try:
                neutron = osclients.Clients(self.context["users"][0]["credential"]).neutron()
                body = {"network": dict(name=self.config.get("name"))}
                self.context["user_network"] = neutron.create_network(body=body)["network"]["id"]
                LOG.debug("User Network with id '%s'" % self.context["user_network"])
            except Exception as e:
                msg = "Can't create network: %s" % e
                if logging.is_debug():
                    LOG.exception(msg)
                else:
                    LOG.warning(msg)

        def _admin_setup():
            try:
                neutron = osclients.Clients(self.context["admin"]["credential"]).neutron()
                body = {"network": dict(name=self.config.get("name"))}
                self.context["admin_network"] = neutron.create_network(body=body)["network"]["id"]
                LOG.debug("Admin Network with id '%s'" % self.context["admin_network"])
            except Exception as e:
                msg = "Can't create network: %s" % e
                if logging.is_debug():
                    LOG.exception(msg)
                else:
                    LOG.warning(msg)

        _user_setup()
        _admin_setup()
        sleep(10)

    def cleanup(self):
        """This method is called after the task finish."""

        def _user_cleanup():
            try:
                neutron = osclients.Clients(
                    self.context["users"][0]["credential"]).neutron()
                neutron.delete_network(self.context["user_network"])
                LOG.debug("User Network %s is deleted" % self.context["user_network"])
            except Exception as e:
                msg = "Can't delete network: %s" % e
                if logging.is_debug():
                    LOG.exception(msg)
                else:
                    LOG.warning(msg)

        def _admin_cleanup():
            try:
                neutron = osclients.Clients(
                    self.context["admin"]["credential"]).neutron()
                neutron.delete_network(self.context["admin_network"])
                LOG.debug("Admin Network %s is deleted" % self.context["admin_network"])
            except Exception as e:
                msg = "Can't delete network: %s" % e
                if logging.is_debug():
                    LOG.exception(msg)
                else:
                    LOG.warning(msg)

        sleep(10)
        _user_cleanup()
        _admin_cleanup()


@context.configure(name="create_subnet", order=801)
class CreateSubnetContext(context.Context):
    CONFIG_SCHEMA={
        "type": "object",
        "$schema": consts.JSON_SCHEMA,
        "additionalProperties": False,
        "properties": {
            "network_id": {"type": "string"},
            "subnet_name": {"type": "string"},
            "cidr": {"type": "string"},
            "allocation_pools": {
                "type": "array",
                "additionalItems": False,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "start": {"type": "string"},
                        "end": {"type": "string"},
                    }
                },
            },
            "dns_nameservers": {
                "type": "array",
                "items": {"type": "string"},
                "additionalItems": False,
                "uniqueItems": True
            }
        }
    }

    def setup(self):

        def _user_setup():
            try:
                neutron = osclients.Clients(
                    self.context["users"][0]["credential"]).neutron()
                body = {
                    "subnet": {
                        "network_id": self.config.get("network_id", self.context["user_network"]),
                        "dns_nameservers": self.config.get("dns_nameservers", ["114.114.114.114"]),
                        "cidr": self.config.get("cidr"),
                        "ip_version": self.config.get("ip_version", 4)
                    }
                }

                # if get allocation_pools, add into body
                if self.config.get("allocation_pools"):
                    body["subnet"]["allocation_pools"] = self.config.get("allocation_pools")

                self.context["user_subnet"] = neutron.create_subnet(body=body)["subnet"]["id"]
                LOG.debug("User Subnet with id {0}".format(self.context["user_subnet"]))
            except Exception as e:
                msg = "Can't create subnet: %s" % e
                if logging.is_debug():
                    LOG.exception(msg)
                else:
                    LOG.warning(msg)

        def _admin_setup():
            try:
                neutron = osclients.Clients(
                    self.context["admin"]["credential"]).neutron()
                body = {
                    "subnet": {
                        "network_id": self.config.get("network_id", self.context["admin_network"]),
                        "dns_nameservers": (self.config.get("dns_nameservers", ["114.114.114.114"])),
                        "cidr": self.config.get("cidr"),
                        "ip_version": self.config.get("ip_version", 4)
                    }
                }

                # if get allocation_pools, add into body
                if self.config.get("allocation_pools"):
                    body["subnet"]["allocation_pools"] = self.config.get("allocation_pools")

                self.context["admin_subnet"] = neutron.create_subnet(body=body)["subnet"]["id"]
                LOG.debug("Admin Subnet with id {0}".format(self.context["admin_subnet"]))
            except Exception as e:
                msg = "Can't create subnet: %s" % e
                if logging.is_debug():
                    LOG.exception(msg)
                else:
                    LOG.warning(msg)

        _user_setup()
        _admin_setup()
        sleep(10)

    def cleanup(self):

        def _user_cleanup():
            try:
                neutron = osclients.Clients(
                    self.context["users"][0]["credential"]).neutron()

                neutron.delete_subnet(self.context["user_subnet"])
                LOG.debug("User Subnet '%s' deleted" % self.context["user_subnet"])
            except Exception as e:
                msg = "Can't delete subnet: %s" % e
                if logging.is_debug():
                    LOG.exception(msg)
                else:
                    LOG.warning(msg)

        def _admin_cleanup():
            try:
                neutron = osclients.Clients(
                    self.context["admin"]["credential"]).neutron()

                neutron.delete_subnet(self.context["admin_subnet"])
                LOG.debug("Admin Subnet '%s' deleted" % self.context["admin_subnet"])
            except Exception as e:
                msg = "Can't delete subnet: %s" % e
                if logging.is_debug():
                    LOG.exception(msg)
                else:
                    LOG.warning(msg)

        _user_cleanup()
        _admin_cleanup()
        sleep(10)


@context.configure(name="create_router", order=802)
class CreateRouterContext(context.Context):
    CONFIG_SCHEMA={
        "type": "object",
        "$schema": consts.JSON_SCHEMA,
        "additionalProperties": False,
        "properties": {
            "name": {"type": "string"},
            "external_gateway_info": {
                "type": "object",
                "properties": {
                    "network_id": {"type": "string"}
                }
            }
        }
    }

    def setup(self):

        def _user_setup():
            try:
                neutron = osclients.Clients(
                    self.context["users"][0]["credential"]).neutron()
                self.context["user_router"] = neutron.create_router(body={"router": self.config})["router"]["id"]
                sleep(10)

                # if subnet has created, add_interface
                if self.context.get("user_subnet"):
                    neutron.add_interface_router(self.context["user_router"], {"subnet_id": self.context["user_subnet"]})
                sleep(10)

                LOG.debug("User Router with id {0}".format(self.context["user_router"]))
            except Exception as e:
                msg = "Can't create Route: %s" % e
                if logging.is_debug():
                    LOG.exception(msg)
                else:
                    LOG.warning(msg)

        def _admin_setup():
            try:
                neutron = osclients.Clients(
                    self.context["admin"]["credential"]).neutron()
                self.context["admin_router"] = neutron.create_router(body={"router": self.config})["router"]["id"]
                sleep(10)

                # if subnet has created, add_interface
                if self.context.get("admin_subnet"):
                    neutron.add_interface_router(self.context["admin_router"], {"subnet_id": self.context["admin_subnet"]})
                sleep(10)

                LOG.debug("Admin Router with id {0}".format(self.context["admin_router"]))
            except Exception as e:
                msg = "Can't create Route: %s" % e
                if logging.is_debug():
                    LOG.exception(msg)
                else:
                    LOG.warning(msg)

        _user_setup()
        _admin_setup()
        sleep(20)

    def cleanup(self):
        def _user_cleanup():
            try:
                neutron = osclients.Clients(
                    self.context["users"][0]["credential"]).neutron()

                # if subnet has created, delete_interce
                if self.context.get("user_subnet"):
                    neutron.remove_interface_router(self.context["user_router"], {"subnet_id": self.context["user_subnet"]})
                # sleep(10)

                neutron.delete_router(self.context["user_router"])
                LOG.debug("Router '%s' deleted" % self.context["user_router"])
            except Exception as e:
                msg = "Can't delete Route: %s" % e
                if logging.is_debug():
                    LOG.exception(msg)
                else:
                    LOG.warning(msg)

        def _admin_cleanup():
            try:
                neutron = osclients.Clients(
                    self.context["admin"]["credential"]).neutron()

                # if subnet has created, delete_interce
                if self.context.get("admin_subnet"):
                    neutron.remove_interface_router(self.context["admin_router"], {"subnet_id": self.context["admin_subnet"]})
                # sleep(10)

                neutron.delete_router(self.context["admin_router"])
                LOG.debug("Router '%s' deleted" % self.context["admin_router"])
            except Exception as e:
                msg = "Can't delete Route: %s" % e
                if logging.is_debug():
                    LOG.exception(msg)
                else:
                    LOG.warning(msg)

        _user_cleanup()
        _admin_cleanup()
        sleep(10)
