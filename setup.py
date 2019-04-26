import setuptools

setuptools.setup(
    name="hmt-basemodels",
    version="0.0.2",
    author="HUMAN Protocol",
    description="Basemodels for manifest data used by hmt-escrow",
    url="https://github.com/hCaptcha/hmt-basemodels",
    include_package_data=True,
    zip_safe=True,
    classifiers=[
        "Intended Audience :: Developers",
        "Operating System :: OS Independent", "Programming Language :: Python"
    ],
    packages=setuptools.find_packages(),
    install_requires=["schematics==2.1.0", "yapf==0.25.0", "mypy==0.670"])
