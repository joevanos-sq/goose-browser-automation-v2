from setuptools import setup, find_packages

setup(
    name="browser-automation",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "playwright>=1.20.0",
        "pytest>=7.0.0",
        "pytest-asyncio>=0.18.0",
    ],
    extras_require={
        "test": [
            "pytest-playwright>=0.3.0",
        ],
    },
)