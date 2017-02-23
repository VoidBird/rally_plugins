# Copyright 2013: Mirantis Inc.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from rally.common import logging
from rally import consts
from rally import osclients
from rally.task import context

LOG = logging.getLogger(__name__)


@context.configure(name="create_flavor", order=1000)
class CreateFlavorContext(context.Context):
    """Create sample flavor

    This sample create flavor with specified options before task starts and
    delete it after task completion.
    To create your own context plugin, inherit it from
    rally.task.context.Context
    """

    CONFIG_SCHEMA = {
        "type": "object",
        "$schema": consts.JSON_SCHEMA,
        "additionalProperties": False,
        "properties": {
            "flavor_name": {
                "type": "string",
            },
            "ram": {
                "type": "integer",
                "minimum": 1
            },
            "vcpus": {
                "type": "integer",
                "minimum": 1
            },
            "disk": {
                "type": "integer",
                "minimum": 1
            }
        }
    }

    def setup(self):
        """This method is called before the task start."""
        try:
            # use rally.osclients to get necessary client instance
            nova = osclients.Clients(
                self.context["admin"]["credential"]).nova()
            # and then do what you need with this client
            self.context["flavor"] = nova.flavors.create(
                # context settings are stored in self.config
                name=self.config.get("flavor_name", "rally_test_flavor"),
                ram=self.config.get("ram", 1),
                vcpus=self.config.get("vcpus", 1),
                disk=self.config.get("disk", 1)).to_dict()
            LOG.debug("Flavor with id '%s'" % self.context["flavor"]["id"])
        except Exception as e:
            msg = "Can't create flavor: %s" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)

    def cleanup(self):
        """This method is called after the task finish."""
        try:
            nova = osclients.Clients(
                self.context["admin"]["credential"]).nova()
            nova.flavors.delete(self.context["flavor"]["id"])
            LOG.debug("Flavor '%s' deleted" % self.context["flavor"]["id"])
        except Exception as e:
            msg = "Can't delete flavor: %s" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)


@context.configure(name="create_network", order=1500)
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
        try:
            neutron = osclients.Clients(self.context["admin"]["credential"]).neutron()
            self.context.update(
                neutron.create_network(
                    body={"network": dict(name=self.config.get("name"))}
                ))
            LOG.debug("Network with id '%s'" % self.context["network"]["id"])
        except Exception as e:
            msg = "Can't create network: %s" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)
        return self

    def cleanup(self):
        """This method is called after the task finish."""
        try:
            neutron = osclients.Clients(
                self.context["admin"]["credential"]).neutron()
            neutron.delete_network(self.context["network"]["id"])
        except Exception as e:
            msg = "Can't delete network: %s" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)


@context.configure(name="create_subnet", order=1501)
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
        try:
            neutron = osclients.Clients(
                self.context["admin"]["credential"]).neutron()
            body = {
                "subnet": {
                    "network_id": self.config.get("network_id"),
                    "allocation_pools": list(self.config.get("allocation_pools", None)),
                    "dns_nameservers": list(self.config.get("dns_nameservers", None)),
                    "cidr": self.config.get("cidr"),
                    "ip_version": self.config.get("ip_version", 4)
                }
            }
            self.context.update(neutron.create_subnet(body=body))
            LOG.debug("Subnet with id {0}".format(self.context["subnet"]["id"]))
        except Exception as e:
            msg = "Can't create subnet: %s" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)
        return self

    def cleanup(self):
        try:
            neutron = osclients.Clients(
                self.context["admin"]["credential"]).neutron()
            neutron.delete_subnet(self.context["subnet"]["id"])
            LOG.debug("Subnet '%s' deleted" % self.context["subnet"]["id"])
        except Exception as e:
            msg = "Can't delete subnet: %s" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)


@context.configure(name="create_router", order=1499)
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
        try:
            neutron = osclients.Clients(
                self.context["admin"]["credential"]).neutron()
            self.context.update(neutron.create_router(body={"router": self.config}))
            LOG.debug("Router with id {0}".format(self.context["router"]["id"]))
        except Exception as e:
            msg = "Can't create Route: %s" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)
        return self

    def cleanup(self):
        try:
            neutron = osclients.Clients(
                self.context["admin"]["credential"]).neutron()
            neutron.delete_router(self.context["router"]["id"])
            LOG.debug("Router '%s' deleted" % self.context["router"]["id"])
        except Exception as e:
            msg = "Can't delete Route: %s" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)


@context.configure(name="create_floatingip", order=1498)
class CreateFloatingIpContext(context.Context):
    CONFIG_SCHEMA={
        "type": "object",
        "$schema": consts.JSON_SCHEMA,
        "additionalProperties": False,
        "properties": {
            "floating_network_id": {
                "type": "string"
            }
        }
    }

    def setup(self):
        try:
            neutron = osclients.Clients(
                self.context["admin"]["credential"]).neutron()
            self.context.update(
                neutron.create_floatingip(
                    body={"floatingip": {"floating_network_id": self.config.get("floating_network_id")}}
                ))
            LOG.debug("FloatingIP with id {0}".format(self.context["floatingip"]["id"]))
        except Exception as e:
            msg = "Can't create Route: %s" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)
        return self

    def cleanup(self):
        try:
            neutron = osclients.Clients(
                self.context["admin"]["credential"]).neutron()
            neutron.delete_floatingip(self.context["floatingip"]["id"])
            LOG.debug("FloatingIP '%s' deleted" % self.context["floatingip"]["id"])
        except Exception as e:
            msg = "Can't delete floatingip: %s" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)
