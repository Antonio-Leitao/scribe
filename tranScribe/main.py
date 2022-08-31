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
    if callable(object):
        branch['SIGNATURE'] = str(inspect.signature(object))
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
        self.separate_classes = True
        self.separate_functions = False
    
    def transcribe(self, in_path,out_path):
        #do a check here?
        self.pkgname = os.path.split(in_path)[-1]
        self.doctree = self.get_doctree(in_path)
        with open(out_path, 'w') as fp:
            json.dump(self.doctree, fp)
        return self

    def _clean_href(self, root):
        href = root.removeprefix(self.pkgname)
        if len(href)==0:
            href='/'
        return href

    def get_doctree(self,path): 
        for root, dirs, files in os.walk(path):
            doctree = {"href": self._clean_href(root), "type":"folder", "children":[]}
            doctree["children"].extend([self.get_doctree(os.path.join(root, d)) for d in dirs])
            for f in files:
                if not f.endswith('.py'):
                    continue
                object = _importfile(os.path.join(root, f))
                self.document(object, child_list=doctree['children'], root = self._clean_href(root))
            return doctree

    def document(self, object, child_list , root):
        """Generate documentation for an object."""
        try:
            if inspect.ismodule(object): return self.docmodule(object,child_list,root)
            if _isclass(object): return self.docclass(object,child_list,root)
            if inspect.isroutine(object): return self.docroutine(object,child_list,root)
        except AttributeError:
            self.fail(object)

    def fail(self, object):
        """Raise an exception for unimplemented types."""
        message = "don't know how to document object%s of type %s" % (
            object.__name__, type(object).__name__)
        raise TypeError(message)


    def docmodule(self, object, child_list, root):
        module_info = _getdata(object)
        module_info['type'] = 'module'
        module_info['href'] = root+'/'+module_info['NAME']
        module_info['path'] = self.pkgname+module_info['href'].replace('/','.')

        module_info['children']=[]
        #if its a class or a function document them too (maybe add more stuff here in future)
        for key, value in inspect.getmembers(object, _isclass) or inspect.getmembers(object, inspect.isroutine):
            self.document(value, module_info['children'], module_info['href'])

        child_list.append(module_info)


    def docclass(self, object, child_list, root):
        class_info = _getdata(object)
        class_info['type'] = 'class'
        class_info['href'] = root + '/' + class_info['NAME']
        class_info['path'] = self.pkgname+class_info['href'].replace('/','.')
        if not self.separate_classes:
            class_info['href'] = root + '/'+'classes'

        class_info['METHODS'] = []
        #get methods of class:
        for name, method in inspect.getmembers(object, inspect.isfunction): 
            #don't add hidden methods
            if name.startswith('_'):
                continue
            class_info['METHODS'].append(_getdata(method))
        child_list.append(class_info)

    def docroutine(self,object,child_list,root):
        routine_info = _getdata(object)
        routine_info['type'] = 'function'
        routine_info['href'] = root + '/' + routine_info['NAME']
        routine_info['path'] = self.pkgname+routine_info['href'].replace('/','.')
        if not self.separate_functions:
            routine_info['href'] = root + '/'+'routines'
        child_list.append(routine_info)



if __name__ == "__main__":
    scribe = Scribe().transcribe('example_dir','deScribe/src/data/transcription.json')

