# Lab 1 - Using Ansible to gather data from network devices

In the first lab you will learn to use Ansible to gather lots of
useful information about a test network. You will create a
**playbook** containing a list of tasks.

> A playbook can have multiple plays and a play can have one or more tasks. Tasks are the smallest unit within playbooks. Each task executes using a _module_. Modules typically take parameters as user inputs.


### Section 1: Exploring the lab environment

#### Step 1

Nagigate to the `networking-workshop` directory.


``` 
[student1@ip-172-16-101-121 ~]$ cd networking-workshop/
[student1@ip-172-16-101-121 networking-workshop]$ 
[student1@ip-172-16-101-121 networking-workshop]$ 

```

#### Step 2

Run the `ansible` command with the `--version` command to look at what is configured:


``` 
[student1@ip-172-16-101-121 networking-workshop]$ ansible --version
ansible 2.5.0
  config file = /home/student1/.ansible.cfg
  configured module search path = [u'/home/student1/.ansible/plugins/modules', u'/usr/share/ansible/plugins/modules']
  ansible python module location = /usr/lib/python2.7/site-packages/ansible
  executable location = /usr/bin/ansible
  python version = 2.7.5 (default, May  3 2017, 07:55:04) [GCC 4.8.5 20150623 (Red Hat 4.8.5-14)]
[student1@ip-172-16-101-121 networking-workshop]$ 


```

> Note: The ansible version you see might differ from the above output


This command gives you information about the version of Ansible, location of the executable, version of Python, search path for the modules and location of the `ansible configuration file`.

#### Step 3

Use the `cat` command to view the contents of the `ansible.cfg` file. 


```
[student1@ip-172-16-101-121 networking-workshop]$ cat /home/student1/.ansible.cfg 
[defaults]
connection = smart
timeout = 60
inventory = /home/student1/networking-workshop/lab_inventory/hosts
host_key_checking = False
private_key_file = /home/student1/.ssh/aws-private.pem
[student1@ip-172-16-101-121 networking-workshop]$ 

```

Note the following parameters within the `ansible.cfg` file:

 - `inventory`: shows the location of the ansible inventory being used
 - `private_key_file`: this shows the location of the private key used to login to devices



#### Step 4

