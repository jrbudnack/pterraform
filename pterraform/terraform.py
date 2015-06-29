from datetime import datetime
import uuid
import shutil
import os
import json
import subprocess
from subprocess import check_output

class Terraform(dict):
    def __init__(self, source_manifest_path, variables=None):
        self.name = os.path.basename(source_manifest_path).split(".")[0]
        self.object_id = str(uuid.uuid4())
        self.source_manifest_path = source_manifest_path
        self.tmpdir = os.path.join(".", "." + self.object_id)
        self.manifestdir = os.path.join(self.tmpdir, self.name)
        self.state_path = os.path.join(self.manifestdir, "terraform.tfstate")
        self.variables = self.parse_variables(variables)

        self.copy_tmp_manifest()
        self.generate_vars_file()

    def cleanup(self):
        self.remove_tmp_manifest()

    def is_a_terraform_file(self, f):
        return (os.path.isfile(f) and (f.lower().endswith(".tf") or f.lower().endswith(".tf.json")))

    def copy_tmp_manifest(self):
        if os.path.isdir(self.source_manifest_path):
            files = [f for f in os.listdir(self.source_manifest_path) if self.is_a_terraform_file(os.path.join(self.source_manifest_path, f))]
            if len(files) > 0:
                if not os.path.isdir(self.tmpdir):
                    os.mkdir(self.tmpdir)
                shutil.copytree(self.source_manifest_path, os.path.join(self.tmpdir, self.name))
            else:
                raise(Exception("Terraform files not found.  Must have at least one *.tf or *.tf.json file to feed to Terraform."))
        elif self.is_a_terraform_file(self.source_manifest_path):
            if not os.path.isdir(self.tmpdir):
                os.mkdir(self.tmpdir)
            if not os.path.isdir(self.manifestdir):
                os.mkdir(self.manifestdir)
            shutil.copy(self.source_manifest_path, self.manifestdir)
        else:
            raise(Exception("Manifest file not found.  Must have a *.tf or *.tf.json file to feed to Terraform."))

    def generate_vars_file(self):
        with open(os.path.join(self.manifestdir, 'override.tf.json'), 'w') as vars_file:
            json.dump(self.variables, vars_file)
        vars_file.close()

    def remove_tmp_manifest(self):
        if os.path.isdir(self.tmpdir):
            shutil.rmtree(self.tmpdir)

    def state(self):
        retval = {}
        if os.path.isfile(self.state_path):
            with open(self.state_path, 'r') as state_file:
                retval = json.load(state_file)
            state_file.close()
        return retval

    def apply(self):
        self.current_stats = {}
        cmd = "terraform apply -input=false -state=" + self.state_path  + " " + self.manifestdir
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=1, shell=True)
        output = self.parse_output(p)
        p.stdout.close()
        return output

    def destroy(self):
        self.current_stats = {}
        cmd = "terraform destroy -input=false -force -state=" + self.state_path  + " " + self.manifestdir
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=1, shell=True)
        output = self.parse_output(p)
        p.stdout.close()
        return output

    def parse_output(self, process):
        retval = {
            "start_times": {},
            "durations": {}
        }
        for line in iter(process.stdout.readline, b''):
            if "Creating..." in line or "Destroying..." in line:
                object_name = line.split(": ")[0].replace('\x1b[0m\x1b[1m','')
                retval['start_times'][object_name] = datetime.utcnow()
                print line.strip() + ", starting at " + str(retval['start_times'][object_name]) + "\n"
            elif "Creation complete" in line or "Destruction complete" in line:
                object_name = line.split(": ")[0].replace('\x1b[0m\x1b[1m','')
                retval['durations'][object_name] = datetime.utcnow() - retval['start_times'][object_name]
                print line.strip() + ", with duration " + str(retval['durations'][object_name]) + "\n"
            else:
                print line
        return retval

    def parse_variables(self, variables):
        if variables is not None:
            tf_vars = {'variable': {}}
            for variable in variables:
                tf_vars['variable'][variable] = {}
                tf_vars['variable'][variable]['default'] = variables[variable]
            return tf_vars
        else:
            return None
