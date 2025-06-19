# Translation utility for When

This utility contains some quick and dirty functions that can be used to create a draft translation of the string constants that should be translated in **When**. The goal is to produce a _strings_XX.py_ (being _XX_ the target language, in lowercase) file that can be copied in the _lib/i18n_ folder, so that **When** can use it to translate UI (and CLI) elements.

The mandatory folders are:

* _INPUT_: input files, which will be left untouched, should be copied here, that is
  * _strings_base.py_: the default translatable UI strings, that are used to build the template and to ask for translations
  * _strings_XX.py_: existing, good, human-edited translations which could also be incomplete
  * _strings.py_: a mock version of the strings loader, which only defines variables used in _strings_base.py_, and that should be left alone along with its copy in _TEMP_
* _OUTPUT_: will contain output files, usually empty
* _TEMP_: this utility uses this folder for intermediate results, it should **mandatorily** contain an exact copy of _strings.py_ as found in _INPUT_.

In order to preserve the directories through _git_ commits, a placeholder file named _placeholder.txt_ is left in each of them.

To use the environment, run `poetry install` and `poetry shell` to enter the virtual environment, then run `jupiter-lab`. Double click the _translate.ipynb_ notebook, and follow the instructons.

In order to avoid cluttering the real source tree, this subtree should be copied to a directory outside the **When** project and used from there.
