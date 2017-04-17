#!/usr/bin/python

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}
                    

from ansible.module_utils.fortios import fortios_argument_spec, fortios_required_if
from ansible.module_utils.fortios import backup
from ansible.module_utils.six import iteritems
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.pycompat24 import get_exception

import re
import math

#check for pyFG lib
try:
    from pyFG import FortiOS, FortiConfig
    from pyFG.fortios import logger
    from pyFG.exceptions import CommandExecutionException, FailedCommit, ForcedCommit
    HAS_PYFG=True
except:
    HAS_PYFG=False
    
def main():
    argument_spec = dict(
        src       = dict(type='str', default=None),
        filter    = dict(type='str', default=""),
    )

    argument_spec.update(fortios_argument_spec)

    required_if = fortios_required_if

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=required_if,
    )

    result = dict(changed=False)

    # fail if pyFG not present
    if not HAS_PYFG:
        module.fail_json(msg='Could not import the python library pyFG required by this module')
        
    #define device
    f = FortiOS( module.params['host'],
            username=module.params['username'],
            password=module.params['password'],
        )
        
    #connect
    try:
        f.open()
    except:
        module.fail_json(msg='Error connecting device')


    # get info
    facts = dict()

    facts['all_ipv4_addresses'] = list()

    interfaces = f.execute_command('get system interface')
    for interface in interfaces:
        if re.search('name:',interface):
            if re.search('0.0.0.0 0.0.0.0',interface) == None:
                ipv4_address = re.match('.*ip:\s([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})',interface).group(1)
                facts['all_ipv4_addresses'].append(ipv4_address)
    
    #facts['all_ipv6_addresses'] = list()
    #facts['apparmor'] = dict()
    #facts['architecture'] = ''
    #facts['bios_date'] =''
    #facts['bios_version'] = ''
    #facts['date_time'] = dict()

    # get interface of default route
    defaultInterface = re.match('.*,\s+(.*)$',f.execute_command('get router info routing-table all | grep 0.0.0.0')[0].lstrip()).group(1)

    # convert ppp1 to pppoe    
    if re.match('ppp',defaultInterface):
        defaultInterface = 'pppoe'
    
    # get interface's info which is used on default route 
    interfaces = f.execute_command('get system interface | grep ' + defaultInterface)

    for interface in interfaces:
        if re.search('status: up',interface) and re.search(defaultInterface,interface):
            default_ipv4_address = re.match('.*ip:\s([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})',interface).group(1)
    
    facts['default_ipv4'] = dict()
    facts['default_ipv4'].update({'address':default_ipv4_address})
    facts['default_ipv4'].update({'interface':defaultInterface})

    #facts['default_ipv6'] = dict()
    
    # Version: Fortigate-50B v4.0,build0665,130514 (MR3 Patch 14)
    distribution_major_version = re.match('Version:\s.*\s(.*),build',f.execute_command('get system status | grep Version')[0].lstrip()).group(1)
    distribution_version = re.match('Version:\s.*\((.*)\)',f.execute_command('get system status | grep Version')[0].lstrip()).group(1)
    facts['distribution'] = 'FortiOS'
    facts['distribution_major_version'] = distribution_major_version
    facts['distribution_version'] = distribution_major_version + ' ' + distribution_version
    
    #dns = f.execute_command('get system dns')[]

    #facts['dns'] = dict()
    #facts['domain'] = ''

    hostname = re.match('Hostname:\s(.*)',f.execute_command('get system status | grep Hostname')[0].lstrip()).group(1)
    facts['fqdn'] = hostname
    facts['hostname'] = hostname
    
    #facts['interfaces'] = list()
    #facts['ip_addresses'] = list()
    #facts['kernel'] = ''
    #facts['lastboot'] = ''
    #facts['machine'] = ''
    #facts['machine_id'] = ''
    #facts['memfree_mb'] = ''

    memfree_mb = re.match('Mem:\s*([0-9]*)\s*([0-9]*)\s*([0-9]*)',f.execute_command('diagnose hardware sysinfo memory | grep Mem:')[0].lstrip()).group(3)
    memfree_mb = math.floor(int(memfree_mb)/1024/1024)
    facts['memfree_mb'] = memfree_mb
    
    memtotal_mb = re.match('Mem:\s*([0-9]*)\s*([0-9]*)\s*([0-9]*)',f.execute_command('diagnose hardware sysinfo memory | grep Mem:')[0].lstrip()).group(1)
    memtotal_mb = math.floor(int(memtotal_mb)/1024/1024)
    facts['memtotal_mb'] = memtotal_mb
    
    #facts['mounts'] = list()
    #facts['nodename'] = ''
    facts['os_family'] = 'FortiOS'
    
    results = f.execute_command('get hardware cpu')
    i = 0
    for result in results:
      if re.match('[pP]rocessor\s*:\s*(.*)',result.lstrip()) != None:
        i = i + 1
    
    #facts['processor'] = list()
    #facts['processor_cores'] = 0
    #facts['processor_count'] = 0
    #facts['processor_threads_per_core'] = 0
    facts['processor_vcpus'] = i

    product_name = re.match('Version:\s(.*)\sv',f.execute_command('get system status | grep Version')[0].lstrip()).group(1)    
    facts['product_name'] = product_name

    product_serial = re.match('Serial-Number:\s(.*)',f.execute_command('get system status | grep Serial')[0].lstrip()).group(1)    
    facts['product_serial'] =  product_serial
    #facts['swapfree_mb'] = 0
    #facts['swaptotal_mb'] =  0
    #facts['system'] = "Win32NT"
    facts['system_vendor'] = "Fortinet"
    #facts['uptime_seconds'] = 767400
    facts['module_setup'] = True

    ansible_facts = dict()
    for key, value in iteritems(facts):
        key = 'ansible_%s' % key
        ansible_facts[key] = value
        
    module.exit_json(ansible_facts=ansible_facts)
    
if __name__ == '__main__':
    main()