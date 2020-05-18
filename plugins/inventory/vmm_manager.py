from __future__ import (absolute_import, division, print_function)
from ansible.errors import AnsibleError, AnsibleParserError
from ansible.plugins.inventory import BaseInventoryPlugin
import re
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
        count:
            description: The number of hosts and groups to make.
            type: integer
            required: True
        password:
            description: Password to put in hostvars b64 encoded.
            type: string
            secret: true
            default: foo
            env:
                - name: BASIC_PASSWORD
    requirements:
        - python >= 3.7
        - vmm_manager >= 0.1.0b3
'''

EXAMPLES = r'''
# create 4 sub-groups and hosts
plugin: vmm_manager
count: 4
'''


class InventoryModule(BaseInventoryPlugin):
    NAME = 'vmm_manager'

    def verify_file(self, path):
        '''Return true/false if this is possibly a valid file for this plugin to consume
        '''
        if super(InventoryModule, self).verify_file(path):
            if re.match(r'.{0,}vmm_manager\.y(a)?ml$', path):
                return True

    def parse(self, inventory, loader, path, cache):
        '''Return dynamic inventory from source '''
        return 'Teste'