The scope of a `play` within a `playbook` is limited to the groups of hosts declared within an Ansible **inventory**. Ansible supports multiple [inventory](http://docs.ansible.com/ansible/latest/intro_inventory.html) types. An inventory could be a simple flat file with a collection of hosts defined within it or it could be a dynamic script (potentially quering a CMDB backend) that generates a list of devices to run the playbook against.

In this lab you will work with a file based inventory written in the **ini** format. Use the `cat` command to view the contents of your inventory:


``` 

[student1@ip-172-16-101-121 networking-workshop]$ cat /home/student1/networking-workshop/lab_inventory/hosts
[all:vars]
ansible_user=student1
ansible_ssh_pass=ansible
ansible_port=22

[routers:children]
cisco

[cisco]
rtr1 ansible_host=52.90.196.252 ansible_ssh_user=ec2-user private_ip=172.16.165.205 ansible_network_os=ios
rtr2 ansible_host=52.91.137.149 ansible_ssh_user=ec2-user private_ip=172.17.249.137 ansible_network_os=ios
rtr3 ansible_host=18.207.193.156 ansible_ssh_user=ec2-user private_ip=172.16.235.46 ansible_network_os=ios
rtr4 ansible_host=34.229.105.87 ansible_ssh_user=ec2-user private_ip=172.17.231.181 ansible_network_os=ios


[cisco:vars]
ansible_ssh_user=ec2-user
ansible_network_os=ios


[dc1]
rtr1
rtr3

[dc2]
rtr2
rtr4

[hosts]
host1 ansible_host=35.153.176.127 ansible_ssh_user=ec2-user private_ip=172.17.65.234

[control]
ansible ansible_host=34.239.141.34 ansible_ssh_user=ec2-user private_ip=172.16.101.121
[student1@ip-172-16-101-121 networking-workshop]$ 

```

#### Step 5

In the above output every `[ ]` defines a group. For example `[dc1]` is a group that contains the hosts `rtr1` and `rtr2`. Groups can also be _nested_. The group `[routers]` is a parent group to the group `[cisco]`

> Parent groups are declared using the `children` directive. Having nested groups allows the flexibility of assigining more specific values to variables.


> Note: A group called **all** always exists and contains all groups and hosts defined within an inventroy.


We can associate variables to groups and hosts. Host variables are declared/defined on the same line as the host themselves. For example for the host `rtr1`:

```
rtr1 ansible_host=52.90.196.252 ansible_ssh_user=ec2-user private_ip=172.16.165.205 ansible_network_os=ios

```

 - `rtr1` - The name that Ansible will use.  This can but does not have to rely on DNS
 - `ansible_host` - The IP address that ansible will use, if not configured it will default to DNS
 - `ansible_ssh_user` - The user ansible will use to login to this host, if not configured it will default to the user the playbook is run from
 - `private_ip` - This value is not reserved by ansible so it will default to a [host variable](http://docs.ansible.com/ansible/latest/intro_inventory.html#host-variables).  This variable can be used by playbooks or ignored completely.
- `ansible_network_os` - This variable is necessary while using the `network_cli` connection type within a play definition, as we will see shortly.




### Section 2: Writing your first playbook

Now that you have a fundamental grasp of the inventory file and the group/host variables, this section will walk you through building a playbook. 

> This section will help you understand the components of a playbook while giving you an immediate baseline for using within your own production environments!

#### Step 1:

Using your favorite text editor (`vim` and `nano` are available on the control host) create a new file called `gather_ios_data.yml`.

>Alternately, you can create it using sublimetext or any GUI editor on your laptop and scp it over)


>Ansible playbooks are **YAML** files. YAML is a structured encoding format that is also extremely human readable (unlike it's subset - the JSON format)

#### Step 2:

Enter the following play definition into `gather_ios_data.yml`:


``` yaml
---
- name: GATHER INFORMATION FROM ROUTERS
  hosts: cisco
  connection: network_cli
  gather_facts: no
```

`---` indicates that this is a YAML file. We are running this playbook against the group `cisco`, that was defined earlier in the inventory file. Playbooks related to network devices should use the connection plugin called `network_cli`. Ansible has different connection plugins that handle different connection interfaces. The `network_cli` plugin is written specifically for network equipment and handles things like ensuring a persistent SSH connection across multiple tasks.


#### Step 3

Next, add the first `task`. This task will use the `ios_facts` module to gather facts about each device in the group `cisco`.


``` yaml
---
- name: GATHER INFORMATION FROM ROUTERS
  hosts: cisco
  connection: network_cli
  gather_facts: no

  tasks:
    - name: GATHER ROUTER FACTS
      ios_facts:
```

>A play is a list of tasks. Modules are pre-written code that perform the task.



#### Step 4

Run the playbook - exit back into the command line of the control host and execute the following:


```
[student1@ip-172-16-101-121 networking-workshop]$ ansible-playbook -i lab_inventory/hosts gather_ios_data.yml 



```

The output should look as follows.

```
[student1@ip-172-16-101-121 networking-workshop]$ ansible-playbook -i lab_inventory/hosts gather_ios_data.yml 

PLAY [GATHER INFORMATION FROM ROUTERS] ******************************************************************

TASK [GATHER ROUTER FACTS] ******************************************************************************
ok: [rtr1]
ok: [rtr4]
ok: [rtr3]
ok: [rtr2]

PLAY RECAP **********************************************************************************************
rtr1                       : ok=1    changed=0    unreachable=0    failed=0   
rtr2                       : ok=1    changed=0    unreachable=0    failed=0   
rtr3                       : ok=1    changed=0    unreachable=0    failed=0   
rtr4                       : ok=1    changed=0    unreachable=0    failed=0   

[student1@ip-172-16-101-121 networking-workshop]$ 


```


#### Step 5


The play ran successfully and executed against the 4 routers. But where is the output?! Re-run the playbook using the `-v` flag.

> Note: Ansible has increasing level of verbosity. You can use up to 4 "v's", -vvvv.


``` 
student1@ip-172-16-101-121 networking-workshop]$ ansible-playbook -i lab_inventory/hosts gather_ios_data.yml  -v
Using /home/student1/.ansible.cfg as config file

PLAY [GATHER INFORMATION FROM ROUTERS] ******************************************************************

TASK [GATHER ROUTER FACTS] ******************************************************************************
ok: [rtr3] => {"ansible_facts": {"ansible_net_all_ipv4_addresses": ["10.100.100.3", "192.168.3.103", "172.16.235.46", "192.168.35.101", "10.3.3.103"], "ansible_net_all_ipv6_addresses": [], "ansible_net_filesystems": ["bootflash:"], "ansible_net_gather_subset": ["hardware", "default", "interfaces"], "ansible_net_hostname": "rtr3", "ansible_net_image": "boot:packages.conf", "ansible_net_interfaces": {"GigabitEthernet1": {"bandwidth": 1000000, "description": null, "duplex": "Full", "ipv4": [{"address": "172.16.235.46", "subnet": "16"}], "lineprotocol": "up ", "macaddress": "0e93.7710.e63c", "mediatype": "Virtual", "mtu": 1500, "operstatus": "up", "type": "CSR vNIC"}, "Loopback0": {"bandwidth": 8000000, "description": null, "duplex": null, "ipv4": [{"address": "192.168.3.103", "subnet": "24"}], "lineprotocol": "up ", "macaddress": "192.168.3.103/24", "mediatype": null, "mtu": 1514, "operstatus": "up", "type": null}, "Loopback1": {"bandwidth": 8000000, "description": null, "duplex": null, "ipv4": [{"address": "10.3.3.103", "subnet": "24"}], "lineprotocol": "up ", "macaddress": "10.3.3.103/24", "mediatype": null, "mtu": 1514, "operstatus": "up", "type": null}, "Tunnel0": {"bandwidth": 100, "description": null, "duplex": null, "ipv4": [{"address": "10.100.100.3", "subnet": "24"}]

.
.
.
.
.
<output truncated for readability>
```


> Note: The output returns key-value pairs that can then be used within the playbook for subsequent tasks. Also note that all variables that start with **ansible_** are automatically available for subsequent tasks within the play.


#### Step 6

Ansible allows you to limit the playbook execution to a subset of the devices declared in the group, against which the play is running against. This can be done using the `--limit` flag. Rerun the above task, limiting it first to `rtr1` and then to both `rtr1` and `rtr3`


``` 
[student1@ip-172-16-101-121 networking-workshop]$ ansible-playbook -i lab_inventory/hosts gather_ios_data.yml  -v --limit rtr1
```


``` 
[student1@ip-172-16-101-121 networking-workshop]$ ansible-playbook -i lab_inventory/hosts gather_ios_data.yml  -v --limit rtr1,rtr3

```





#### Step 7

Running a playbook in verbose mode is a good option to validate the output from a task. To work with the variables within a playbook you can use the `debug` module. 

Write 2 tasks that display the routers' OS version and serial number.


``` yaml
---
- name: GATHER INFORMATION FROM ROUTERS
  hosts: cisco
  connection: network_cli
  gather_facts: no

  tasks:
    - name: GATHER ROUTER FACTS
      ios_facts:

    - name: DISPLAY VERSION
      debug:
        msg: "The IOS version is: {{ ansible_net_version }}"

    - name: DISPLAY SERIAL NUMBER
      debug:
        msg: "The serial number is:{{ ansible_net_serialnum }}"
```

#### Step 8

Now re-run the playbook but this time do not use the `verbose` flag and run it against all hosts.

```

[student1@ip-172-16-101-121 networking-workshop]$ ansible-playbook -i lab_inventory/hosts gather_ios_data.yml 

PLAY [GATHER INFORMATION FROM ROUTERS] ******************************************************************

TASK [GATHER ROUTER FACTS] ******************************************************************************
ok: [rtr4]
ok: [rtr1]
ok: [rtr2]
ok: [rtr3]

TASK [DISPLAY VERSION] **********************************************************************************
ok: [rtr4] => {
    "msg": "The IOS version is: 16.08.01a"
}
ok: [rtr1] => {
    "msg": "The IOS version is: 16.08.01a"
}
ok: [rtr2] => {
    "msg": "The IOS version is: 16.08.01a"
}
ok: [rtr3] => {
    "msg": "The IOS version is: 16.08.01a"
}

TASK [DISPLAY SERIAL NUMBER] ****************************************************************************
ok: [rtr1] => {
    "msg": "The serial number is:96F0LYYKYUZ"
}
ok: [rtr4] => {
    "msg": "The serial number is:94KZZ28ZT1Y"
}
ok: [rtr2] => {
    "msg": "The serial number is:9VBX7BSSLGS"
}
ok: [rtr3] => {
    "msg": "The serial number is:9OLKU6JWXRP"
}

PLAY RECAP **********************************************************************************************
rtr1                       : ok=3    changed=0    unreachable=0    failed=0   
rtr2                       : ok=3    changed=0    unreachable=0    failed=0   
rtr3                       : ok=3    changed=0    unreachable=0    failed=0   
rtr4                       : ok=3    changed=0    unreachable=0    failed=0   

[student1@ip-172-16-101-121 networking-workshop]$ 

```


Using less than 20 lines of "code" you have just automated version and serial number collection. Imagine if you were running this against your production network! You have actionable data in hand that does not go out of date.





### Section 3 - Module documentation, Registering output & tags


In the previous section you learned to use the `ios_facts` and the debug modules. The `debug` module had an input parameter called `msg` whereas the `ios_facts` module had no input parameters. As someone just starting out how would you know what these parameters were for a module?

There are 2 options. 

- 1. Point your browser to https://docs.ansible.com > Network Modules and read the documentation

- 2. From the command line, issue the `ansible-doc <module-name>` to read the documentation on the control host.

#### Step 1
On the control host read the documentation about the `ios_facts` module and the `debug` module.


``` 
[student1@ip-172-16-101-121 networking-workshop]$ ansible-doc debug

```

What happens when you use `debug` without specifying any parameter?

``` 
[student1@ip-172-16-101-121 networking-workshop]$ ansible-doc ios_facts

```

How can you limit the facts collected ?



#### Step 2
In the previous section, you learned how to use the `ios_facts` module to collect device details. What if you wanted to collect the output of a `show` command that was not provided as a part of `ios_facts` ?
