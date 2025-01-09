from setuptools import find_packages, setup

from typing import List

# setup.py is to install our source code
REQUIREMENT_FILE_NAME = "requirements.txt"
HYPHEN_E_DOT = "-e ."  # install our source code as library(-e is editable or install)


def get_requirements() -> list[str]:
    with open(REQUIREMENT_FILE_NAME) as requirement_file:
        requirement_list = requirement_file.readlines()
    requirement_list = [requirement_name.replace("\n", "") for requirement_name in requirement_list]

    if HYPHEN_E_DOT in requirement_list:
        requirement_list.remove(HYPHEN_E_DOT)
    return requirement_list


setup(
    name="Store",
    version="0.0.1",
    author="praveen",
    author_email="tumatipraveenreddy23@gmail.com",
    packages=find_packages(),
    install_requires=get_requirements(),
)