# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
from django.db import models
from . import forms
from django.forms import modelform_factory
from django.conf import settings
from django.forms import model_to_dict


class DriverMixin(object):
    """
    Baseclass that adds some utility methods to the Driver classes.

    All drivers (CloudDriver and LocalDriver) should have this class as a parent.
    """

    @classmethod
    def form_class(cls):
        """
        Returns the form class for the driver.
        
        Tries to auto import a custom form from the forms module first. If there is no custom form, returns the default
        DriverForm.
        
        To add a custom form for a driver, add a form to the forms module and name it like your class with `Form` as
        suffix. e.g:
        
        If your driver is named `AWS`, a custom form would look like this:
        
        `class AWSForm(DriverForm):
            pass`
        """
        try:
            classname = cls.identifier() + "Form"
            form_module = __import__("drivers.forms", fromlist=[classname])
            return getattr(form_module, classname)
        except (ImportError, AttributeError), e:
            return forms.DriverForm

    @classmethod
    def settings_form_class(cls):
        """
        Returns the settings form class for the driver.
        
        Tries to auto import a custom form from the forms module first. If there is no custom form, returns the default
        SettingsForm.
        
        To add a custom form for a driver setting, add a form to the forms module and name it like your class with 
        `SettingsForm` as suffix. e.g:
        
        If your driver is named `AWS`, a custom settings form would look like this:
        
        `class AWSSettingsForm(SettingsForm):
            pass`
        """
        try:
            classname = cls.identifier() + "SettingsForm"
            form_module = __import__("drivers.forms", fromlist=[classname])
            return getattr(form_module, classname)
        except (ImportError, AttributeError), e:
            return forms.SettingsForm

    @classmethod
    def form(cls):
        """
        Returns the driver form for this model from a modelform factory.
        """
        return modelform_factory(model=cls, form=cls.form_class())

    @classmethod
    def settings_form(cls):
        """
        Returns the settings form for this model from a modelform factory.
        """
        return modelform_factory(model=cls.settings_class(), form=cls.settings_form_class(), fields="__all__")

    @classmethod
    def settings_class(cls):
        """
        Returns the settings class for the driver.

        Auto imports the settings by name: FooDriver -> FooDriverSettings
        """
        # django auto imports all related fields during startup. This leads to problems for our use case, because all
        # related settings are auto imported and wired together by name. If the class.__name__ is DriverMixin, we
        # return 'self' as the related field to fix that.
        if cls.identifier() == "DriverMixin":
            return "self"
        classname = cls.identifier() + "Settings"
        form_module = __import__("drivers.models", fromlist=[classname])
        return getattr(form_module, classname)

    @classmethod
    def logo(cls):
        """
        Returns the path to the logo for the driver
        """
        return "/".join([settings.STATIC_URL, "img/drivers", cls.Properties.logo])

    @classmethod
    def identifier(cls):
        """
        Returns the classes __name__
        """
        return cls.__name__

    @classmethod
    def driver_name(cls):
        """
        Returns the human readable driver name
        """
        return cls.Properties.name

    @property
    def as_dict(self):
        dic = model_to_dict(self, exclude=("settings", "id", "name"))
        dic["driver"] = self.__class__.Properties.driver
        return dic


class CloudDriver(DriverMixin, models.Model):
    """
    Abstract baseclass for all cloud drivers.

    All drivers that inherit from this class have to implement a Properties class that holds some meta information
    about the driver

    e.g:

    `class Properties:
        logo = "digital-ocean.png"
        name = "Digital Ocean"
        driver = "digitalocean"`

    Where:
        - logo: name of the logo file in static/img/drivers
        - name: the human readable (verbose) name of the driver
        - driver: the name of the driver as specified by docker
    """

    name = models.CharField(
        max_length=50,
        blank=False,
        verbose_name="Name",
                            help_text="Unique name for your login details."
    )

    settings = models.OneToOneField(DriverMixin.settings_class(), null=True, blank=True)

    class Meta:
        abstract = True


class LocalDriver(DriverMixin, models.Model):
    """
    Abstract baseclass for all cloud drivers.

    All drivers that inherit from this class have to implement a Properties class that holds some meta information
    about the driver

    e.g:

    `class Properties:
        logo = "digital-ocean.png"
        name = "Digital Ocean"
        driver = "digitalocean"`

    Where:
        - logo: name of the logo file in static/img/drivers
        - name: the human readable (verbose) name of the driver
        - driver: the name of the driver as specified by docker
    """

    settings = models.OneToOneField(DriverMixin.settings_class(), null=True, blank=True)

    class Meta:
        abstract = True


class AWS(CloudDriver):
    """
    --amazonec2-access-key: required Your access key id for the Amazon Web Services API.
    --amazonec2-ami: The AMI ID of the instance to use Default: ami-4ae27e22
    --amazonec2-instance-type: The instance type to run. Default: t2.micro
    --amazonec2-iam-instance-profile: The AWS IAM role name to be used as the instance profile
    --amazonec2-region: The region to use when launching the instance. Default: us-east-1
    --amazonec2-root-size: The root disk size of the instance (in GB). Default: 16
    --amazonec2-secret-key: required Your secret access key for the Amazon Web Services API.
    --amazonec2-security-group: AWS VPC security group name. Default: docker-machine
    --amazonec2-session-token: Your session token for the Amazon Web Services API.
    --amazonec2-subnet-id: AWS VPC subnet id
    --amazonec2-vpc-id: required Your VPC ID to launch the instance in.
    --amazonec2-zone: The AWS zone launch the instance in (i.e. one of a,b,c,d,e). Default: a
    """

    class Properties:
        logo = "aws.png"
        name = "Amazon EC2"
        driver = "amazonec2"

    amazonec2_access_key = models.CharField(
        max_length=50,
        verbose_name="Access Key",
        help_text="Your access key id for the Amazon Web Services API"
    )

    amazonec2_secret_key = models.CharField(
        max_length=50,
        verbose_name="Secret Key",
        help_text="Your secret access key for the Amazon Web Services API"
    )


