#!/usr/bin/env python
# encoding: utf-8

from rally.plugins.openstack import scenario
from rally.task import atomic

"""
    1.插件类通过@scenario.configure装饰器注册。
    2.run方法将会被rally自动调用，配置文件中的
    arg参数将传递给run方法。
    3.self.clients("neutron")生成的为
    neutronclient.v2_0.client.Client类的实例，
    通过调用其接口实现对eayunstack环境进行操作。
    注意：rally自带neutronclient与测试环境中
    neutronclient存在差异，若需使用eayunstack
    独有功能需在本地Client类中添加相应的接口。
"""


@scenario.configure(name="EayunQos.list_qos")
class ListQos(scenario.OpenStackScenario):
    @atomic.action_timer("list_qos")
    def _list_qos(self):
        self.clients("neutron", 'eayun').list_eayun_qoss()

    @atomic.action_timer("list_qos_as_admin")
    def _list_qos_as_admin(self):
        self.admin_clients("neutron", 'eayun').list_eayun_qoss()

    def run(self):
        self._list_qos()
        self._list_qos_as_admin()


@scenario.configure(name="EayunQos.create_and_delete_qos")
class CreateAndDeleteQos(scenario.OpenStackScenario):
    def __init__(self, context=None, admin_clients=None, clients=None):
        self.qoss = {}
        super(CreateAndDeleteQos, self).__init__(context, admin_clients, clients)

    @atomic.action_timer("create_qos")
    def _create_qos(self, name="rally_qos", direction="ingress", rate="104000", default_rate="10400"):
        body = {
            "qos": {
                "default_rate": default_rate,
                "direction": direction,
                "rate": rate,
                "name": name,
            }
        }
        client = self.clients("neutron")
        self.qoss['user'] = client.create_eayun_qos(body)

    @atomic.action_timer("delete_qos")
    def _delete_qos(self):
        qos_id = self.qoss['user']['qos']['qos_queues'][0]['qos_id']
        self.clients("neutron").delete_eayun_qos(qos=qos_id)

    @atomic.action_timer("create_qos_as_admin")
    def _create_qos_as_admin(self):
        pass

    @atomic.action_timer("delete_qos_as_admin")
    def _delete_qos_as_admin(self):
        pass

    def run(self, name, direction, rate, default_rate):
        self._create_qos(name, direction, rate, default_rate)
