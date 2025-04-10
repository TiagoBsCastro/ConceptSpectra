from setuptools import setup, find_packages

setup(
    name="ConceptSpectra",
    version="1.0.0",
    author="Tiago Castro and Jeppe Dakin",
    author_email="tiago.castro@inaf.it",
    description="Compute linear power spectra in cosmology using CLASS with concept.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/TiagoBsCastro/ConceptSpectra",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        # Note: ConceptSpectra is intended to be used from the Python environment installed with it.
    ],
    entry_points={
        "console_scripts": [
            "conceptspectra=ConceptSpectra.cli:main",
        ],
    },
)
