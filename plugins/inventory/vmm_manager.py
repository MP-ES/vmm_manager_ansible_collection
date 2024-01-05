"""
vmm_manager inventory plugin
"""

from __future__ import absolute_import, division, print_function

import json
import os
import re
import subprocess
from shutil import which

from ansible.errors import AnsibleError
from ansible.plugins.inventory import (BaseInventoryPlugin, Cacheable,
                                       Constructable)

# pylint: disable=invalid-name
__metaclass__ = type

DOCUMENTATION = r'''
    name: vmm_manager
    plugin_type: inventory
    author:
        - Estevão Costa (@estevao90)
    short_description: vmm_manager inventory source.
    description:
        - Fetch virtual machines from SCVMM through the vmm_manager app.
    options:
        plugin:
            description: Marks this as an instance of the 'vmm_manager' plugin.
            required: True
            choices: ['mpes.vmm_manager.vmm_manager', 'vmm_manager']
        vmm_access_point:
            description: Windows server with OpenSSH and access to SCVMM PowerShell.
            type: string
            required: True
            env:
                - name: VMM_ACCESS_POINT
        vmm_server:
            description: SCVMM Server.
            type: string
            required: True
            env:
                - name: VMM_SERVER
        vmm_inventory:
            description: Inventory file (YAML format).
            type: string
            required: True
            env:
                - name: VMM_INVENTORY
        vmm_username:
            description: User with access to Windows access server and SCVMM.
            type: string
            required: True
            env:
                - name: VMM_USERNAME
        vmm_password:
            description: User password.
            type: string
            required: True
            secret: True
            env:
                - name: VMM_PASSWORD
        vmm_ssh_priv_key_file:
            description: Private SSH key to access the VMs.
                        If the access is valid, the plugin set the ansible var ansible_ssh_private_key_file.
            type: string
            required: False
            env:
                - name: VMM_SSH_PRIV_KEY_FILE
        vmm_ssh_user:
            description: SSH user to access the VMs.
            type: string
            required: False
            env:
                - name: VMM_SSH_USER
    requirements:
        - python >= 3.9
        - vmm_manager ^1
    extends_documentation_fragment:
        - inventory_cache
'''

EXAMPLES = r'''
# create the inventory described in test_inventory.yaml
# You can pass the parameters through environment variables: see docs
plugin: vmm_manager
vmm_inventory: inventory.yaml
vmm_access_point: 'access_server'
vmm_server: 'scvmm_server'
vmm_username: 'username'
vmm_password: 'password'
vmm_ssh_priv_key_file: '/private/key' # optional
vmm_ssh_user: user # optional
'''


