from setuptools import find_packages, setup
from pip._internal.req import parse_requirements


install_reqs = parse_requirements('requirements.txt', session='hack')
requirements = [ir.requirement for ir in install_reqs]

setup(
    name='ws_lib',
    packages=find_packages(include=["src"]),
    python_requires=">=3.8",
    version="0.0.1",
    install_requires=requirements,
    description="Wine services common code",
    author="Me",
    license="MIT",
    test_suite="tests"
)