class AWSSettings(models.Model):
    REGIONS = [
        "ap-northeast-1", "ap-southeast-1", "ap-southeast-2", "cn-north-1", "eu-west-1", "eu-central-1", "sa-east-1",
        "us-east-1", "us-west-1", "us-west-2", "us-gov-west-1"
    ]

    AMIS = [
        "ami-44f1e245", "ami-f95875ab", "ami-890b62b3", "ami-fe7ae8c7", "ami-823686f5", "ami-ac1524b1", "ami-c770c1da",
        "ami-4ae27e22", "ami-d1180894", "ami-898dd9b9", "ami-cf5630ec"
    ]

    INSTANCES = [
        'c1.medium', 'c1.xlarge', 'c3.2xlarge', 'c3.4xlarge', 'c3.8xlarge', 'c3.large', 'c3.xlarge', 'c4.2xlarge',
        'c4.4xlarge', 'c4.8xlarge', 'c4.large', 'c4.xlarge', 'cc2.8xlarge', 'cg1.4xlarge', 'cr1.8xlarge', 'd2.2xlarge',
        'd2.4xlarge', 'd2.8xlarge', 'd2.xlarge', 'g2.2xlarge', 'g2.8xlarge', 'hi1.4xlarge', 'hs1.8xlarge',
        'i2.2xlarge', 'i2.4xlarge', 'i2.8xlarge', 'i2.xlarge', 'm1.large', 'm1.medium', 'm1.small', 'm1.xlarge',
        'm2.2xlarge', 'm2.4xlarge', 'm2.xlarge', 'm3.2xlarge', 'm3.large', 'm3.medium', 'm3.xlarge', 'r3.2xlarge',
        'r3.4xlarge', 'r3.8xlarge', 'r3.large', 'r3.xlarge', 't1.micro', 't2.medium', 't2.micro', 't2.small'
    ]

    ZONES = [
        "a", "b", "c", "d", "e"
    ]

    amazonec2_ami = models.CharField(
        max_length=50,
        verbose_name="AMI",
        choices=[(ami, ami) for ami in AMIS],
        default="ami-4ae27e22",
        help_text="The AMI ID of the instance to use",
        blank=True
    )
    amazonec2_instance_type = models.CharField(
        max_length=50, verbose_name="Instance Type",
        choices=[(inst, inst) for inst in INSTANCES],
        default="t2.micro",
        help_text="The instance type to run",
        blank=True
    )
    amazonec2_iam_instance_profile = models.CharField(
        max_length=50,
        verbose_name="IAM Role",
        blank=True,
        help_text="The AWS IAM role name to be used as the instance profile")
    amazonec2_region = models.CharField(
        max_length=50,
        verbose_name="Region",
        choices=[(reg, reg) for reg in REGIONS],
        default="us-east-1",
        help_text="The region to use when launching the instance",
        blank=True
    )
    amazonec2_root_size = models.PositiveIntegerField(
        default=16,
        verbose_name="Disk Size",
        blank=True,
        help_text="The root disk size of the instance (in GB)"
    )

    amazonec2_security_group = models.CharField(
        max_length=50,
        blank=True,
        help_text="AWS VPC security group name. Default: docker-machine"
    )
    amazonec2_session_token = models.CharField(
        max_length=50,
        verbose_name="Session Token",
        help_text="Your session token for the Amazon Web Services API.",
        blank=True
    )
    amazonec2_subnet_id = models.CharField(
        max_length=50,
        verbose_name="Subnet ID",
        help_text="AWS VPC subnet id",
        blank=True)
    amazonec2_vpc_id = models.CharField(
        max_length=50,
        verbose_name="VPC ID",
        help_text="Your VPC ID to launch the instance in.")
    amazonec2_zone = models.CharField(
        max_length=50,
        verbose_name="AWS Zone",
        choices=[(zone, zone) for zone in ZONES],
        help_text="The AWS zone launch the instance in",
        default="a", blank=True
    )


class DigitalOcean(CloudDriver):
    """
    --digitalocean-access-token: Your personal access token for the Digital Ocean API.
    --digitalocean-image: The name of the Digital Ocean image to use. Default: docker
    --digitalocean-region: The region to create the droplet in, see Regions API for how to get a list. Default: nyc3
    --digitalocean-size: The size of the Digital Ocean droplet (larger than default options are of the form 2gb). Default: 512mb
    --digitalocean-ipv6: Enable IPv6 support for the droplet. Default: false
    --digitalocean-private-networking: Enable private networking support for the droplet. Default: false
    --digitalocean-backups: Enable Digital Oceans backups for the droplet. Default: false
    """

    class Properties:
        logo = "digital-ocean.png"
        name = "Digital Ocean"
        driver = "digitalocean"

    digitalocean_access_token = models.CharField(
        max_length=100,
        blank=False,
        verbose_name="Access Token",
        help_text="Your personal access token for the Digital Ocean API"
    )


