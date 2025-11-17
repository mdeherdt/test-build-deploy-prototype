from setuptools import setup, find_packages

setup(
    name="service_b",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "httpx>=0.20.0",
    ],
)