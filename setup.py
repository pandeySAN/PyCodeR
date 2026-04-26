from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="pylint-pro",
    version="2.0.0",
    author="Your Name",
    description="Production-grade static code analyzer with cross-file analysis and caching",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.8",
    install_requires=[
        # No runtime dependencies - stdlib only!
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'coverage>=6.0',
            'pre-commit>=2.20.0',
        ]
    },
    entry_points={
        "console_scripts": [
            "pylint-pro=src.cli:main",
        ],
    },
)
