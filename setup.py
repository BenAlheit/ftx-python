import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ftx-python",
    version="0.0.3",
    author="Ben Alheit",
    author_email="alheitb@gmail.com",
    description="A python client for the FTX exchange",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BenAlheit/ftx_python",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'websockets',
        'ciso8601'
    ],
    python_requires='>=3.6',
)
