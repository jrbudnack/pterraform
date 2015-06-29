# Pterraform
A Python wrapper for Terraform.
## Purpose
I have a need to stand up many Openstack client infrastructures for testing, using some kind of definition to minimize the need to alter code.  Since my current testing framework is written in Python, I figured I would write a simple Python wrapper.  Right now this is a POC, but depending on how successful it is, we'll see how far this goes!
## Usage
Right now, I can take a terraform JSON definition file and use it to deploy a tenant with the infrastructure I want.  I also write an override.tf.json file, given a dict you provide, which will override any variables you put in the definition.

You can point terraform to a single Terraform file, OR you can point it to the traditional Terraform folder, which contains the *.tf and *.tf.json files you wish to use.

Here is an example of how to use it:
```
import pterraform

variables = {
  "auth_url": "http://127.0.0.1:5000/v2.0",
  "user_name": "admin",
  "password": "password",
  "tenant_name": "tf_test",
  "instance_count": 10,
  "extnet_uuid": "703dd102-eee1-47da-b90a-345e98e6da5b",
  "extnet_name": "extnet1"
}
tfproject = Terraform("test.tf.json", variables);
tfproject.apply()
tfproject.destroy()
```
