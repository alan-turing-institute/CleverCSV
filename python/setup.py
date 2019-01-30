import setuptools

with open("README.md", "r") as fid:
    long_description = fid.read()

setuptools.setup(
    name="ccsv",
    version="0.0.1",
    author="Gertjan van den Burg",
    author_email="gertjanvandenburg@gmail.com",
    description="A clever CSV parser",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CleverCSV/ccsv",
    packages=setuptools.find_packages(),
    classifiers=["Programming Language :: Python :: 3"],
)
