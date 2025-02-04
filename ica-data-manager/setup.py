from setuptools import setup, find_packages

setup(
    name="ica-data-manager",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandas>=1.5.0",
        "numpy>=1.21.0",
        "pyyaml>=6.0",
        "requests>=2.28.0",
        "illumina-ica>=1.0.0",  # Illumina Connected Analytics SDK
        "biopython>=1.80",      # For biological sequence handling
        "icav2",                # ICA v2 CLI
        "tabulate>=0.9.0",      # For table formatting
    ],
    author="ATGCU",
    author_email="your.email@example.com",
    description="ICA (Illumina Connected Analytics) Data Management Package",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ica-data-manager",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    python_requires=">=3.8",
) 