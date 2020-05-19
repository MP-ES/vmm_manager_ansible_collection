# Ansible collection to vmm_manager

Ansible collection to support [vmm_manager](https://github.com/MP-ES/vmm_manager) application on Ansible codes.

[![License](https://img.shields.io/github/license/MP-ES/vmm_manager_ansible_collection.svg)](LICENSE)

## Development

### python-poetry configuration

```shell
# poetry installation
curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python
echo 'source $HOME/.poetry/env' >>~/.bashrc

# autocomplete configuration
# Bash
poetry completions bash | sudo tee /etc/bash_completion.d/poetry.bash-completion
```

### Dependencies

```shell
poetry install --no-root
```

### Configurations

Set the enviromment variable **ANSIBLE_INVENTORY_PLUGINS**:

```shell
export ANSIBLE_INVENTORY_PLUGINS='plugins/inventory'
```

### Tests

```shell
# Check documentation
ansible-doc -t inventory vmm_manager

# Test inventory list
ansible-inventory -i test_vmm_manager.yaml --list
```

## References

- [vmm_manager](https://github.com/MP-ES/vmm_manager)
- [Developing Ansible collections](https://docs.ansible.com/ansible/latest/dev_guide/developing_collections.html#developing-collections)
- [Developing Ansible plugins](https://docs.ansible.com/ansible/latest/dev_guide/developing_plugins.html#developing-plugins)
- [Developing Ansible dynamic inventory](https://docs.ansible.com/ansible/latest/dev_guide/developing_inventory.html#inventory-sources)
- [Poetry](https://python-poetry.org/)
