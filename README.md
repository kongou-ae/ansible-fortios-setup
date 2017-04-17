# ansible-fortios-setup

```
- hosts: forti
  gather_facts: no
  connection: local
  tasks:
    - name: "gather facts"
      fortios_setup:
        host: "{{ inventory_hostname }}"
        username: "{{ ansible_user }}"
        password: "{{ ansible_password }}"
      register: gather
      
    - name: "output"
      debug: var=gather
```

```
TASK [gather facts] *************************************************************************************************************************************
ok: [xxx.xxx.xxx.xxx]

TASK [output] *******************************************************************************************************************************************
ok: [xxx.xxx.xxx.xxx] => {
    "changed": false,
    "gather": {
        "ansible_facts": {
            "ansible_distribution": "FortiOS",
            "ansible_distribution_major_version": "v4.0",
            "ansible_distribution_version": "v4.0 MR3 Patch 14",
            "ansible_fqdn": "FGT50B3Gxxxxxxxx",
            "ansible_hostname": "FGT50B3Gxxxxxxxx",
            "ansible_memfree_mb": 115,
            "ansible_memtotal_mb": 249,
            "ansible_module_setup": true,
            "ansible_os_family": "FortiOS",
            "ansible_processor_vcpus": 1,
            "ansible_product_name": "Fortigate-50B",
            "ansible_product_serial": "FGT50B3Gxxxxxxxx",
            "ansible_system_vendor": "Fortinet"
        },
        "changed": false
    }
}
```


I tested with this FortiGate.

- FortiGate 50B v4.3.14
- FortiGate 60D v5.2.5