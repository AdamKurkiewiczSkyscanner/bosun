#!/bin/python
from __future__ import print_function
import os
import sys
import time
import urllib
import subprocess

USAGE = """
Usage:  %(programName)s <bosunVersionString>

Example: %(programName)s 0.5.0.1-rc2
""" % {"programName": sys.argv[0]}

DOCKERFILE = """
FROM centos:7
RUN mkdir -p /data /bosun

COPY bosun.conf /data/
COPY %(bosunPath)s /bosun/

EXPOSE 8070
RUN chmod +x /bosun/%(bosunPath)s
CMD ["/bosun/%(bosunPath)s", "-c", "/data/bosun.conf"]
"""

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def downloadBosun(bosunURL, destinationPath):
    print("Assuming that bosun executable lives under the URL:", bosunURL)
    time.sleep(1)
    print("Attempting to download bosun.")
    downloadBosun = urllib.FancyURLopener()
    downloadBosun.retrieve(bosunURL, destinationPath)
    print("Bosun saved on the filesystem under path:", destinationPath)

def downloadBosunCarefully(bosunURL, destinationPath): 
    try:
        downloadBosun(bosunURL, destinationPath)
    except Exception as e:
        eprint("Something went wrong while downloading bosun")
        raise e

def isBosunDownloaded(destinationPath):
    print("Checking if correct version of bosun is already downloaded.")
    try:
        statinfo = os.stat(destinationPath)
    except OSError:
        print("Looks like correct version of bosun is not downloaded yet.")
        return False
    print("Looks like correct version of bosun is already downloaded.")
    return True

def buildDocker(absoluteWorkingDir, bosunPath):
    print("Overwriting Dockerfile.")
    dockerfileContents = DOCKERFILE % {"bosunPath": bosunPath}
    with open(os.path.join(absoluteWorkingDir, "Dockerfile"), "w") as dockerfile:
        dockerfile.write(dockerfileContents)
    os.chdir(absoluteWorkingDir) # because docker's "build context" sucks
    print("Building Dockerfile.")
    subprocess.call(["docker", "build", "."])

def buildDockerCarefully(*args):
    try:
        buildDocker(*args)
    except Exception as e:
        eprint("Can't build the docker container")
        raise e

def selfDirAbsPath():
    fileAbsPath = os.path.abspath(__file__)
    return os.path.dirname(fileAbsPath)


if os.geteuid() != 0:
    eprint("run as root")
    sys.exit(1)

if len(sys.argv) < 2:
    eprint("Pass in bosun version string as first argument.")
    eprint(USAGE)
    sys.exit(1)

repository = "https://github.com/Skyscanner/bosun/releases/download/%(bosunVersionString)s/bosun"
bosunVersion = sys.argv[1]
bosunVersionFormatDict = {"bosunVersionString": bosunVersion}
bosunURL = repository % bosunVersionFormatDict
absoluteWorkingDir = selfDirAbsPath()
bosunDestinationRelPath = "bosun-%(bosunVersionString)s" % bosunVersionFormatDict
bosunDestinationPath = os.path.join(absoluteWorkingDir, bosunDestinationRelPath)

if isBosunDownloaded(bosunDestinationPath):
    pass
else:
    downloadBosunCarefully(bosunURL, bosunDestinationPath)
buildDockerCarefully(absoluteWorkingDir, bosunDestinationRelPath)