class DigitalOceanSettings(models.Model):
    SIZES = [
        "512mb", "1gb", "2gb", "4gb", "8gb", "16gb", "32gb", "48gb", "64gb"
    ]

    REGIONS = [
        ('ams1', 'Amsterdam 1'), ('ams2', 'Amsterdam 2'), ('ams3', 'Amsterdam 3'), ('fra1', 'Frankfurt 1'),
        ('lon1', 'London 1'), ('nyc1', 'New York 1'), ('nyc2', 'New York 2'), ('nyc3', 'New York 3'),
        ('sfo1', 'San Francisco 1'), ('sgp1', 'Singapore 1')
    ]

    digitalocean_image = models.CharField(
        max_length=50,
        blank=False,
        verbose_name="Image",
        default="docker",
        help_text="The name of the Digital Ocean image to use"
    )
    digitalocean_region = models.CharField(
        max_length=50,
        blank=False,
        verbose_name="Region",
        choices=REGIONS,
        default="nyc3",
        help_text="The region to create the droplet in, see Regions API for how to get a list"
    )
    digitalocean_size = models.CharField(
        max_length=50,
        blank=False,
        verbose_name="Droplet",
        default="512mb",
        choices=[(size, size.upper()) for size in SIZES],
        help_text="The size of the Digital Ocean droplet"
    )
    digitalocean_ipv6 = models.BooleanField(
        default=False,
        verbose_name="Enable IPv6",
        help_text="Enable IPv6 support for the droplet"
    )
    digitalocean_private_networking = models.BooleanField(
        default=False,
        verbose_name="Private Networking",
        help_text="Enable private networking support for the droplet"
    )
    digitalocean_backups = models.BooleanField(
        default=False,
        verbose_name="Backups",
        help_text="Enable Digital Oceans backups for the droplet"
    )


class Google(CloudDriver):
    """
    --google-zone: The zone to launch the instance. Default: us-central1-a
    --google-machine-type: The type of instance. Default: f1-micro
    --google-username: The username to use for the instance. Default: docker-user
    --google-instance-name: The name of the instance. Default: docker-machine
    --google-project: The name of your project to use when launching the instance.
    """

    class Properties:
        logo = "googlecloud.png"
        name = "Google Cloud Platform"
        driver = "google"


class GoogleSettings(models.Model):
    ZONES = [
        "us-central1-a", "us-central1-b", "us-central1-c", "us-central1-f", "europe-west1-b", "europe-west1-c",
        "europe-west1-d", "asia-east1-a", "asia-east1-b", "asia-east1-c",
    ]

    MACHINES = [
        "f1-micro", "g1-small", "n1-standard-1", "n1-standard-2", "n1-standard-4", "n1-standard-8", "n1-standard-16",
        "n1-standard-32", "n1-highmem-2", "n1-highmem-4", "n1-highmem-8", "n1-highmem-16", "n1-highmem-32",
        "n1-highcpu-2", "n1-highcpu-4", "n1-highcpu-8", "n1-highcpu-16", "n1-highcpu-32",
    ]

    google_username = models.CharField(
        max_length=50,
        blank=False,
        verbose_name="Username",
        default="docker-user",
        help_text="The username to use for the instance"
    )

    google_zone = models.CharField(
        max_length=50,
        blank=False,
        verbose_name="Zone",
        default="us-central1-a",
        help_text="The zone to launch the instance",
        choices=[(zone, zone) for zone in ZONES]
    )
    google_machine_type = models.CharField(
        max_length=50,
        blank=False,
        verbose_name="Instance",
        default="f1-micro",
        choices=[(mach, mach) for mach in MACHINES],
        help_text="The type of instance"
    )

    google_instance_name = models.CharField(
        max_length=50,
        blank=False,
        verbose_name="Instance Name",
        default="docker-machine",
        help_text="The name of the instance"
    )
    google_project = models.CharField(
        max_length=50,
        blank=False,
        verbose_name="Project",
        help_text="The name of your project to use when launching the instance"
    )


class Softlayer(CloudDriver):
    """
    --softlayer-user: required username for your softlayer account, api key needs to match this user.
    --softlayer-api-key: required API key for your user account
    --softlayer-domain: required domain name for the machine
    --softlayer-api-endpoint: Change softlayer API endpoint
    --softlayer-cpu: Number of CPU's for the machine.
    --softlayer-disk-size: Size of the disk in MB.0` sets the softlayer default.
    --softlayer-hostname: hostname for the machine
    --softlayer-hourly-billing: Sets the hourly billing flag (default), otherwise uses monthly billing
    --softlayer-image: OS Image to use
    --softlayer-local-disk: Use local machine disk instead of softlayer SAN.
    --softlayer-memory: Memory for host in MB
    --softlayer-private-net-only: Disable public networking
    --softlayer-region: softlayer region
    """

    class Properties:
        logo = "softlayer.png"
        name = "Softlayer"
        driver = "softlayer"

    softlayer_user = models.CharField(
        max_length=50,
        blank=False,
        verbose_name="Username",
        help_text="username for your softlayer account, api key needs to match this user"
    )
    softlayer_api_key = models.CharField(
        max_length=50,

        blank=False,
        verbose_name="API Key",
        help_text="API key for your user account"
    )


