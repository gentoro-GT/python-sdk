import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Gentoro",
    version="0.1.0",
    author="Gentoro",
    author_email="",
    description="A Python library ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/     /Gentoro",  # Need Repo URL here
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

