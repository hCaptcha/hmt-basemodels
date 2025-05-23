import setuptools

setuptools.setup(
    name="hmt-basemodels",
    version="1.3.3",
    author="HUMAN Protocol",
    description="Common data models shared by various components of the Human Protocol stack",
    url="https://github.com/hCaptcha/hmt-basemodels",
    include_package_data=True,
    zip_safe=True,
    classifiers=[
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    packages=setuptools.find_packages(),
    install_requires=["requests>=2", "typing-extensions", "pydantic>=2.5.3"],
)
