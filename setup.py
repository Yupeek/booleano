# -*- coding: utf-8 -*-
#
# Copyright (c) 2009 by Gustavo Narea <http://gustavonarea.net/>.
#
# This file is part of Booleano <http://code.gustavonarea.net/booleano/>.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, distribute with
# modifications, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# ABOVE COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
# IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Except as contained in this notice, the name(s) of the above copyright
# holders shall not be used in advertising or otherwise to promote the sale,
# use or other dealings in this Software without prior written authorization.

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup



HERE = os.path.abspath(os.path.dirname(__file__))
VERSION = open(os.path.join(HERE, "VERSION.txt")).readline().rstrip()
README = open(os.path.join(HERE, "README.rst")).read()


if sys.argv[-1] == 'publish':
    # os.system('cd docs && make html')
    os.system('python setup.py sdist bdist_wheel upload')
    print("You probably want to also tag the version now:")
    print("  git tag -a %s -m 'version %s'" % (VERSION, VERSION))
    print("  git push --tags")
    sys.exit()

if sys.argv[-1] == 'doc':
    os.system('cd docs && make html')
    sys.exit()


setup(name="booleano",
      version=VERSION,
      description="Boolean Expressions Interpreter",
      long_description=README,
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        "Topic :: Scientific/Engineering :: Human Machine Interfaces",
        "Topic :: Software Development :: Libraries",
        "Topic :: Text Processing :: Linguistic",
        ],
      keywords="boolean expression natural language condition conditions",
      author="Gustavo Narea",
      author_email="me@gustavonarea.net",
      url="https://github.com/Yupeek/booleano",
      download_url="https://github.com/Yupeek/booleano",
      license="MIT X License (http://www.opensource.org/licenses/mit-license.php)",
      namespace_packages=["booleano"],
      package_dir={'': "src"},
      packages=['booleano', 'booleano.parser', 'booleano.operations', 'booleano.operations.operands'],
      zip_safe=False,
      tests_require=["coverage >= 3.0", "nose >= 0.11.0", "tox"],
      install_requires=["pyparsing >= 1.5.2", "six"],
      test_suite="nose.collector",
      )

