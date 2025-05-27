from setuptools import setup, find_packages

setup(
    name="BroadieLLM",
    version="1.0",
    description="A Broadie Chat module",
    author="Vivek Salgia",
    author_email="vsalgia@broadinstitute.org",
    packages=find_packages(),  # same as name
    # install_requires=["wheel", "bar", "greek"],  # external packages as dependencies
)
