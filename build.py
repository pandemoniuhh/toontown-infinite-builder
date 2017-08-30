import os
import sys
import hashlib
import traceback
import zipfile
import shutil
import platform
import importlib

try:
    import pip
except ImportError:
    print("Pip must be installed to build")
    sys.exit(1)

requests = None

PYTHON_PATH = sys.executable
WINDOWS = sys.platform.startswith("win")

# (C) Freshollie - Oliver Bell - 2017

if platform.machine().endswith('64'):
    BITS = 64
else:
    BITS = 32

class Builder:
    LIBRARY_BUILD_STRING = "apt-get install -y " \
                           "build-essential pkg-config " \
                           "python-dev libpng-dev " \
                           "libjpeg-dev libtiff-dev " \
                           "zlib1g-dev libssl-dev libx11-dev " \
                           "libgl1-mesa-dev libxrandr-dev " \
                           "libxxf86dga-dev libxcursor-dev " \
                           "bison flex libfreetype6-dev " \
                           "libvorbis-dev libeigen3-dev " \
                           "libopenal-dev libode-dev " \
                           "libbullet-dev nvidia-cg-toolkit " \
                           "libgtk2.0-dev libssl-dev " \
                           "libyaml-dev libboost-all-dev " \
                           "cmake"

    RESOURSES_LIST = [
        {
            "name": "panda3d",
            "url": "https://github.com/freshollie/panda3d/archive/00150976f7b233b4be54e68a36785187a4bfa77b.zip",
            "hash": "a0c0afd726b0196ceb1377be8c353b8f",
            "zip_hash":"1c2d1a41c60195b4b68ab303ce55283e",
            "built_checks": [".deb", ".exe"]
        },
        {
            "name": "resources",
            "url": "https://github.com/freshollie/toontown-infinite-resources/archive/master.zip",
            "hash": "333d87cd82228ffde4e048ee3729a9d5",
            "zip_hash": "",
            "built_checks": []
        },
        {
            "name": "src",
            "url": "https://github.com/freshollie/toontown-infinite-source/archive/master.zip",
            "hash": "-25", # This really doesn't want to be deleted automatically
            "built_checks": [],
            "zip_hash": ""
        }
    ]

    if not WINDOWS:
        RESOURSES_LIST.append({
            "name": "Astron",
            "url": "https://github.com/freshollie/Astron/archive/3a15606ab15b63b666fdff1e0145417470232dbc.zip",
            "hash": "8b64d03af9b04a7c31816de79646c13a",
            "zip_hash": "",
            "built_checks": ["astrond"]
        })

        RESOURSES_LIST.append({
            "name": "panda-tools" + str(BITS),
            "built_checks": []
        })

        if BITS==64:
            RESOURSES_LIST[-1]["url"] = "https://www.panda3d.org/download/panda3d-1.9.0/panda3d-1.9.0-tools-win64.zip"
            RESOURSES_LIST[-1]["hash"] = "d41d8cd98f00b204e9800998ecf8427e"
            RESOURSES_LIST[-1]["zip_hash"] = "719a5c0c5d4337f91efcb1c6d1910f5d"
        else:
            RESOURSES_LIST[-1]["url"] = "https://www.panda3d.org/download/panda3d-1.9.0/panda3d-1.9.0-tools-win32.zip"
            RESOURSES_LIST[-1]["hash"] = "3c7db76fd8238c4669ce71c6294586a6"
            RESOURSES_LIST[-1]["zip_hash"] = "10dea9a525f86bf11c62432e2a14dbab"

    def __init__(self):
        if WINDOWS:
            os.system("@echooff")

    def _make_file_hash(self, file_path):
        file_hash = hashlib.md5()

        try:
            f1 = open(file_path, 'rb')
        except:
            # You can't open the file for some reason
            return ""

        while 1:
            # Read file in as little chunks
            buf = f1.read(4096)
            if not buf: break
            file_hash.update(buf)

        f1.close()
        return file_hash.hexdigest()

    def _make_dir_hash(self, directory):
        exclude = [".git", "thirdparty"]

        sha_hash = hashlib.md5()
        if not os.path.exists(directory):
            return "-1"

        try:
            for root, dirs, files in os.walk(directory):
                dirs[:] = [d for d in dirs if d not in exclude]
                for names in files:
                    filepath = os.path.join(root, names)
                    file_hash = self._make_file_hash(filepath)
                    if file_hash:
                        sha_hash.update(file_hash)

        except:
            # Print the stack traceback
            traceback.print_exc()
            return "-2"

        return sha_hash.hexdigest()

    def _find_resource_object(self, name):
        for resource in Builder.RESOURSES_LIST:
            if resource["name"] == name:
                return resource
        return None

    def _download_resource(self, resource):
        if resource["name"] + ".zip" in os.listdir("."):
            zip_hash = self._make_file_hash(resource["name"] + ".zip")
            print("Found local " + resource["name"] + " zip with hash: " + zip_hash)
            if zip_hash == resource["zip_hash"]:
                return True
            else:
                print("Local zip not valid")

        r = requests.get(resource["url"], stream=True)
        with open(resource["name"] + ".zip", 'wb') as f:
            shutil.copyfileobj(r.raw, f)

        return resource["name"] + ".zip" in os.listdir(".")

    def _extract_resource(self, resource):
        if resource["name"] + ".zip" in os.listdir("."):
            resource_zip = zipfile.ZipFile(resource["name"] + ".zip")
            resource_zip.extractall()

            if resource_zip.namelist()[0].split("/")[0] in os.listdir("."):
                os.rename(resource_zip.namelist()[0].split("/")[0], resource["name"])

            else:
                resource_zip.close()
                return False

            resource_zip.close()
            return self._check_resource(resource)
        return False

    def _is_built(self, resource):
        if type(resource) == str:
            resource = self._find_resource_object(resource)

        if (resource["name"] == "src"):
            if os.path.isdir("src/astron"):
                if "astrond" in os.listdir("src/astron") or "astron.exe" in os.listdir("src/astron"):
                    return True

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

        resource_hash = self._make_dir_hash(resource["name"])

        print(resource["name"] + " hash: " + resource_hash)

        if resource_hash == resource["hash"]:
            return True

        if resource_hash == "-25":
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
            print(self._make_dir_hash(resource["name"] + ".zip"))

            print("Extracting " + resource["name"] + " files")
            if not self._extract_resource(resource):
                print("Failed to extract " + resource["name"])
                return False

            #os.remove(resource["name"]+".zip")
        return True

    def _build_panda(self):
        if self._is_built("panda3d"):
            return True

        if WINDOWS:
            print("Copying panda-tools into panda3d")
            shutil.copytree("panda-tools64/thirdparty", "panda3d/thirdparty")

        os.chdir("panda3d")

        if WINDOWS and os.system("makepanda\\makepanda.bat --everything --installer --no-eigen"):
            return False
        elif os.system(sys.executable + " makepanda/makepanda.py --everything --installer --no-egl --no-gles --no-gles2"):
            return False

        if WINDOWS:
            shutil.rmtree("panda3d/thirdparty")

        os.chdir("../")
        return True

    def _build_astron(self):
        if WINDOWS or self._is_built("Astron"):
            return True
        else:
            os.chdir("Astron")
            os.system("cmake -DCMAKE_BUILD_TYPE=Release . && make")
            os.chdir("../")
            return True

    def _install_build_libraries(self):
        if os.system(Builder.LIBRARY_BUILD_STRING):
            return False

        return pip.main(['install', "pyyaml"]) == 0

    def _install_astron(self):
        if WINDOWS:
            shutil.copy("Astron-windows-binaries/astrond.exe", "src/astron/astrond.exe")
            shutil.copy("Astron-windows-binaries/libeay32.dll", "src/astron/libeay32.dll")
            shutil.copy("Astron-windows-binaries/ssleay32.dll", "src/astron/ssleay32.dll")
        else:
            shutil.copy("Astron/astrond", "src/astron/astrond")

        return True

    def _install_panda3d(self):
        os.chdir("panda3d")
        if WINDOWS:
            print("Please follow instructions on screen")
            os.system("install.exe")
        else:
            os.system("sudo dpkg -i panda3d*.deb")
        os.chdir("../")
        return True
    
    def build(self):
        print("Checking requirements")

        try:
            importlib.import_module("requests")
        except ImportError:
            pip.main(['install', "requests"])
        finally:
            globals()["requests"] = importlib.import_module("requests")

        if not self._install_build_libraries():
            print("Failed to collect some linux requirements")
            return False

        print("Checking resources")

        missing = self._check_missing_resources()

        if not WINDOWS and not self._restore_missing(missing):
            return False

        if missing and self._check_missing_resources():
            print("Failed to collect missing resources")
            return False

        print("Starting dependencies build")

        print("Building astron")
        if not self._build_astron():
            print("Failed to build astron")
            return False

        print("Building panda3d")
        if not self._build_panda():
            print("Failed to build panda3d")
            return False

        print("Starting dependencies install")
        print("Installing astron into src")
        if not self._install_astron():
            print("Failed to install astron")
            return False

        print("Installing panda3d")
        if not self._install_panda3d():
            print("Failed to install panda3d")
            return False

        return True

if __name__ == "__main__":
    if not WINDOWS and not os.geteuid() == 0:
        print("Please execute this as sudo!")
        sys.exit(1)

    if not Builder().build():
        print("Build failed")
    else:
        print("Build completed, toontown can now be executed")
    print("-" * 30)
    #input("Press enter to exit")
    sys.exit(0)

# Ready to download these sources if they do not exist

# https://github.com/freshollie/panda3d/archive/00150976f7b233b4be54e68a36785187a4bfa77b.zip
# https://github.com/freshollie/Astron/archive/3a15606ab15b63b666fdff1e0145417470232dbc.zip
# https://github.com/freshollie/toontown-infinite-resources/archive/f7cfe07d35893bf0c964e668bc46fb605e317d4d.zip
#https://github.com/freshollie/toontown-infinite-source/archive/master.zip