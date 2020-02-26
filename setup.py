import setuptools

setuptools.setup(
    name="hmt-basemodels",
    version="0.0.14",
    author="HUMAN Protocol",
    description="Common data models shared by various components of the Human Protocol stack",
    url="https://github.com/hCaptcha/hmt-basemodels",
    include_package_data=True,
    zip_safe=True,
    classifiers=[
        "Intended Audience :: Developers", "Operating System :: OS Independent",
        "Programming Language :: Python"
    ],
    packages=setuptools.find_packages(),
    install_requires=["schematics>=2.1.0", "marshmallow>=3.2.1"])
