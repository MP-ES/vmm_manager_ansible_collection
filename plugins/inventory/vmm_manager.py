"""
vmm_manager inventory plugin
"""

from __future__ import (absolute_import, division, print_function)
import re
import subprocess
import json
from subprocess import PIPE, STDOUT, SubprocessError
from shutil import which
from ansible.errors import AnsibleError
from ansible.plugins.inventory import BaseInventoryPlugin

# pylint: disable=invalid-name
__metaclass__ = type

DOCUMENTATION = r'''
    name: vmm_manager
    plugin_type: inventory
    author:
      - Estevão Costa (@estevao90)
    short_description: vmm_manager inventory source.
    description:
        - Fetch virtual machines from SCVMM through vmm_manager app.
    options:
        plugin:
            description: Marks this as an instance of the 'vmm_manager' plugin
            required: True
            choices: ['vmm_manager']
        vmm_servidor_acesso:
            description: Windows server with OpenSSH and access to SCVMM PowerShell
            type: string
            required: True
            env:
                - name: VMM_SERVIDOR_ACESSO
        vmm_servidor:
            description: SCVMM Server
            type: string
            required: True
            env:
                - name: VMM_SERVIDOR
        vmm_inventario:
            description: Inventory file (YAML format)
            type: string
            required: True
            env:
                - name: VMM_INVENTARIO
        vmm_usuario:
            description: User with access to Windows access server and SCVMM
            type: string
            required: True
            env:
                - name: VMM_USUARIO
        vmm_senha:
            description: User password
            type: string
            required: True
            secret: True
            env:
                - name: VMM_SENHA
    requirements:
        - python >= 3.7
        - vmm_manager >= 0.1.0b2
'''

EXAMPLES = r'''
# create the inventory described in test_inventory.yaml
# You can pass the parameters through enviromment variables: see docs
plugin: vmm_manager
vmm_inventario: inventory.yaml
vmm_servidor_acesso: 'access_server'
vmm_servidor: 'scvmm_server'
vmm_usuario: 'username'
vmm_senha: 'password'
'''


class InventoryModule(BaseInventoryPlugin):
    """
    Ansible Inventory plugin class
    """
    NAME = 'vmm_manager'
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
        self.command_result = None

    def verify_file(self, path):
        """
        Return true/false if this is possibly a valid file for this plugin to consume
        """
        if super(InventoryModule, self).verify_file(path):
            if re.match(r'.{0,}vmm_manager\.y(a)?ml$', path):
                return True
        return False

    def parse(self, inventory, loader, path, cache=True):
        """
        Return dynamic inventory from source
        """
        super(InventoryModule, self).parse(inventory, loader, path)

        self._read_config_data(path)
        self.__setup()

        self.__run_command()

    def __run_command(self):
        """
        Run vmm_manager command
        """
        try:
            command_exec = subprocess.run(
                self.command, stdout=PIPE,
                stderr=STDOUT, check=True)
            self.command_result = json.loads(command_exec.stdout.decode())
            print(self.command_result)
        except SubprocessError as error:
            # pylint: disable=no-member
            raise AnsibleError('vmm_manager error: {}\n{}'.format(
                error, error.output.decode()))

    def __setup(self):
        """
        Plugin setup
        """
        if not InventoryModule.has_vmm_manager():
            raise AnsibleError(
                'This module requires the vmm_manager app. Try `pip install vmm-manager`.'
            )
        self.command.append(InventoryModule.VMM_MANAGER_APP)

        self.command.append('--servidor-acesso')
        self.command.append(self.get_option('vmm_servidor_acesso'))
        self.command.append('--servidor')
        self.command.append(self.get_option('vmm_servidor'))

        self.command.append('--usuario')
        self.command.append(self.get_option('vmm_usuario'))
        self.command.append('--senha')
        self.command.append(self.get_option('vmm_senha'))

        self.command.append('-o')
        self.command.append('show')

        self.command.append('--inventario')
        self.command.append(self.get_option('vmm_inventario'))
