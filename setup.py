from setuptools import setup

setup(
    name="zafiaonline",
    version="1.0",
    packages=["zafiaonline". "zafiaonline.*"],
    install_requires=["websockets", "msgspec"],
)