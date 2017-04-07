#!/usr/bin/env python
# encoding: utf-8

from rally.common import logging
from rally import consts
from rally import osclients
from rally.task import context
from time import sleep

LOG = logging.getLogger(__name__)


@context.configure(name="create_volume_type", order=1200)
class CreateVolumeType(context.Context):
    CONFIG_SCHEMA = {
        "type": "object",
        "$schema": consts.JSON_SCHEMA,
        "additionalProperties": False,
        "properties": {
            "name": {"type": "string"}
        }
    }

    def setup(self):
        try:
            manager = osclients.Clients(self.context["admin"]["credential"]).cinder().volume_types

            # add function to delete volume_type which has name as same as which you want to use
            for v_type in manager.list():
                if v_type.name == self.config.get("name", "rally_type"):
                    manager.delete(v_type)

            self.volume_type = manager.create(name=self.config.get("name", "rally_type"))
            self.context["volume_type"] = self.volume_type.id
            sleep(20)
            LOG.debug("Voluem Type %s Created" % self.volume_type.name)
        except Exception as e:
            msg = "Can't create volume_type: %s" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)

    def cleanup(self):
        try:
            manager = osclients.Clients(
                self.context["admin"]["credential"]).cinder().volume_types
            manager.delete(self.volume_type)
            LOG.debug("Voluem Type %s Deleted" % self.volume_type.id)
        except Exception as e:
            msg = "Can't create volume_type: %s" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)
