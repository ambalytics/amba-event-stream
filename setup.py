import setuptools
import versioneer

# todo test versioneer

# read long_description
with open("README.md", "r") as fh:
    long_description = fh.read()

# read requirements
with open("requirements.txt", "r") as fh:
    requirements = [line.strip() for line in fh]

# setup
setuptools.setup(
    name="amba-event-stream",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="Lukas Jesche",
    author_email="lukas.jesche.se@gmail.com",
    description="amba-event-stream for kafka",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=requirements,
)