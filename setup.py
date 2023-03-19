from setuptools import setup

setup(
    name="apc",
    version="0.0.1",
    packages=["apc"],
    entry_points={
        "console_scripts": [
            "apc=apc.__main__:main"
        ]
    }
)