class SoftlayerSettings(models.Model):
    REGIONS = [
        ('AMS01', 'Amsterdam 1'),
        ('AMS03', 'Amsterdam 3'),
        ('DAL01', 'Dallas 1'),
        ('DAL05', 'Dallas 5'),
        ('DAL06', 'Dallas 6'),
        ('DAL09', 'Dallas 9'),
        ('FRA02', 'Frankfurt 2'),
        ('HKG02', 'Hong Kong 2'),
        ('HOU02', 'Houston 2'),
        ('LON02', 'London 2'),
        ('MEL01', 'Melbourne 1'),
        ('MEX01', 'Queretaro 1'),
        ('MON01', 'Montreal 1'),
        ('PAR01', 'Paris 1'),
        ('SJC01', 'San Jose 1'),
        ('SEA01', 'Seattle 1'),
        ('SNG01', 'Singapore 1'),
        ('SYD01', 'Sydney 1'),
        ('TOK02', 'Tokyo 2'),
        ('TOR01', 'Toronto 1'),
        ('WDC01', 'Washington, DC 1')
    ]

    softlayer_domain = models.CharField(
        max_length=50,
        blank=False,
        verbose_name="Domain",
        help_text="domain name for the machine"
    )
    softlayer_api_endpoint = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="API Endpoint",
        help_text="Change softlayer API endpoint"
    )
    softlayer_cpu = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="CPUs",
        help_text="Number of CPU's for the machine."
    )
    softlayer_disk_size = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Disk Size",
        help_text="Size of the disk in MB.0` sets the softlayer default."
    )

    softlayer_hostname = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Hostname",
        help_text="hostname for the machine"
    )
    softlayer_hourly_billing = models.BooleanField(
        default=True,
        verbose_name="Hourly Billing",
        help_text="Sets the hourly billing flag (default), otherwise uses monthly billing"
    )
    softlayer_image = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Image",
        help_text="OS Image to use"
    )
    softlayer_local_disk = models.BooleanField(
        verbose_name="Local Disk",
        help_text="Use local machine disk instead of softlayer SAN."
    )
    softlayer_memory = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="RAM",
        help_text="Memory for host in MB"
    )
    softlayer_private_net_only = models.BooleanField(
        verbose_name="Disable Public Networking",
        help_text="Disable public networking"
    )
    softlayer_region = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Region",
        help_text="softlayer region"
    )


class Azure(CloudDriver):
    """
    --azure-subscription_id: Your Azure subscription ID (A GUID like d255d8d7_5af0-4f5c-8a3e-1545044b861e).
    --azure-subscription-cert: Your Azure subscription cert.
    """

    class Properties:
        logo = "azure.png"
        name = "Microsoft Azure"
        driver = "azure"

    azure_subscription_id = models.CharField(
        max_length=50,
        blank=False,
        verbose_name="Subscription ID",
        help_text="Your Azure subscription ID (A GUID like d255d8d7_5af0-4f5c-8a3e-1545044b861e)"
    )
    azure_subscription_cert = models.FileField(
        verbose_name="Subscription Cert",
        help_text="Your Azure subscription cert as .pem file"
    )

    @property
    def as_dict(self):
        return {
            "azure_subscription_id": self.azure_subscription_id,
            "azure_subscription_cert": self.azure_subscription_cert.path,
            "driver": self.__class__.Properties.driver
        }


class AzureSettings(models.Model):
    """
    --azure-docker-port "2376"	Azure Docker port
    --azure-image Azure image name. Default is Ubuntu 14.04 LTS x64 [$AZURE_IMAGE]
    --azure-location "West US"	Azure location [$AZURE_LOCATION]
    --azure-password Azure user password
    --azure-size "Small"	Azure size [$AZURE_SIZE]
    --azure-ssh-port "22"	Azure SSH port
    --azure-username "ubuntu" Azure username
    """

    LOCATIONS = ["East US", "East US 2", "Central US", "South Central US", "West US", "North Europe", "West Europe",
                 "East Asia", "Southeast Asia", "Japan West"]

    SIZES = ["ExtraSmall", "Small", "Medium", "Large", "ExtraLarge", "A5", "A6", "A7", "A8", "A9", "A10", "A11",
             "Standard_D1", "Standard_D2", "Standard_D3", "Standard_D4", "Standard_D11", "Standard_D12", "Standard_D13",
             "Standard_D14"]

    azure_docker_port = models.IntegerField(
        default=2376,
        verbose_name="Docker Port",
        help_text="Azure Docker port"
    )
    # azure_image = models.CharField(
    # max_length=100,
    # default="Ubuntu 14.04 LTS x64",
    #   verbose_name="Image",
    #   help_text="Azure Image"
    # )
    azure_location = models.CharField(
        max_length=30,
        default="West US",
        verbose_name="Region",
        help_text="Azure Region",
        choices=[(loc, loc) for loc in LOCATIONS]
    )
    azure_password = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="User Password",
        help_text="Azure user password"
    )
    azure_size = models.CharField(
        max_length=50,
        default="Small",
        verbose_name="Size",
        help_text="Azure size",
        choices=[(size, size) for size in SIZES]
    )
    azure_ssh_port = models.IntegerField(
        default=22,
        verbose_name="SSH Port",
        help_text="Azure SSH port"
    )
    azure_username = models.CharField(
        max_length=50,
        default="ubuntu",
        verbose_name="Azure username"
    )


