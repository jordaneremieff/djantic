from setuptools import find_packages, setup


__version__ = "0.6.0"


def get_long_description():
    return open("README.md", "r", encoding="utf8").read()


setup(
    name="djantic",
    version=__version__,
    packages=find_packages(),
    license="MIT",
    url="https://github.com/jordaneremieff/djantic/",
    description="Pydantic model support for Django ORM",
    long_description=get_long_description(),
    python_requires=">=3.7",
    package_data={"djantic": ["py.typed"]},
    long_description_content_type="text/markdown",
    author="Jordan Eremieff",
    author_email="jordan@eremieff.com",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Framework :: Django :: 3.0",
        "Framework :: Django :: 3.1",
        "Framework :: Django :: 3.2",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
