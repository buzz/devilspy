#!/usr/bin/env python3
"""setup.py for devilspy"""

import re
import sys
from setuptools import find_packages, setup

if sys.version_info < (3, 2):
    raise SystemExit("devilspy requires Python 3.2 or later.")

# parse version (setup.py should not import module!)
def get_version():
    """Get version using regex parsing."""
    versionfile = "devilspy/meta.py"
    with open(versionfile, "rt") as file:
        version_file_content = file.read()
    match = re.search(r"^VERSION = ['\"]([^'\"]*)['\"]", version_file_content, re.M)
    if match:
        return match.group(1)
    raise RuntimeError("Unable to find version string in {}.".format(versionfile))


setup(
    name="devilspy",
    version=get_version(),
    description="Window matching utility",
    author="buzz",
    author_email="buzz@users.noreply.github.com",
    license="GPLv2",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Environment :: No Input/Output (Daemon)",
        "Environment :: X11 Applications",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Operating System :: POSIX :: Linux",
        "Topic :: Desktop Environment",
    ],
    url="https://github.com/buzz/devilspy",
    packages=find_packages(),
    install_requires=["click", "PyGObject", "PyYAML"],
    include_package_data=True,
    entry_points={"console_scripts": ["devilspy = devilspy.__main__:main"]},
)
