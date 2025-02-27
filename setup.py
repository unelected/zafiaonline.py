from setuptools import setup, find_packages

setup(
    name="zafiaonline",
    version="2.4.12",
    packages=find_packages(include=["zafiaonline", "zafiaonline.*"]),
    install_requires=["websockets", "msgspec", "sphinx"],
    description="A Python API library for interacting with Mafia Online game.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/unelected/zafiaonline.py",
    python_requires=">=3.9",
)
