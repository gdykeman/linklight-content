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
