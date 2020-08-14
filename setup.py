#!/usr/bin/env python3
"""setup.py for devilspy"""

import re
from setuptools import find_packages, setup


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
    url="https://buzz.github.io/devilspy/",
    packages=find_packages(),
    entry_points={"gui_scripts": ["devilspy = devilspy.__main__:main"]},
)
