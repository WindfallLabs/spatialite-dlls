#! /usr/bin/python
# -*- coding: utf-8 -*-
"""
SpatiaLite Binary Retriever Script
Garin Wally; May 2016

This script gets the SpatiaLite DLLs from the web, and converts the .7z file
into a .zip file if 7z.exe is found.

USAGE:
$ python helper_scripts/get_spatialite.py
    --ignore_version: force downloads the binary files regardless of version
"""

import argparse
from glob import glob
import os
import re
import requests
import shutil
import sys
from subprocess import call
from urlparse import urljoin
import zipfile

readme_content = (
    "\nThis is a direct copy of the mod_spatialite-*.7z file available from "
    "http://www.gaia-gis.it/gaia-sins/windows-bin-x86 that has been converted "
    "into .zip format for wider use by those without the 7-Zip software."
    )

# ==============================================================================
# PATHS

# SpatiaLite Homepage
home_url = "https://www.gaia-gis.it/fossil/libspatialite/home"
# FTP-like download site; Direct access is Forbidden
bin_url = "https://www.gaia-gis.it/gaia-sins/windows-bin-x86/"
# SpatiaLite version number stored in README
readme = os.path.abspath(r".\README.txt")
# Existing .zip of binaries
old_bin = os.path.abspath(r".\bin.zip")
# Path to 7z.exe
sevenzip_app = r"C:\Program Files (x86)\7-Zip\7z.exe"

# ==============================================================================
# MAIN FUNCTION


def main():
    # ==========================================================================
    # CHECK SPATIALITE VERSION

    # Get current version of webpage
    home_html = requests.get(home_url).text
    web_version = re.findall("current version is <b>(.*)</b>", home_html)[0]
    mod_folder = "mod_spatialite-{}-win-x86".format(web_version)
    print("Current Version: {}".format(web_version))

    # Compare with textfile
    if not args.ignore_version:
        with open(readme, "r+") as f:
            content = f.readlines()
            cur_version = content[0].strip()
            if cur_version <= web_version:
                sys.exit("No updates available")
            else:
                print("Updating...")
                f.seek(0)
                f.write("\n\n".join([web_version, readme_content]))

    else:
        # Remove duplicates / old versions
        if os.path.exists(old_bin):
            os.remove(old_bin)
        if os.path.exists(mod_folder):
            shutil.rmtree(mod_folder)

    # ==========================================================================
    # CREATE URLS & DOWNLOAD .7z

    dlls = "{}.7z".format(mod_folder)
    dlls_url = urljoin(bin_url, dlls)

    r = requests.get(dlls_url, stream=True)

    if r.status_code == 200:
        with open("bin.7z", "wb") as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)
    else:
        raise IOError("Request Failed with Status Code: {}".format(
            r.status_code))

    # ==========================================================================
    # EXTRACT .7z
    # Reasoning: not everyone has 7-Zip, or can easily get it (requires admin
    #   permissions)

    zipped = os.path.abspath("bin.7z")
    print("Extracting .7z file...")
    call([sevenzip_app, "x", zipped])

    # ==========================================================================
    # RE-ZIP

    to_zip = glob("mod_spatialite*")[0]

    print("Compressing to .zip...")
    rezip = zipfile.ZipFile(r".\bin.zip", "w", zipfile.ZIP_DEFLATED)
    for fname in os.listdir(os.path.join(os.getcwd(), to_zip)):
        rezip.write(os.path.join(to_zip, fname))
    rezip.close()

    # TODO: automate the update to github process


# ==============================================================================
# RUN IT

if __name__ == "__main__":
    # ==========================================================================
    # ARGS
    argp = argparse.ArgumentParser()

    # Override use of "spatialite_version.txt" to test for version
    argp.add_argument("--ignore_version", action="store_true",
                      dest="ignore_version", default=False,
                      help="Force download")

    args = argp.parse_args()

    main()
    print("\nDONE!\n")
