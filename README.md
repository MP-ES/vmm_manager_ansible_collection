# Ansible collection to vmm_manager

Ansible collection to support [vmm_manager](https://github.com/MP-ES/vmm_manager) application on Ansible codes.

[![License](https://img.shields.io/github/license/MP-ES/vmm_manager_ansible_collection.svg)](LICENSE)
[![Integration](https://github.com/MP-ES/vmm_manager_ansible_collection/workflows/Integration/badge.svg)](https://github.com/MP-ES/vmm_manager_ansible_collection/actions?query=workflow%3AIntegration)
[![Release](https://github.com/MP-ES/vmm_manager_ansible_collection/workflows/Release/badge.svg)](https://github.com/MP-ES/vmm_manager_ansible_collection/actions?query=workflow%3ARelease)

## Installation and usage

### Installing the collection from Ansible Galaxy

Before using the vmm_manager collection, you need to install it with the Ansible Galaxy CLI:

```sh
ansible-galaxy collection install mpes.vmm_manager
```

You can also include it in a `requirements.yml` file and install it via `ansible-galaxy collection install -r requirements.yml`, using the format:

```yaml
---
collections:
  - name: mpes.vmm_manager
```

### Installing the vmm_manager

This collection requires the [vmm_manager](https://github.com/MP-ES/vmm_manager) application. You can install it with:

```sh
pip install vmm-manager
```

### Using the dynamic inventory from this collection in your playbooks

Create an inventory file, named **\*vmm_manager.yaml**, for example, [test_vmm_manager.yaml](test_vmm_manager.yaml) with this content:

```yaml
plugin: vmm_manager
vmm_inventario: test_inventory.yaml # vmm_manager inventory file
cache: True # optional
cache_plugin: jsonfile # optional

# Best pratices: use enviromment variables to set this parameters
# vmm_servidor_acesso: 'access_server'
# vmm_servidor: 'scvmm_server'
# vmm_usuario: 'username'
# vmm_senha: 'password'
# vmm_ssh_priv_key_file: '/private/key' # optional
# vmm_ssh_user: user # optional
```

Use the command `ansible-doc -t inventory vmm_manager` for more details.

### Cache configuration (Optional)

If cache is enabled (recommend, due the response time of SCVMM queries), you have to set the cache plugin that Ansible will use (cache_plugin).

In case of **jsonfile** plugin, you have to set the cache location path, throught enviromment variable **ANSIBLE_CACHE_PLUGIN_CONNECTION**, for example:

```shell
export ANSIBLE_CACHE_PLUGIN_CONNECTION=.cache
```

For more details about Ansible cache, see [Ansible cache plugins](https://docs.ansible.com/ansible/latest/plugins/cache.html).

## Development

### python-poetry configuration

```shell
# poetry installation
curl -sSL https://install.python-poetry.org | python3 -

# autocomplete configuration
# bash
poetry completions bash >> ~/.bash_completion
```

### Dependencies

```shell
poetry install --no-root
```

### Configurations

Set the enviromments variables:

```shell
export ANSIBLE_INVENTORY_PLUGINS=plugins/inventory
# if jsonfile cache is enabled
export ANSIBLE_CACHE_PLUGIN_CONNECTION=.cache
```

### Helpful developer commands

```shell
# developer shell
poetry shell

# Load envs
export $(cat .env | xargs)

# List inventories
ansible-doc -t inventory -l

# Check documentation
ansible-doc -t inventory vmm_manager

# Test inventory list
ansible-inventory -i test_vmm_manager.yaml --list

# Lint
pylint --load-plugins pylint_quotes plugins/inventory/vmm_manager.py
```

## References

- [vmm_manager](https://github.com/MP-ES/vmm_manager)
- [Developing Ansible collections](https://docs.ansible.com/ansible/latest/dev_guide/developing_collections.html#developing-collections)
- [Developing Ansible plugins](https://docs.ansible.com/ansible/latest/dev_guide/developing_plugins.html#developing-plugins)
- [Developing Ansible dynamic inventory](https://docs.ansible.com/ansible/latest/dev_guide/developing_inventory.html#inventory-sources)
- [Poetry](https://python-poetry.org/)
