#!/usr/bin/env python
# encoding: utf-8

from rally.task import utils


def check_ready(instance):

    utils.wait_for_status(
        instance, update_resource=utils.get_from_manager(),
        ready_statuses=["ACTIVE"],
        failure_statuses=["ERROR"],
        timeout=5400,
        check_interval=30)


# TODO add dedecorator like this:
# def decorator(fun):
#     def warpper(*args, **kwargs):
#         change_status(*args[: -1])
#         return fun(*args, **kwargs)
#
# use like this:
# @staticmethod
# @decorator
# def fun()....

def change_status(instance, status, c_manager=None):

    if status == "ACTIVE":
        check_ready(instance)
    elif status in ("BUILD", "ERROR"):
        utils.wait_for_status(instance, ready_statuses=[status],
                              update_resource=utils.get_from_manager(), timeout=5400, check_interval=60)
    elif status == "REBOOT":
        check_ready(instance)
        instance.restart()
        utils.wait_for_status(instance,
                              update_resource=utils.get_from_manager(), ready_statuses=[status])
    elif status == "RESTART_REQUIRED":
        conf_parm = {
            "name": "rally_configuration",
            "values": '{"performance_schema": true}',
            "datastore": "mysql",
            "datastore_version": "5.5"
        },
        conf = c_manager.create(**conf_parm)
        instance.manager.edit(instance, configuration=conf)
        utils.wait_for_status(instance,
                              update_resource=utils.get_from_manager(), ready_statuse=[status])
    else:
        raise BaseException
