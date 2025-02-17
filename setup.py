import setuptools


def read_requirements():
    with open("requirements.txt", encoding="utf-8") as req_file:
        return req_file.read().splitlines()


setuptools.setup(
    name="Gentoro",
    version="0.1.0",
    author="Gentoro",
    author_email="",
    description="Gentoro Python SDK for AI tool execution and authentication",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/gentoro-GT/python-sdk",  # Need Repo URL here
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=read_requirements(),
    include_package_data=True,
    license="Apache-2.0",
)