class HyperV(LocalDriver):
    """
    --hyper-v-boot2docker-location: Location of a local boot2docker iso to use. Overrides the URL option below.
    --hyper-v-boot2docker-url: The URL of the boot2docker iso. Defaults to the latest available version.
    --hyper-v-disk-size: Size of disk for the host in MB. Defaults to 20000.
    --hyper-v-memory: Size of memory for the host in MB. Defaults to 1024. The machine is setup to use dynamic memory.
    --hyper-v-virtual-switch: Name of the virtual switch to use. Defaults to first found.

    """

    class Properties:
        logo = "hyperv.png"
        name = "Microsoft HyperV"
        driver = "hyper-v"


class HyperVSettings(models.Model):
    hyper_v_boot2docker_location = models.CharField(
        max_length=100,
        blank=False,
        verbose_name="Boot2Docker Location",
        help_text="Location of a local boot2docker iso to use. Overrides the URL option below."
    )
    hyper_v_boot2docker_url = models.URLField(
        blank=True,
        verbose_name="Boot2Docker URL",
        help_text="The URL of the boot2docker iso. Defaults to the latest available version."
    )
    hyper_v_disk_size = models.IntegerField(
        default=20000,
        null=True,
        blank=True,
        verbose_name="Disk Size",
        help_text="Size of disk for the host in MB."
    )
    hyper_v_memory = models.IntegerField(
        default=1024,
        null=True,
        blank=True,
        verbose_name="RAM",
        help_text="Size of memory for the host in MB. The machine is setup to use dynamic memory."
    )
    hyper_v_virtual_switch = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Virtual Switch",
        help_text="Name of the virtual switch to use. Defaults to first found"
    )


class Openstack(CloudDriver):
    """
    --openstack-flavor-id or openstack-flavor-name: Identify the flavor that will be used for the machine.
    --openstack-image-id or openstack-image-name: Identify the image that will be used for the machine.
    --openstack-auth-url: Keystone service base URL.
    --openstack-domain-name or --openstack-domain-id: Domain to use for authentication (Keystone v3 only)
    --openstack-username: User identifer to authenticate with.
    --openstack-password: User password. It can be omitted if the standard environment variable OS_PASSWORD is set.
    --openstack-tenant-name or --openstack-tenant-id: Identify the tenant in which the machine will be created.
    --openstack-region: The region to work on. Can be omitted if there is ony one region on the OpenStack.
    --openstack-endpoint-type: Endpoint type can be internalURL, adminURL on publicURL. If is a helper for the CloudDriver to choose the right URL in the OpenStack service catalog. If not provided the default id publicURL
    --openstack-net-id or --openstack-net-name: Identify the private network the machine will be connected on. If your OpenStack project project contains only one private network it will be use automatically.
    --openstack-sec-groups: If security groups are available on your OpenStack you can specify a comma separated list to use for the machine (e.g. secgrp001,secgrp002).
    --openstack-floatingip-pool: The IP pool that will be used to get a public IP an assign it to the machine. If there is an IP address already allocated but not assigned to any machine, this IP will be chosen and assigned to the machine. If there is no IP address already allocated a new IP will be allocated and assigned to the machine.
    --openstack-ssh-user: The username to use for SSH into the machine. If not provided root will be used.
    --openstack-ssh-port: Customize the SSH port if the SSH server on the machine does not listen on the default port.
    --openstack-insecure: Explicitly allow openstack CloudDriver to perform "insecure" SSL (https) requests. The server's certificate will not be verified against any certificate authorities. This option should be used with caution
    """

    class Properties:
        logo = "openstack.png"
        name = "Openstack"
        driver = "openstack"

    openstack_username = models.CharField(
        max_length=100,
        blank=False,
        verbose_name="Username",
        help_text="User identifer to authenticate with."
    )
    openstack_password = models.CharField(
        max_length=50,
        blank=False,
        verbose_name="Password",
        help_text="User password."
    )
    openstack_auth_url = models.URLField(
        max_length=400,
        blank=False,
        verbose_name="Auth URL",
        help_text="Keystone service base URL."
    )




