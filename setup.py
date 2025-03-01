from setuptools import setup, find_packages

def get_requirements():
    with open("requirements.txt") as file:
        requirements = file.read().splitlines()
    if "-e ." in requirements:
        requirements.remove("-e .")
    return requirements

setup(
    name="store_app",
    version="0.0.1",
    author="Praveen",
    author_email="tumatipraveenreddy23@gmail.com",
    packages=find_packages(include=["store*", "utils*", "constants*"]),
    include_package_data=True,  # Includes non-code files specified in MANIFEST.in
    install_requires=get_requirements(),
)
