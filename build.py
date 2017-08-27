import os
import sys
import urllib
import hashlib
import traceback
import zipfile
import shutil
import requests

PYTHON_PATH = sys.executable
WINDOWS = sys.platform.startswith("win")

# (C) Freshollie - Oliver Bell - 2017

class Builder:
    RESOURSES_LIST = [
        {
            "name": "panda3d",
            "url": "https://github.com/freshollie/panda3d/archive/00150976f7b233b4be54e68a36785187a4bfa77b.zip",
            "hash": "a7f6ea1eb6588db9340fc0a89f3d1cd1",
            "built_checks": [".deb", ".exe"]
        }#,
        #{
        #    "name":"resources",
        #    "url": "https://github.com/freshollie/toontown-infinite-resources/archive/master.zip",
        ##    "hash": "1085702ec32d85a4c8d09fa846a57f01",
        #    "built_checks": []
        #}
    ]

    if not WINDOWS:
        RESOURSES_LIST.append({
            "name": "Astron",
            "url": "https://github.com/freshollie/Astron/archive/3a15606ab15b63b666fdff1e0145417470232dbc.zip",
            "hash": "ffcdbab1cd99c9b6c40d52dce156f0b9",
            "built_checks":["astrond"]
        })

    def __init__(self):
        if WINDOWS:
            os.system("@echooff")

    def _make_dir_hash(self, directory):
        exclude = [".git"]

        sha_hash = hashlib.md5()
        if not os.path.exists(directory):
            return -1

        try:
            for root, dirs, files in os.walk(directory):
                dirs[:] = [d for d in dirs if d not in exclude]
                for names in files:
                    filepath = os.path.join(root, names)
                    try:
                        f1 = open(filepath, 'rb')
                    except:
                        # You can't open the file for some reason
                        f1.close()
                        continue

                    while 1:
                        # Read file in as little chunks
                        buf = f1.read(4096)
                        if not buf: break
                        sha_hash.update(hashlib.md5(buf).hexdigest())
                    f1.close()

        except:
            # Print the stack traceback
            traceback.print_exc()
            return -2

        return sha_hash.hexdigest()

    def _find_resource_object(self, name):
        for resource in Builder.RESOURSES_LIST:
            if resource["name"] == name:
                return resource
        return None

    def _download_resource(self, resource):
        r = requests.get(resource["url"], stream=True)
        with open(resource["name"] + ".zip", 'wb') as f:
            shutil.copyfileobj(r.raw, f)

        return resource["name"] + ".zip" in os.listdir(".")

    def _extract_resource(self, resource):
        if resource["name"] + ".zip" in os.listdir("."):
            directory_name = None
            resource_zip = zipfile.ZipFile(resource["name"] + ".zip")
            resource_zip.extractall()
            resource_zip.close()
            for folder in os.listdir("."):
                if folder.startswith(resource["name"]) and not len(folder.split("-")) > 2:
                    os.rename(folder, resource["name"])
                    break
            return self._check_resource(resource)
        return False

    def _is_built(self, resource):
        if type(resource) == str:
            resource = self._find_resource_object(resource)

        for built_check in resource["built_checks"]:
            for resource_file in os.listdir(resource["name"]):
                if resource_file.endswith(built_check):
                    return True
        return False

    def _check_resource(self, resource):
        '''
        Checks if the directory is clean, otherwise it checks if its already built,
        otherwise it returns false
        '''

        if self._make_dir_hash(resource["name"]) == resource["hash"] and len(os.listdir(resource["name"])) > 1:
            return True

        if os.path.isdir(resource["name"]):
            return self._is_built(resource)

        return False

    def _check_missing_resources(self):
        missing = []
        for resource in Builder.RESOURSES_LIST:
            if not self._check_resource(resource):
                print(resource["name"] + " missing or doesn't match hash")
                missing.append(resource)
        return missing

    def _restore_missing(self, missing):
        for resource in missing:
            # Delete the old version seeing as we are redownloading
            if resource["name"] in os.listdir("."):
                shutil.rmtree(resource["name"])

            print("Downloading " + resource["name"] + " files")
            if not self._download_resource(resource):
                print(resource["name"] + " could not be downloaded")
                return False

            print("Extracting " + resource["name"] + " files")
            if not self._extract_resource(resource):
                print("Failed to extract " + resource["name"])
                return False

            os.remove(resource["name"]+".zip")
        return True

    def _build_panda(self):
        if self._is_built("panda3d"):
            return True
        return True

    def _build_astron(self):
        if WINDOWS or self._is_built("Astron"):
            return True


        return True

    def _install_astron(self):
        return True

    def _install_panda3d(self):
        return True
    
    def build(self):
        print("Checking resources")
        missing = self._check_missing_resources()
        if not self._restore_missing(missing):
            return False

        if self._check_missing_resources():
            print("Failed to collect missing resources")
            return False

        print("Starting resources build")

        print("Building astron")
        if not self._build_astron():
            print("Failed to build astron")
            return False

        print("Building panda3d")
        if not self._build_panda():
            print("Failed to build panda3d")
            return False

        print("Starting resources install")
        print("Installing astron into src")
        if not self._install_astron():
            print("Failed to install astron")
            print

        print("Installing panda3d")
        if not self._install_panda3d():
            print("Failed to install panda3d")

        return True

if __name__ == "__main__":
    if not Builder().build():
        print("Build failed")
    else:
        print("Build completed, toontown can now be executed")
    print("-" * 30)
    input("Press enter to exit")
    sys.exit()

# Ready to download these sources if they do not exist

# https://github.com/freshollie/panda3d/archive/00150976f7b233b4be54e68a36785187a4bfa77b.zip
# https://github.com/freshollie/Astron/archive/3a15606ab15b63b666fdff1e0145417470232dbc.zip
# https://github.com/freshollie/toontown-infinite-resources/archive/f7cfe07d35893bf0c964e668bc46fb605e317d4d.zip
#https://github.com/freshollie/toontown-infinite-source/archive/master.zip