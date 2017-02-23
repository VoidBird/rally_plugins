#!/usr/bin/env python
# encoding: utf-8

from rally.common import logging
from rally import consts
from rally import osclients
from rally.task import context
from context_plugin import CreateNetWorkContext, CreateSubnetContext, CreateFloatingIpContext, CreateRouterContext

LOG = logging.getLogger(__name__)


@context.configure(name="net_manager", order=1200)
class Net(context.Context):
    CONFIG_SCHEMA = {
        "type": "object",
        "$schema": consts.JSON_SCHEMA,
        "additionalProperties": False,
        "properties": {
            "networks": {
                "type": "array",
                "items": CreateNetWorkContext.CONFIG_SCHEMA
            },
            "subnets": {
                "type": "array",
                "items": CreateSubnetContext.CONFIG_SCHEMA
            },
            "routers": {
                "type": "array",
                "items": CreateRouterContext.CONFIG_SCHEMA
            },
            "floatingip": CreateFloatingIpContext.CONFIG_SCHEMA
        }
    }

    def __init__(self, ctx):
        super(Net, self).__init__(ctx)
        self.old_ctx = ctx
        self.config_map = map(None, self.config.get("networks"), self.config.get("subnets"), self.config.get("routers"))
        self.client = osclients.Clients(self.context["admin"]["credential"]).neutron()
        self.context['nets'] = []
        self.resource = []

    def _create_network(self, network_conf):
        return CreateNetWorkContext(network_conf).setup()

    def _create_subnet(self, subnet_conf):
        return CreateSubnetContext(subnet_conf).setup()

    def _create_router(self, router_conf):
        return CreateRouterContext(router_conf).setup()

    def _create_floatingip(self, floatingip_conf):
        return CreateFloatingIpContext(floatingip_conf).setup()

    def setup(self):
        try:
            n_ctx, s_ctx, r_ctx, f_ctx = self.old_ctx.copy(), self.old_ctx.copy(), self.old_ctx.copy(), self.old_ctx.copy()
            n_ctx["config"], s_ctx["config"], r_ctx["config"], f_ctx["config"] = {"create_network": {}}, \
                {"create_subnet": {}}, \
                {"create_router": {}}, \
                {"create_floatingip": {}}
            for n_conf, s_conf, r_conf in self.config_map:
                n_ctx["config"]["create_network"], r_ctx["config"]["create_router"] = n_conf, r_conf
                network = self._create_network(n_ctx)
                s_conf = dict(s_conf)
                s_conf.update(dict(network_id=network.context['network']["id"]))
                s_ctx["config"]["create_subnet"] = s_conf
                subnet = self._create_subnet(s_ctx)
                router = self._create_router(r_ctx)
                self.client.add_interface_router(router.context["router"]["id"], dict(subnet_id=subnet.context['subnet']['id']))
                self.resource.append(list((network, subnet, router)))
                self.context["nets"].append(list((network.context['network'], subnet.context['subnet'], router.context['router'])))
            f_ctx["config"]["create_floatingip"] = self.config.get("floatingip")
            self.floatingip = self._create_floatingip(f_ctx)
            self.context["floatingip"] = self.floatingip.context["floatingip"]
        except Exception as e:
            msg = "Add interface Error: %s" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)

    def cleanup(self):
        try:
            self.floatingip.cleanup()
            for n, s, r in self.resource:
                self.client.remove_interface_router(r.context['router']['id'], dict(subnet_id=s.context['subnet']['id']))
                n.cleanup()
                s.cleanup()
                r.cleanup()
        except Exception as e:
            msg = "Remove interface error: %s" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)
