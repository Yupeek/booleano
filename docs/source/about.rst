==============
About Booleano
==============

Booleano is a project started by `Gustavo Narea <http://gustavonarea.net/>`_
in late April 2009, when he was working on some authorization stuff (`PyACL 
<http://pyacl.com>`_ and `repoze.what 2 <http://what.repoze.org>`_) and the
need to support user-friendly, plain text conditions arose.

it's now maintened by `Yupeek <http://my.yupeek.com>`_ for the scale rule system of
`Maiev <https://github.com/Yupeek/maiev>`_.

Contributing
------------


see :ref:`Contributing`


Coding conventions
------------------

The coding conventions for Booleano are not special at all -- they are 
basically the same you will find in other Python projects. Most of the
conventions below apply to Python files only, but some of them apply to any
source code file:

* The character encoding should be UTF-8.
* Lines should not contain more than 119 characters.
* The new line character should be the one used in Unix systems (``\n``).
* Stick to the `widely` used `Style Guide for Python Code
  <http://www.python.org/dev/peps/pep-0008/>`_ and `Docstring Conventions
  <http://www.python.org/dev/peps/pep-0257/>`_.
* The **unit test suite** for the package should cover 100% of the code and all
  its tests must pass, otherwise no release will be made. It won't make the 
  package 100% bug-free (that's impossible), but at least we'll 
  avoid regression bugs effectively and we'll be sure that a bug found will be 
  just a not yet written test. It should be easy if you practice the 
  Test-Driven Development methodology.
* All the public components of the package should be properly documented
  along with examples, so that people won't have to dive into our code to
  learn how to achieve what they want. This is optional in alpha releases only.


Acknowledgment
==============

Big thank-yous go to:

* `Paul McGuire <http://sourceforge.net/users/ptmcg>`_, for making the awesome
  `Pyparsing <http://pyparsing.wikispaces.com/>`_ package (which powers the
  Booleano parser).
* `Denis Spir <http://spir.wikidot.com/>`_, for his highly valuable
  recommendations since early in the development of this library and for
  making an `alternate Booleano parser <http://spir.wikidot.com/pijnu-samples>`_.


What's in a name?
=================

The author of the library is a Venezuelan guy who enjoys naming projects with
Castilian (aka Spanish) words. As you may have guessed, "booleano" is the
Castilian translation for "boolean".

In case you wonder how would a native speaker pronounce it, it'd be something
like "boo-leh-ah-noh".


.. _legal-terms:

Legal stuff (aka "boring stuff")
================================

Except for the logo and this documentation, or unless explicitly told otherwise,
any resource that is part of the Booleano project, including but not limited to
source code in the Python Programming Language and its in-code documentation 
("docstrings"), is available under the terms of the MIT/X License:

    Copyright (c) 2009 by Gustavo Narea.
    
    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, distribute with
    modifications, sublicense, and/or sell copies of the Software, and to permit
    persons to whom the Software is furnished to do so, subject to the following
    conditions:
    
    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.
    
    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    ABOVE COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
    WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
    IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
    
    Except as contained in this notice, the name(s) of the above copyright
    holders shall not be used in advertising or otherwise to promote the sale,
    use or other dealings in this Software without prior written authorization.

When you contribute software source code to the project, you accept to license 
your work under the terms of this license.

This documentation, on the other hand, copyright 2009 by Gustavo Narea, is 
available under the terms of the `Creative Commons Attribution-Share Alike 3.0 
Unported  License <http://creativecommons.org/licenses/by-sa/3.0/>`_. When you 
contribute documentation to the project, you accept to license your work under 
the terms of the same license.

Finally, the logo, also copyright 2009 by Gustavo Narea, is available 
under the terms of `Creative Commons Attribution-No Derivative Works 3.0 Spain 
License <http://creativecommons.org/licenses/by-nd/3.0/es/deed.en_US>`_.
