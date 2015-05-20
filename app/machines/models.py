from __future__ import absolute_import, print_function, unicode_literals

import os
from django.db import models
from .core import run, machines_ls
from jsonfield import JSONField

MACHINE_BIN = os.getenv("MACHINERY_DOCKER_MACHINE_BIN", "/usr/local/bin/docker-machine")

class Job(models.Model):
    """
    Model that holds information about a job.
    """

    started = models.BooleanField(default=False)
    name = models.CharField(max_length=40)
    params = JSONField()
    output = models.TextField()

    @property
    def command(self):
        return " ".join(self.format_command())

    def format_command(self):
        return self._create_params()

    def _create_params(self):

        cli_params = [MACHINE_BIN, "create", self.params["name"]]

        if self.params["swarm"].get("enable_swarm"):
            self.params["swarm"].pop("enable_swarm")
            cli_params.append("--swarm")
            cli_params.extend(self._construct_cli(self.params["swarm"]))

        cli_params.extend(self._construct_cli(self.params["driver"]))
        cli_params.extend(self._construct_cli(self.params["settings"]))

        return cli_params

    @staticmethod
    def _construct_cli(dic):
        """
        Iter over all key value pairs to construct a string containing the key and (optionally) the value.
        If we have a boolean value the parameter looks like this `--swarm-master` and key value pairs for everything else
        `--swarm-discovery=token://`
        """

        params = []

        for k, v in dic.iteritems():

            # add a -- to the beginning and replace all underscores with dashes
            key = "--" + k.replace("_", "-")

            # if the value is a boolean and true we only add the key
            if isinstance(v, bool):
                if v:
                    params.append(key)
            # otherwise we'll only add values that are not empty
            else:
                if v not in [None, ""]:
                    params.append(key + "=" + str(v))

        return params

    def run(self):
        """
        Runs the saved command and save all output.
        """

        returncode = None

        for item in run(self.format_command()):
            if isinstance(item, int):
                returncode = item
                break

            self.output += item
            self.save()

        # run machines ls to update the cache
        machines_ls()

        return returncode == 0


class SwarmToken(models.Model):

    token = models.CharField(max_length=100)