class OpenstackSettings(models.Model):

    ENDPOINTS = ["internalURL", "adminURL", "publicURL"]

    openstack_flavor_id = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Flavor ID",
        help_text=" Identify the flavor that will be used for the machine."
    )
    openstack_flavor_name = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Flavor Name",
        help_text=" Identify the flavor that will be used for the machine."
    )
    openstack_image_id = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Image ID",
        help_text="Identify the image that will be used for the machine."
    )
    openstack_image_name = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Image Name",
        help_text="Identify the image that will be used for the machine."
    )

    openstack_tenant_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Tenant ID",
        help_text="Identify the tenant in which the machine will be created."
    )

    openstack_tenant_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Tenant Name",
        help_text="Identify the tenant in which the machine will be created."
    )

    openstack_net_id = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Net ID",
        help_text="Identify the private network the machine will be connected on. If  your OpenStack  project "
                  "contains only one private network it will be use automatically."
    )
    openstack_net_name = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Net Name",
        help_text="Identify the private network the machine will be connected on. If your OpenStack project contains "
                  "only one private network it will be use automatically."
    )

    openstack_domain_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Domain Name",
        help_text="Domain to use for authentication (Keystone v3 only)"
    )
    openstack_domain_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Domain ID",
        help_text="Domain to use for authentication (Keystone v3 only)"
    )

    openstack_region = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Region",
        help_text="The region to work on. Can be omitted if there is ony one region on the OpenStack."
    )
    openstack_endpoint_type = models.CharField(
        max_length=50,
        blank=False,
        verbose_name="Endpoint",
        choices=[(endp, endp) for endp in ENDPOINTS],
        default="publicURL",
        help_text="Endpoint type can be internalURL, adminURL on publicURL. If is a helper for the CloudDriver to "
                  "choose the right URL in the OpenStack service catalog."
    )

    openstack_sec_groups = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Security Groups",
        help_text="If security groups are available on your OpenStack you can specify a comma separated list to use for"
                  " the machine (e.g. secgrp001,secgrp002)."
    )
    openstack_floatingip_pool = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Floating IP Pool",
        help_text="The IP pool that will be used to get a public IP an assign it to the machine. If there is an IP "
                  "address already allocated but not assigned to any machine, this IP will be chosen and assigned "
                  "to the machine. If there is no IP address already allocated a new IP will be allocated and assigned "
                  "to the machine."
    )
    openstack_ssh_user = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Username",
        help_text="The username to use for SSH into the machine. If not provided root will be used."
    )
    openstack_ssh_port = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="SSH Port",
        help_text="Customize the SSH port if the SSH server on the machine does not listen on the default port."
    )
    openstack_insecure = models.BooleanField(
        default=False,
        verbose_name="Insecure",
        help_text="Explicitly allow openstack CloudDriver to perform 'insecure' SSL (https) requests. The server's "
                  "certificate will not be verified against any certificate authorities. This option should be used "
                  "with caution"
    )


class Rackspace(CloudDriver):
    """
    --rackspace-username: Rackspace account username
    --rackspace-api-key: Rackspace API key
    --rackspace-region: Rackspace region name
    --rackspace-endpoint-type: Rackspace endpoint type (adminURL, internalURL or the default publicURL)
    --rackspace-image-id: Rackspace image ID. Default: Ubuntu 14.10 (Utopic Unicorn) (PVHVM)
    --rackspace-flavor-id: Rackspace flavor ID. Default: General Purpose 1GB
    --rackspace-ssh-user: SSH user for the newly booted machine. Set to root by default
    --rackspace-ssh-port: SSH port for the newly booted machine. Set to 22 by default
    """


    class Properties:
        logo = "rackspace.png"
        name = "Rackspace"
        driver = "rackspace"

    rackspace_username = models.CharField(
        max_length=50,
        blank=False,
        verbose_name="Username",
        help_text="Rackspace account username"
    )
    rackspace_api_key = models.CharField(
        max_length=50,
        blank=False,
        verbose_name="API Key",
        help_text="Rackspace API key"
    )


class RackspaceSettings(models.Model):
    FLAVORS = [
        ('2', '512 MB Standard Instance'), ('3', '1 GB Standard Instance'), ('4', '2 GB Standard Instance'),
        ('5', '4 GB Standard Instance'), ('6', '8 GB Standard Instance'), ('7', '15 GB Standard Instance'),
        ('8', '30 GB Standard Instance'), ('general1-1', '1 GB General Purpose v1'),
        ('general1-2', '2 GB General Purpose v1'), ('general1-4', '4 GB General Purpose v1'),
        ('general1-8', '8 GB General Purpose v1'), ('compute1-4', '3.75 GB Compute v1'),
        ('compute1-8', '7.5 GB Compute v1'), ('compute1-15', '15 GB Compute v1'),
        ('compute1-30', '30 GB Compute v1'), ('compute1-60', '60 GB Compute v1'),
        ('io1-15', '15 GB I/O v1'), ('io1-30', '30 GB I/O v1'), ('io1-60', '60 GB I/O v1'),
        ('io1-90', '90 GB I/O v1'), ('io1-120', '120 GB I/O v1'), ('memory1-15', '15 GB Memory v1'),
        ('memory1-30', '30 GB Memory v1'), ('memory1-60', '60 GB Memory v1'), ('memory1-120', '120 GB Memory v1'),
        ('memory1-240', '240 GB Memory v1'), ('onmetal-compute1', 'OnMetal Compute v1'),
        ('onmetal-io1', 'OnMetal I/O v1'), ('onmetal-memory1', 'OnMetal Memory v1')
    ]

    IMAGES = [
        ("PVHVM", "Ubuntu 14.10 (Utopic Unicorn)"),
    ]

    ENDPOINTS = [
        "adminURL", "internalURL", "publicURL"
    ]

    rackspace_region = models.CharField(
        max_length=50,
        blank=False,
        verbose_name="Region",
        help_text="Rackspace region name"
    )
    rackspace_endpoint_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Endpoint",
        default="publicURL",
        choices=[(end, end) for end in ENDPOINTS],
        help_text="Rackspace endpoint type"
    )
    rackspace_image_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Image",
        default="PVHVM",
        choices=IMAGES,
        help_text="Rackspace image ID"
    )
    rackspace_flavor_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        default="general1-1",
        choices=FLAVORS,
        verbose_name="Flavor ID",
        help_text="Rackspace flavor ID"
    )
    rackspace_ssh_user = models.CharField(
        max_length=50,
        blank=True,
        default="root",
        verbose_name="SSH User",
        help_text=""
    )
    rackspace_ssh_port = models.IntegerField(
        default=22,
        null=True,
        blank=True,
        verbose_name="SSH Port",
        help_text="SSH port for the newly booted machine"
    )


