# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
from django.test import TestCase


# Create your tests here.
class ConstrucCLIStringTestCase(TestCase):

    def test_swarm(self):

        from .core import construct_cli_string

        dic = {
            "swarm_master": True,
            "swarm_discovery": "token://foo.bar",
            "swarm_host": "",
            "swarm_addr": None
        }

        string = construct_cli_string(dic)
        self.assertEquals(string, "--swarm-master --swarm-discovery=token://foo.bar")
