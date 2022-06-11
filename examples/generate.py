#!/usr/bin/python3

from urllib.parse import quote
import glob
import os
import re
import subprocess
import sys

CHROMIUM_PATH = "chromium"
IMAGE_MAGICK = "convert"

def generateScreenShot(name):
    example = open(name, "rb")
    url = "file://%s/container.html?mathBase64=%s" % (
        os.path.dirname(os.path.realpath(sys.argv[0])),
        quote(example.read())
    )
    print("Opening %s..." % url)
    image = name.replace(".html", ".png")
    subprocess.run([CHROMIUM_PATH,
                    "--headless",
                    "--disable-gpu",
                    "--screenshot=%s" % image,
                    "--enable-blink-features=MathMLCore",
                    "--window-size=500x500",
                    url])
    components = subprocess.check_output([IMAGE_MAGICK,
                                          image,
                                          "-define", "connected-components:verbose=true",
                                          "-connected-components", "4",
                                          "-auto-level",
                                          "out.png"]).decode('ascii')
    os.remove("out.png")
    for line in components.splitlines():
        match = re.match("^\s+0: ([0-9]+x[0-9]+\+0\+0)", str(line))
        if match:
            subprocess.run([IMAGE_MAGICK,
                            image,
                            "-transparent", "white",
                            "-crop", match.groups()[0],
                            image])
            break
     
print("Generation assumes chromium is available.")
print("Use the committed examples in git.\n")

# Generate screenshot for the specified file example, or for all of them.
if len(sys.argv) >= 2:
    generateScreenShot(sys.argv[1])
else:
    for name in glob.glob("example-*.html"):
        if not name.startswith("example-without-screenshot"):
            generateScreenShot(name)