class VirtualBox(LocalDriver):
    """
    --virtualbox-boot2docker-url: The URL of the boot2docker image. Defaults to the latest available version.
    --virtualbox-disk-size: Size of disk for the host in MB. Default: 20000
    --virtualbox-memory: Size of memory for the host in MB. Default: 1024
    --virtualbox-cpu-count: Number of CPUs to use to create the VM. Defaults to number of available CPUs.
    """

    class Properties:
        logo = "virtualbox.png"
        name = "VirtualBox"
        driver = "virtualbox"


class VirtualBoxSettings(models.Model):
    virtualbox_boot2docker_url = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Boot2Docker URL",
        help_text="The URL of the boot2docker image. Defaults to the latest available version if left blank"
    )
    virtualbox_disk_size = models.IntegerField(
        blank=True,
        null=True,
        default=20000,
        verbose_name="Disk Size",
        help_text="Size of disk for the host in MB"
    )
    virtualbox_memory = models.IntegerField(
        blank=True,
        null=True,
        default=1024,
        verbose_name="RAM",
        help_text="Size of memory for the host in MB"
    )
    virtualbox_cpu_count = models.IntegerField(
        blank=True,
        null=True,
        default=None,
        verbose_name="CPUs",
        help_text="Number of CPUs to use to create the VM. Defaults to number of available CPUs if left blank"
    )


class VMWareFusion(LocalDriver):
    """
    --vmwarefusion-boot2docker-url: URL for boot2docker image.
    --vmwarefusion-disk-size: Size of disk for host VM (in MB). Default: 20000
    --vmwarefusion-memory-size: Size of memory for host VM (in MB). Default: 1024
    """

    class Properties:
        logo = "fusion.png"
        name = "VMWare Fusion"
        driver = "vmwarefusion"


class VMWareFusionSettings(models.Model):
    vmwarefusion_boot2docker_url = models.CharField(
        max_length=400,
        blank=True,
        verbose_name="Boot2Docker URL",
        help_text="URL for boot2docker image."
    )

    vmwarefusion_disk_size = models.IntegerField(
        blank=True,
        null=True,
        default=20000,
        verbose_name="Disk Size",
        help_text="Size of disk for host VM (in MB)"
    )

    vmwarefusion_memory_size = models.IntegerField(
        blank=True,
        null=True,
        default=1024,
        verbose_name="RAM",
        help_text="Size of memory for host VM (in MB)"
    )


class VMWareCloudAir(CloudDriver):
    """
    --vmwarevcloudair-username: vCloud Air Username.
    --vmwarevcloudair-password: vCloud Air Password.
    --vmwarevcloudair-catalog: Catalog. Default: Public Catalog
    --vmwarevcloudair-catalogitem: Catalog Item. Default: Ubuntu Server 12.04 LTS (amd64 20140927)
    --vmwarevcloudair-computeid: Compute ID (if using Dedicated Cloud).
    --vmwarevcloudair-cpu-count: VM Cpu Count. Default: 1
    --vmwarevcloudair-docker-port: Docker port. Default: 2376
    --vmwarevcloudair-edgegateway: Organization Edge Gateway. Default: <vdcid>
    --vmwarevcloudair-memory-size: VM Memory Size in MB. Default: 2048
    --vmwarevcloudair-name: vApp Name. Default: <autogenerated>
    --vmwarevcloudair-orgvdcnetwork: Organization VDC Network to attach. Default: <vdcid>-default-routed
    --vmwarevcloudair-provision: Install Docker binaries. Default: true
    --vmwarevcloudair-publicip: Org Public IP to use.
    --vmwarevcloudair-ssh-port: SSH port. Default: 22
    --vmwarevcloudair-vdcid: Virtual Data Center ID.
    """

    class Properties:
        logo = "vcloud.png"
        name = "VMWare vCloud Air"
        driver = "vmwarevcloudair"

    vmwarevcloudair_username = models.CharField(
        max_length=50,
        blank=False,
        verbose_name="Username",
        help_text="vCloud Air Username"
    )
    vmwarevcloudair_password = models.CharField(
        max_length=50,
        blank=False,
        verbose_name="Password",
        help_text="vCloud Air Password"
    )


