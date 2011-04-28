from setuptools import setup

setup(name="sgpy",
      classifiers = [
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 2.6"],
      description="Framework for manipulation and execution of SCSI commands using the Linux SG driver",
      license="BSD",
      author="Alon Horev",
      author_email="alonho@gmail.com",
      url="http://github.com/alonho/sgpy",
      version="0.6.1",
      packages=["sgpy"],
      install_requires=["construct"]
      )
