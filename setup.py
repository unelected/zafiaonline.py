from setuptools import setup, find_packages

setup(
    name="zafiaonline",
    version="1.1",
    packages=find_packages(include=["zafiaonline", "zafiaonline.*"]),
    install_requires=["websockets", "msgspec"],
)