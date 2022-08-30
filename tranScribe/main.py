import sys
import importlib
import importlib.util
import os
import inspect
import types
import json

from docutils.core import publish_parts
import docutils.utils
from bs4 import BeautifulSoup
sys.dont_write_bytecode = True


############ HELPER FUNCTIONS ###########


class ErrorDuringImport(Exception):
    """Errors that occurred while trying to import something to document it."""
    def __init__(self, filename, exc_info):
        self.filename = filename
        self.exc, self.value, self.tb = exc_info

    def __str__(self):
        exc = self.exc.__name__
        return 'problem in %s - %s: %s' % (self.filename, exc, self.value)


def describe(docstring):

    shut_up_level = docutils.utils.Reporter.SEVERE_LEVEL + 1
    body = publish_parts(docstring, writer_name='html',settings_overrides={'report_level':shut_up_level})['html_body']
    soup = BeautifulSoup(body, 'html.parser')

    #grab description as first section
    description = soup.find_all("p", limit=2)
    components = {'description':f'<div class="section" id="description"><div class="synopse">{description[0]}</div>,{description[1]}</div>'}

    sections = soup.find_all("div",{"class": "section"})
    for section in sections:
        components[section.get('id')]=section.prettify( formatter="html" )

    return components



def _getdata(object):
    """
    Gets attributes from module
    """
    branch = {}
    if hasattr(object, '__name__'):
        branch['NAME'] = str(object.__name__)
    if hasattr(object, '__doc__'):
        components = describe(inspect.getdoc(object))
        branch['DOC'] = components
    if hasattr(object, '__version__'):
        version = str(object.__version__)
        if version[:11] == '$' + 'Revision: ' and version[-1:] == '$':
            version = version[11:-1].strip()
        branch['VERSION'] = version
    if hasattr(object, '__date__'):
        branch['DATE'] = str(object.__date__)
    if hasattr(object, '__author__'):
        branch['AUTHOR']= str(object.__author__)
    if hasattr(object, '__credits__'):
        branch['CREDITS']=str(object.__credits__)
    return branch



def _isclass(object):
    return inspect.isclass(object) and not isinstance(object, types.GenericAlias)

def _importfile(path):
    """Import a Python source file or compiled file given its path."""
    magic = importlib.util.MAGIC_NUMBER
    with open(path, 'rb') as file:
        is_bytecode = magic == file.read(len(magic))
    filename = os.path.basename(path)
    name, ext = os.path.splitext(filename)
    if is_bytecode:
        loader = importlib._bootstrap_external.SourcelessFileLoader(name, path)
    else:
        loader = importlib._bootstrap_external.SourceFileLoader(name, path)
    # XXXWe probably don't need to pass in the loader here.
    spec = importlib.util.spec_from_file_location(name, path, loader=loader)
    try:
        return importlib._bootstrap._load(spec)
    except:
        raise ErrorDuringImport(path, sys.exc_info())


class Scribe:

    def __init__(self):
        self.doctree={}

    def docmodule(self, object, module_path):
        """Produce text documentation for a given module object."""
        module_breadcrumbs = module_path[:-3].replace("/", ".")
        module_name = object.__name__# ignore the passed-in name
        #maybe dome synopse here too?

        self.doctree[module_path]={'name':module_name,'path':module_path[:-3]}
        #get list of classes in module
        classes = []
        for key, value in inspect.getmembers(object, _isclass):
            classes.append((key, value))

        #get list of functions in module
        funcs = []
        for key, value in inspect.getmembers(object, inspect.isroutine):
            funcs.append((key, value))

        #get info of the classes and methods (missing hierarchy!)
        if classes:
            self.doctree[module_path]['classes'] = []
            for key, value in classes:
                branch = _getdata(value)
                branch['CRUMBS']=module_breadcrumbs +'.'+ branch['NAME']
                
                #get methods and documentize them
                methods = []
                for name, method in inspect.getmembers(value, inspect.isfunction):
                    #don't add hidden methods
                    if name.startswith('_'):
                        continue
                    methods.append((name, method))

                if methods:
                    branch['METHODS'] = []
                    for name, method in methods:
                        method_branch = _getdata(method)
                        branch['METHODS'].append(method_branch)
                        
                self.doctree[module_path]['classes'].append(branch)

        #get infot on functions
        if funcs:
            self.doctree[module_path]['functions'] = []
            for key, value in funcs:
                branch = _getdata(value)
                branch['CRUMBS']=module_breadcrumbs + '.' + branch['NAME']
                self.doctree[module_path]['functions'].append(branch)
      
        return self





def main(SOURCE='example_dir'):

    scribe = Scribe()
    for root, dirs, files in os.walk(SOURCE, topdown='true'):

        for filename in files:
            if not filename.endswith(".py"):
                continue
            else:
                module_path = os.path.join(root, filename)
                object = _importfile(module_path)
                scribe.docmodule(object, module_path)


    with open('transcription.json', 'w') as fp:
        json.dump(scribe.doctree, fp)



if __name__ == "__main__":
    main()
