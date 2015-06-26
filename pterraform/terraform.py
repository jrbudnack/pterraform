from datetime import datetime
import uuid
import shutil
import os
import json
import subprocess
from subprocess import check_output

class Terraform(dict):
    def __init__(self, manifest, variables={}):
        self.name = manifest
        self.object_id = str(uuid.uuid4())
        self.filename = manifest + ".tf"
        self.src_manifest_path = os.path.join(".", self.filename)
        self.tmpdir = os.path.join(".", "." + self.object_id)
        self.manifestdir = os.path.join(self.tmpdir, manifest)
        self.variables = self.parse_variables(variables)

        if not os.path.isfile(self.src_manifest_path):
            self.filename = self.filename + ".json"
            self.src_manifest_path = self.src_manifest_path + ".json"
        if not os.path.isfile(self.src_manifest_path):
            raise("Manifest file not found.  Must have a *.tf or *.tf.json file to feed to Terraform.")

    def copy_tmp_manifest(self):
        if os.path.isfile(self.src_manifest_path):
            if not os.path.isdir(self.tmpdir):
                os.mkdir(self.tmpdir)
            if not os.path.isdir(self.manifestdir):
                os.mkdir(self.manifestdir)
            shutil.copy(self.src_manifest_path, self.manifestdir)
        else:
            raise("Manifest file not found.  Must have a *.tf or *.tf.json file to feed to Terraform.")

    def generate_vars_file(self):
        with open(os.path.join(self.manifestdir, 'override.tf.json'), 'w') as vars_file:
            json.dump(self.variables, vars_file)
        vars_file.close()

    def remove_tmp_manifest(self):
        if os.path.isdir(self.tmpdir):
            shutil.rmtree(self.tmpdir)

    def state(self):
        print "Unimplemented."

    def apply(self):
        self.copy_tmp_manifest()
        self.generate_vars_file()
        self.current_stats = {}
        cmd = "terraform apply -input=false " + self.manifestdir
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=1, shell=True)
        output = self.parse_output(p)
        p.stdout.close()
        self.remove_tmp_manifest()
        return output

    def destroy(self):
        self.copy_tmp_manifest()
        self.generate_vars_file()
        self.current_stats = {}
        cmd = "terraform destroy -input=false -force " + self.manifestdir
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=1, shell=True)
        output = self.parse_output(p)
        p.stdout.close()
        self.remove_tmp_manifest()
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

    def parse_variables(self, variables={}):
        tf_vars = {'variable': {}}
        for variable in variables:
            tf_vars['variable'][variable] = {}
            tf_vars['variable'][variable]['default'] = variables[variable]
        return tf_vars
