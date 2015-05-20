"""
This module implements a interface to docker-machine.

The current implementation is based on the docker-machine command line interface. The long term goal is to get rid of
the CLI and to support libmachine (through python bindings) out of the box.
"""

# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
import subprocess
import json
from django.core.cache import cache
from drivers.models import driver_class_by_name
import os

MACHINE_BIN = os.getenv("MACHINERY_DOCKER_MACHINE_BIN", "/usr/local/bin/docker-machine")


def get_machine_details(name, cached=False):
    """
    Get the details of a machine.

    :param name: The name of the machine
    :param cached: Use the cache
    :return: dict containing all machine details, None if the machine can't be found
    """
    machines = machines_ls(cached=cached)
    # iter over machine_ls. If the machine is there, return it.
    # We have to iter over machine ls because this is the only way to get the machine state.
    if machines is not None:
        for machine in machines:
            if name == machine["name"]:
                return machine
    return None


def machines_ls(cached=False):
    """
    Get a detailed list of machines.

    :param cached: Use the cache
    :return: list of machines
    """

    # if cached is True, return early
    if cached:
        return cache.get("machines_ls")

    process = subprocess.Popen([MACHINE_BIN, "ls"], stdout=subprocess.PIPE)
    out, err = process.communicate()

    machines = []
    header = False

    #
    for line in out.splitlines():

        # machine ls can yield some errors at the beginning. Mark the table header so that we don't accidentially
        # parse error messages as machines
        if line.startswith("NAME"):
            header = True
            continue

        if header:
            # parse the machine
            data = line.split()
            name = data[0]
            line = line.replace(name, "")

            # as of docker-machine 0.2 there is no way to get the machines state using the CLI. We have to parse
            # it from the table
            if "Running" in line:
                state = "running"
            elif "Stopped" in line:
                state = "stopped"
            else:
                state = "unknown"

            # add some more details
            inspect = machine_inspect(name)

            machines.append({
                "name": name,
                "state": state,
                "inspect": inspect,
                "driver_class": driver_class_by_name(inspect.get("DriverName", None)),
                "ip": machine_ip(name),
                "url": machine_url(name)}
            )

    # write this in the cache
    cache.set("machines_ls", machines, 60*5)
    return machines


def machine_inspect(name):
    """
    Inspect a machine

    :param name: name of the machine
    :return: dict
    """
    process = subprocess.Popen([MACHINE_BIN, "inspect", name], stdout=subprocess.PIPE)
    out, err = process.communicate()

    return json.loads(out)


def machine_ip(name):
    """
    Get the IP for a machine

    :param name: name of the machine
    :return: ip address string
    """
    process = subprocess.Popen([MACHINE_BIN, "ip", name], stdout=subprocess.PIPE)
    out, err = process.communicate()

    return out


def machine_url(name):
    """
    Get the URL for a machine

    :param name: name of the machine
    :return: url string
    """
    process = subprocess.Popen([MACHINE_BIN, "url", name], stdout=subprocess.PIPE)
    out, err = process.communicate()

    return out


def machine_rm(name, force=False):
    """
    Remove a machine

    :param name: name of the machine
    :return: cli output
    """
    command = [MACHINE_BIN, "rm", name]

    if force:
        command.append("-f")

    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    out, err = process.communicate()
    process.wait()
    return process.returncode == 0, out


def run(command):
    """
    Runs a command using subprocess.Popen. Yields the output from stdout.


    :param command: list or string
    """

    print("running", command)

    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    for line in iter(process.stdout.readline, ''):
        yield line

    process.wait()
    yield process.returncode