class InventoryModule(BaseInventoryPlugin, Constructable, Cacheable):
    """
    Ansible Inventory plugin class
    """
    NAME = 'mpes.vmm_manager.vmm_manager'
    VMM_MANAGER_APP = 'vmm_manager'

    @staticmethod
    def has_vmm_manager():
        """
        Check if vmm_manager is installed
        """
        return which(InventoryModule.VMM_MANAGER_APP) is not None

    def __init__(self):
        super().__init__()
        self.command = []
        self.envs = os.environ.copy()
        self.command_result = None

    def verify_file(self, path):
        """
        Return true/false if this is possibly a valid file for this plugin to consume
        """
        if super().verify_file(path):
            if re.match(r'.{0,}vmm_manager\.y(a)?ml$', path):
                return True
        return False

    def parse(self, inventory, loader, path, cache=True):
        """
        Return dynamic inventory from source
        """
        super().parse(inventory, loader, path)

        self._read_config_data(path)
        self.__setup()

        # cache
        cache_key = self.get_cache_key(path)
        user_cache_setting = self.get_option('cache')

        attempt_to_read_cache = user_cache_setting and cache
        cache_needs_update = user_cache_setting and not cache

        if attempt_to_read_cache:
            try:
                self.command_result = self._cache[cache_key]
            except KeyError:
                cache_needs_update = True
        else:
            self.__run_command()

        if cache_needs_update:
            self.__run_command()
            # set the cache
            self._cache[cache_key] = self.command_result

        self.__populate()

    def __run_command(self):
        """
        Run vmm_manager command
        """
        try:
            command_exec = subprocess.run(
                self.command, stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, check=True, env=self.envs)
            self.command_result = json.loads(command_exec.stdout.decode())
        except subprocess.SubprocessError as error:
            # pylint: disable=no-member
            raise AnsibleError(
                f'vmm_manager error: {error}\n{error.output.decode()}') from error

    def __setup(self):
        """
        Plugin setup
        """
        if not InventoryModule.has_vmm_manager():
            raise AnsibleError(
                'This module requires the vmm_manager app. Try `pip install vmm-manager`.'
            )
        self.command.append(InventoryModule.VMM_MANAGER_APP)

        self.command.append('--access-point')
        self.command.append(self.get_option('vmm_access_point'))
        self.command.append('--server')
        self.command.append(self.get_option('vmm_server'))

        self.command.append('--hide-progress')
        self.command.append('show')

        self.command.append('--inventory')
        self.command.append(os.path.abspath(self.get_option('vmm_inventory')))

        # user and password as env
        self.envs['VMM_USERNAME'] = self.get_option('vmm_username')
        self.envs['VMM_PASSWORD'] = self.get_option('vmm_password')

    def __is_ssh_priv_key_ok(self, host_ip):
        vmm_ssh_priv_key_file = self.get_option('vmm_ssh_priv_key_file')
        vmm_ssh_user = self.get_option('vmm_ssh_user')

        if not vmm_ssh_priv_key_file or not vmm_ssh_user:
            return False

        try:
            command_exec = subprocess.run(
                f'ssh -i {vmm_ssh_priv_key_file} \
                -o "BatchMode yes" -o "StrictHostKeyChecking no" \
                -o "IdentitiesOnly yes" -o "PreferredAuthentications publickey" \
                -o "ControlMaster no" {vmm_ssh_user}@{host_ip} exit 0',
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=True, check=True, env=self.envs)
            return command_exec.returncode == 0
        except subprocess.SubprocessError:
            return False

    def __populate(self):
        all_groups = []

        if not self.command_result:
            return

        for vm_obj in self.command_result.get('vms'):
            groups_vm = []
            all_vars = []

            # iterate over ansible data
            for ansible_entry in vm_obj.get('ansible'):
                group = ansible_entry.get('group')
                groups_vm.append(group)

                # append extra vars
                for var in ansible_entry.get('vars'):
                    all_vars.append(var)

                if group not in all_groups:
                    self.inventory.add_group(group)
                    all_groups.append(group)

            # add host just if it is in a group
            if groups_vm:
                host = vm_obj.get('name')
                self.inventory.add_host(host)

                for group_vm in groups_vm:
                    self.inventory.add_child(group_vm, host)

                # add hostvars
                host_ip = [network.get('ips')[0]
                           for network in vm_obj.get('networks')
                           if network.get('default')].pop()

                self.inventory.set_variable(
                    host, 'ansible_host', host_ip)
                if self.__is_ssh_priv_key_ok(host_ip):
                    self.inventory.set_variable(
                        host, 'ansible_ssh_private_key_file',
                        self.get_option('vmm_ssh_priv_key_file'))

                self.inventory.set_variable(
                    host, 'vm_id', vm_obj.get('vmm_id'))
                self.inventory.set_variable(
                    host, 'vm_description', vm_obj.get('description'))
                self.inventory.set_variable(
                    host, 'vm_image', vm_obj.get('image'))

                self.inventory.set_variable(
                    host, 'vm_region', vm_obj.get('region'))
                self.inventory.set_variable(
                    host, 'vm_region_host', vm_obj.get('region_host'))

                self.inventory.set_variable(
                    host, 'vm_status', vm_obj.get('status'))
                self.inventory.set_variable(
                    host, 'vm_cpu', vm_obj.get('cpu'))
                self.inventory.set_variable(
                    host, 'vm_memory', vm_obj.get('memory'))

                self.inventory.set_variable(
                    host, 'network_json', vm_obj.get('networks'))

                # add extra vars
                for var in all_vars:
                    self.inventory.set_variable(
                        host, var.get('name'), var.get('value'))
