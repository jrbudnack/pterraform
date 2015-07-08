# Pterraform
A Python wrapper for Terraform.
## Purpose
This package allows you to programmatically invoke Terraform from Python.  At this point, we only do Apply and Destroy.  This library also parses the local terraform.tfstate file, so the state of your infrastructure can be used in your application (such as uuid's for objects and other properties).  Finally, pterraform parses the output to generate data on how long it takes for any given piece of the infrastructure to stand up.

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

# Apply the terraform manifest and print the start times and durations.
print tfproject.apply()

# Print the current state after apply() is called.
print tfproject.state()

tfproject.destroy()
```