class VMWareCloudAirSettings(models.Model):
    CATALOGS = ["Public Catalog"]
    CATALOG_ITEMS = ["Ubuntu Server 12.04 LTS (amd64 20140927)"]

    vmwarevcloudair_vdcid = models.CharField(
        max_length=50,
        blank=False,
        verbose_name="Virtual Data Center ID",
        help_text="Virtual Data Center ID.",
        default="VDC1"
    )
    vmwarevcloudair_publicip = models.GenericIPAddressField(
        blank=False,
        verbose_name="Public IP",
        help_text="Org Public IP to use"
    )

    vmwarevcloudair_catalog = models.CharField(
        max_length=50,
        blank=False,
        verbose_name="Catalog",
        help_text="Catalog",
        choices=[(i, i) for i in CATALOGS],
        default=CATALOGS[0]
    )
    vmwarevcloudair_catalogitem = models.CharField(
        max_length=50,
        blank=False,
        verbose_name="Catalog Item",
        help_text="Catalog Item",
        choices=[(i, i) for i in CATALOG_ITEMS],
        default=CATALOG_ITEMS[0]
    )
    vmwarevcloudair_computeid = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Compute ID",
        help_text="Compute ID"
    )
    vmwarevcloudair_cpu_count = models.IntegerField(
        default=1,
        blank=False,
        verbose_name="CPUs",
        help_text="VM Cpu Count"
    )
    vmwarevcloudair_docker_port = models.IntegerField(
        default=2376,
        blank=False,
        verbose_name="Docker Port",
        help_text="Docker port"
    )
    vmwarevcloudair_edgegateway = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Gateway",
        help_text="Organization Edge Gateway"
    )
    vmwarevcloudair_memory_size = models.IntegerField(
        default=2048,
        blank=False,
        verbose_name="RAM",
        help_text="VM Memory Size in MB"
    )
    vmwarevcloudair_name = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="vApp Name",
        help_text="vApp Name. Default: <autogenerated>"
    )
    vmwarevcloudair_orgvdcnetwork = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="VDC Network",
        help_text="Organization VDC Network to attach."
    )
    vmwarevcloudair_provision = models.BooleanField(
        default=True,
        verbose_name="Install Docker Binaries",
        help_text="Install Docker binaries."
    )
    vmwarevcloudair_ssh_port = models.IntegerField(
        default=22,
        blank=False,
        verbose_name="SSH Port",
        help_text="SSH port."
    )


class VMWareVsphere(CloudDriver):
    """
    --vmwarevsphere-username: vSphere Username.
    --vmwarevsphere-password: vSphere Password.
    --vmwarevsphere-boot2docker-url: URL for boot2docker image.
    --vmwarevsphere-compute-ip: Compute host IP where the Docker VM will be instantiated.
    --vmwarevsphere-cpu-count: CPU number for Docker VM. Default: 2
    --vmwarevsphere-datacenter: Datacenter for Docker VM (must be set to ha-datacenter when connecting to a single host).
    --vmwarevsphere-datastore: Datastore for Docker VM.
    --vmwarevsphere-disk-size: Size of disk for Docker VM (in MB). Default: 20000
    --vmwarevsphere-memory-size: Size of memory for Docker VM (in MB). Default: 2048
    --vmwarevsphere-network: Network where the Docker VM will be attached.
    --vmwarevsphere-pool: Resource pool for Docker VM.
    --vmwarevsphere-vcenter: IP/hostname for vCenter (or ESXi if connecting directly to a single host).
    """

    class Properties:
        logo = "vsphere.png"
        name = "VMWare vSphere"
        driver = "vmwarevsphere"

    vmwarevsphere_username = models.CharField(
        max_length=50,
        blank=False,
        verbose_name="Username",
        help_text="vSphere Username"
    )
    vmwarevsphere_password = models.CharField(
        max_length=50,
        blank=False,
        verbose_name="Password",
        help_text="vSphere Password"
    )
    vmwarevsphere_vcenter = models.CharField(
        max_length=50,
        blank=False,
        verbose_name="IP/Hostname",
        help_text="IP/hostname for vCenter (or ESXi if connecting directly to a single host)"
    )


class VMWareVsphereSettings(models.Model):
    vmwarevsphere_boot2docker_url = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Boot2Docker URL",
        help_text="URL for boot2docker image."
    )
    vmwarevsphere_compute_ip = models.CharField(
        max_length=50,
        blank=False,
        verbose_name="Compute Host IP",
        help_text="Compute host IP where the Docker VM will be instantiated."
    )
    vmwarevsphere_cpu_count = models.IntegerField(
        blank=False,
        verbose_name="CPUs",
        help_text="CPU number for Docker VM",
        default=2
    )
    vmwarevsphere_datacenter = models.CharField(
        max_length=50,
        blank=False,
        verbose_name="Datacenter",
        help_text="Datacenter for Docker VM (must be set to ha-datacenter when connecting to a single host)."
    )
    vmwarevsphere_datastore = models.CharField(
        max_length=100,
        blank=False,
        verbose_name="Datastore",
        help_text="Datastore for Docker VM.",
        default="datastore1"
    )
    vmwarevsphere_disk_size = models.IntegerField(
        blank=False,
        verbose_name="Disk Size",
        default=20000,
        help_text="Size of disk for Docker VM (in MB)"
    )
    vmwarevsphere_memory_size = models.IntegerField(
        blank=False,
        verbose_name="RAM",
        default=2048,
        help_text="Size of memory for Docker VM (in MB)"
    )
    vmwarevsphere_network = models.CharField(
        max_length=50,
        blank=False,
        verbose_name="Network",
        help_text="Network where the Docker VM will be attached.",
        default="VM Network"
    )
    vmwarevsphere_pool = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Resource Pool",
        help_text="Resource pool for Docker VM."
    )


CLOUD_DRIVER = [
    AWS, DigitalOcean, Softlayer, Azure,
    Openstack, Rackspace, VMWareCloudAir,
    VMWareVsphere,
    # Google is broken
]

LOCAL_DRIVER = [
    VMWareFusion, VirtualBox, HyperV
]


def driver_class_by_name(name):
    for driver in LOCAL_DRIVER + CLOUD_DRIVER:
        if driver.Properties.driver == name:
            return driver

    return None