#!/usr/bin/env python
# encoding: utf-8

from rally.plugins.openstack import scenario
from rally.task import atomic


@scenario.configure(name="EayunGlance.list_images")
class ListImages(scenario.OpenStackScenario):
    @atomic.action_timer("list_qos")
    def _list_images(self):
        import pdb;pdb.set_trace()
        client = self.clients("glance")

    def run(self):
        self._list_images()
