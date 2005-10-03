# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#
#
# Authors:  Eray Ozkural <eray@uludag.org.tr>
#           Gurer Ozen <gurer@uludag.org.tr>
#           Baris Metin <baris@uludag.org.tr>


"""
 xmlfile is a helper module for accessing XML files using
 xml.dom.minidom.

 XmlFile class further abstracts a dom object using the
 high-level dom functions provided in xmlext module (and sorely lacking
 in xml.dom :( )

 autoxml is a metaclass for automatic XML translation, using
 a miniature type system. (w00t!) This is based on an excellent
 high-level XML processing prototype that Gurer prepared.

 Method names are mixedCase for compatibility with minidom,
 an old library. 
"""

# System
import xml.dom.minidom as mdom
from xml.parsers.expat import ExpatError
import codecs
import types

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

# PiSi
import pisi
from pisi.xmlext import *
import pisi.context as ctx


class Error(pisi.Error):
    pass

mandatory, optional = range(2) # poor man's enum

# basic types

Text = types.StringType
Integer = types.IntType

#class datatype(type):
#    def __init__(cls, name, bases, dict):
#        """entry point for metaclass code"""
#        # standard initialization
#        super(autoxml, cls).__init__(name, bases, dict)

class LocalText(object):
    """Handles XML tags with localized text"""

    def __init__(self, tag, spec):
        self.tag = tag
        self.req = spec[1]
        self.locs = {}
    
    def decode(self, node, errs):
        # flags, tag name, instance attribute
        nodes = getAllNodes(node, self.tag)
        if not nodes:
            if self.req == mandatory:
                errs.append(_("LocalText '%s' should have at least one '%s' tag\n") %
                             self.tag)
        else:
            for node in nodes:
                lang = getNodeAttribute(node, "xml:lang")
                c = getNodeText(node)
                if not c:
                    errs.append(_("'%s' language of tag '%s' should have some text data\n") %
                                (lang, self.tag))
                # FIXME: check for dups and 'en'
                if not lang:
                    lang = 'en'
                self.locs[lang] = c
            
    def encode(self, xml, node, errs):
        for key in self.locs.iterkeys():
            newnode = newNode(node, self.tag)
            newnode.setAttribute('xml:lang', key)     
            newtext = newTextNode(node, self.locs[key])
            newnode.appendChild(newtext)
            node.appendChild(newnode)
    
    def format(self, errs):
        return ''

    # FIXME: use something like the below to return a default
    #L = language
    #if not self.locs.has_key(L):
    #    L = 'en'
    #if not self.locs.has_key(L):
    #    #errs.append("Tag '%s' should have an English version\n" % d[2])
    #    return ""
    #retur
            
class autoxml(type):
    """High-level automatic XML transformation interface for xmlfile.
    The idea is to declare a class for each XML tag. Inside the
    class the tags and attributes nested in the tag are further
    elaborated. A simple example follows:

    class Employee:
         __metaclass__ = autoxml
         t_Name = [xmlfile.Text, xmlfile.mandatory]
         a_Type = [xmlfile.Integer, xmlfile.optional]
    
    This class defines a tag and an attribute nested in Employee 
    class. Name is a string and type is an integer, called basic
    types.
    While the tag is mandatory, the attribute may be left out.
    
    Other basic types supported are: xmlfile.Float, xmlfile.Double
    and (not implemented yet): xmlfile.Binary

    By default, the class name is taken as the corresponding tag,
    which may be overridden by defining a tag attribute. Thus, 
    the same tag may also be written as:

    class EmployeeXML:
        ...
        tag = 'Employee'
        ...

    In addition to basic types, we allow for two kinds of complex
    types: class types and list types.

    A declared class can be nested in another class as follows

    class Position:
         __metaclass__ = autoxml
         t_Name = [xmlfile.Text, xmlfile.mandatory]
         t_Description = [xmlfile.Text, xmlfile.optional]

    which we can add to our Employee class.

    class Employee:
         __metaclass__ = autoxml
         t_Name = [xmlfile.Text, xmlfile.mandatory]
         a_Type = [xmlfile.Integer, xmlfile.optional]
         t_Position = [Position, xmlfile.mandatory]

    Note some unfortunate redundancy here with Position; this is
    justified by the implementation (kidding). Still, you might
    want to assign a different name than the class name that
    goes in there, which may be fully qualified.

    There is more! Suppose we want to define a company, with
    of course many employees.

    class Company:
        __metaclass__ = autoxml
        t_Employees = [ [Employee], xmlfile.mandatory, 'Employee']

    Logically, inside the Company/Employees tag, we will have several
    Employes tags, which are inserted to the Employees instance variable of
    Company in order of appearance.

    The mandatory flag here asserts that at least one such record
    is to be found.

    You see, it works like magic, when it works of course. All of it
    done without a single brain exploding.
        
    """

    def __init__(cls, name, bases, dict):
        """entry point for metaclass code"""
        #print 'generating class', name

        # add XmlFile as one of the superclasses, we're smart
        bases = list(bases)
        if not XmlFile in bases:
            bases.append(XmlFile)

        # standard initialization
        super(autoxml, cls).__init__(name, bases, dict)

        #TODO: initialize class attribute __xml_tags
        #setattr(cls, 'xml_variables', [])

        # default class tag is class name
        if not dict.has_key('tag'): 
            cls.tag = name

        # generate helper routines, for each XML component
        inits = []
        decoders = []
        encoders = []
        formatters = []
        for var in dict:
            if var.startswith('t_') or var.startswith('a_'):
                name = var[2:]
                if var.startswith('a_'):
                    x = autoxml.gen_attr_member(cls, name)
                elif var.startswith('t_'):
                    x = autoxml.gen_tag_member(cls, name)
                (init, decoder, encoder, formatter) = x
                inits.append(init)
                decoders.append(decoder)
                encoders.append(encoder)
                formatters.append(formatter)

        # generate top-level helper functions
        cls.initializers = inits
        def initialize(self, tag = None, spec = None):
#            XmlFile.__init__(self, cls.tag)
            for init in self.__class__.initializers:
                init(self)
        cls.__init__ = initialize

        cls.decoders = decoders
        def decode(self, node, errs):
            for decode_member in self.__class__.decoders:
                decode_member(self, node, errs)
        cls.decode = decode

        cls.encoders = encoders
        def encode(self, xml, node, errs):
            for encode_member in self.__class__.encoders:
                encode_member(self, xml, node, errs)
        cls.encode = encode

        cls.formatters = formatters
        def format(self, errs):
            string = ''
            for formatter in self.__class__.formatters:
                string += formatter(self, errs)
            return string
        cls.format = format
        if not dict.has_key('__str__'):
            cls.__str__ = format

    def gen_attr_member(cls, attr):
        """generate readers and writers for an attribute member"""
        #print 'attr:', attr
        spec = getattr(cls, 'a_' + attr)
        tag_type = spec[0]
        assert type(tag_type) == type(type)
        def readtext(node, attr):
            return getNodeAttribute(node, attr)
        def writetext(xml, node, attr, text):
            #print 'write attr', attr, text
            node.setAttribute(attr, text)
        anonfuns = cls.gen_anon_basic(attr, spec, readtext, writetext)
        return cls.gen_named_comp(attr, spec, anonfuns)

    def gen_tag_member(cls, tag):
        """generate helper funs for tag member of class"""
        #print 'tag:', tag
        spec = getattr(cls, 't_' + tag)
        anonfuns = cls.gen_tag(tag, spec)
        return cls.gen_named_comp(tag, spec, anonfuns)
                    
    def gen_tag(cls, tag, spec):
        """generate readers and writers for the tag"""
        tag_type = spec[0]
        if type(tag_type) is types.TypeType and \
           autoxml.basic_cons_map.has_key(tag_type):
            def readtext(node, tagpath):
                #print 'read tag', node, tagpath
                return getNodeText(node, tagpath)
            def writetext(xml, node, tagpath, text):
                #print 'write tag', node, tagpath, text
                xml.addTextNodeUnder(node, tagpath, text)
            return cls.gen_anon_basic(tag, spec, readtext, writetext)
        elif type(tag_type) is types.ListType:
            return cls.gen_list_tag(tag, spec)
        elif tag_type is LocalText:
            return cls.gen_insetclass_tag(tag, spec)
        elif type(tag_type) is autoxml or type(tag_type) is types.TypeType:
            return cls.gen_class_tag(tag, spec)
        else:
            raise Error(_('gen_tag: unrecognized tag type %s in spec') %
                        str(tag_type))

    def gen_named_comp(cls, token, spec, anonfuns):
        """generate a named component tag/attr. a decoration of
        anonymous functions that do not bind to variable names"""
        name = cls.mixed_case(token)
        token_type = spec[0]
        req = spec[1]
        (init_a, decode_a, encode_a, format_a) = anonfuns

        def init(self):
            """initialize component"""
            setattr(self, name, init_a())
            
        def decode(self, node, errs):
            """decode component from DOM node"""
            setattr(self, name, decode_a(node, errs))
            
        def encode(self, xml, node, errs):
            """encode self inside, possibly new, DOM node using xml"""
            if hasattr(self, name):
                value = getattr(self, name)
            else:
                value = None
            encode_a(xml, node, value, errs)
            
        def format(self, errs):
            if hasattr(self, name):
                value = getattr(self,name)
                return '%s: %s\n' % (token, format_a(value, errs))
            else:
                if req == mandatory:
                    raise Error(_('Mandatory variable %s not available') % name)
            return ''
            
        return (init, decode, encode, format)

    def mixed_case(cls, identifier):
        """helper function to turn token name into mixed case"""
        if identifier is "":
            return ""
        else:
            return identifier[0].lower() + identifier[1:]

    def tagpath_head_last(cls, tagpath):
        "returns split of the tag path into last tag and the rest"
        try:
            lastsep = tagpath.rindex('/')
        except ValueError, e:
            return ('', tagpath)
        return (tagpath[:lastsep], tagpath[lastsep+1:])

    def parse_spec(cls, token, spec):
        """decompose member specification"""
        name = cls.mixed_case(token)
        token_type = spec[0]
        req = spec[1]

        if len(spec)>=3:
            path = spec[2]               # an alternative path specified
        else:
            path = token                 # otherwise it's the same name as
                                         # the token
        return name, token_type, req, path

    def gen_anon_basic(cls, token, spec, readtext, writetext):
        """Generate a tag or attribute with one of the basic
        types like integer. This has got to be pretty generic
        so that we can invoke it from the complex types such as Class
        and List. The readtext and writetext arguments achieve
        the DOM text access for this datatype."""
        
        name, token_type, req, tagpath = cls.parse_spec(token, spec)
       
        def initialize():
            """default value for all basic types is None"""
            return None

        def decode(node, errs):
            """decode from DOM node, the value, watching the spec"""
            text = readtext(node, token)
            #print 'read text ', text
            if text:
                try:
                    value = autoxml.basic_cons_map[token_type](text)
                except Error:
                    value = None
                    errs.append(_('Type mismatch: read text cannot be decoded'))
                return value
            else:
                if req == mandatory:
                    errs.append(_('Mandatory token %s not available') % token)
                return None

        def encode(xml, node, value, errs):
            """encode given value inside DOM node"""
            if value:
                writetext(xml, node, token, str(value))
            else:
                if req == mandatory:
                    errs.append(_('Mandatory argument not available'))

        def format(value, errs):
            """format value for pretty printing"""
            return str(value)

        return initialize, decode, encode, format

    def gen_class_tag(cls, tag, spec):
        """generate a class datatype"""
        name, tag_type, req, path = cls.parse_spec(tag, spec)

        def make_object():
            obj = tag_type.__new__(tag_type)
            obj.__init__(tag, spec)
            return obj

        def init():
            return make_object()

        def decode(node, errs):
            node = getNode(node, tag)
            if node:
                try:
                    obj = make_object()
                    obj.decode(node, errs)
                    return obj
                except Error:
                    errs.append(_('Type mismatch: DOM cannot be decoded'))
            else:
                if req == mandatory:
                    errs.append(_('Mandatory argument not available'))
            return None
        
        def encode(xml, node, obj, errs):
            if node and obj:
                try:
                    #FIXME: this doesn't look pretty
                    classnode = node.ownerDocument.createElement(tag)
                    obj.encode(xml, classnode, errs)
                    node.appendChild(classnode)
                except Error:
                    if req == mandatory:
                        # note: we can receive an error if obj has no content
                        errs.append(_('Object cannot be encoded'))
            else:
                if req == mandatory:
                    errs.append(_('Mandatory argument not available'))
                
        def format(obj, errs):
            try:
                return obj.format(errs)
            except Error:
                if req == mandatory:
                    errs.append(_('Mandatory argument not available'))
                else:
                    return ''
        return (init, decode, encode, format)

    def gen_list_tag(cls, tag, spec):
        """generate a list datatype. stores comps in tag/comp_tag"""
        name, tag_type, req, comp_tag = cls.parse_spec(tag, spec)
        #head, last = cls.tagpath_head_last(path)

        if len(tag_type) != 1:
            raise Error(_('List type must contain only one element'))

        x = cls.gen_tag(comp_tag, [tag_type[0], mandatory])
        (init_item, decode_item, encode_item, format_item) = x

        def init():
            return []

        def decode(node, errs):
            l = []
            nodes = getAllNodes(node, tag + '/' + comp_tag)
            #print node, tag + '/' + comp_tag, nodes
            if len(nodes) is 0 and req is mandatory:
                errs.append(_('Mandatory list empty'))
            for node in nodes:
                dummy = node.ownerDocument.createElement("Dummy")
                dummy.appendChild(node)
                l.append(decode_item(dummy, errs))
            return l

        def encode(xml, node, l, errs):
            if l and len(l) > 0:
                listnode = xml.newNode(tag)
                for item in l:
                    encode_item(xml, listnode, item, errs)
                node.appendChild(listnode)
            else:
                if req is mandatory:
                    errs.append(_('Mandatory list empty'))

        def format(l, errs):
            #print 'format:', name
            s = ''
            for ix in range(len(l)):
                s += str(ix+1) + ': ' + format_item(l[ix], errs)
                if ix != len(l)-1:
                    s += ', '
            return s
        
        return (init, decode, encode, format)

    def gen_insetclass_tag(cls, tag, spec):
        """generate a class datatype that is highly integrated
           don't worry if that means nothing to you. this is a silly
           hack to implement local text quickly. it's not the most 
           elegant thing in the world. it's basically a copy of 
           class tag"""
        name, tag_type, req, path = cls.parse_spec(tag, spec)

        def make_object():
            obj = tag_type.__new__(tag_type)
            obj.__init__(tag, spec)
            return obj

        def init():
            return make_object()

        def decode(node, errs):
            if node:
                try:
                    obj = make_object()
                    obj.decode(node, errs)
                    return obj
                except Error:
                    errs.append(_('Type mismatch: DOM cannot be decoded'))
            else:
                if req == mandatory:
                    errs.append(_('Mandatory argument not available'))
            return None

        def encode(xml, node, obj, errs):
            if node and obj:
                try:
                    #FIXME: this doesn't look pretty
                    obj.encode(xml, node, errs)
                except Error:
                    if req == mandatory:
                        # note: we can receive an error if obj has no content
                        errs.append(_('Object cannot be encoded'))
            else:
                if req == mandatory:
                    errs.append(_('Mandatory argument not available'))
                
        def format(obj, errs):
            try:
                return obj.format(errs)
            except Error:
                if req == mandatory:
                    errs.append(_('Mandatory argument not available'))
                else:
                    return ''
        return (init, decode, encode, format)

    basic_cons_map = {
        types.StringType : str,
        types.IntType : int
        }


class XmlFile(object):
    """A class to help reading and writing an XML file"""

    def __init__(self, rootTag):
        self.rootTag = rootTag
        self.newDOM()

    def newDOM(self):
        """clear DOM"""
        impl = mdom.getDOMImplementation()
        self.dom = impl.createDocument(None, self.rootTag, None)

    def unlink(self):
        """deallocate DOM structure"""
        self.dom.unlink()

    def rootNode(self):
        """returns root document element"""
        return self.dom.documentElement

    def readxml(self, fileName):
        try:
            self.dom = mdom.parse(fileName)
        except ExpatError, inst:
            raise Error(_("File '%s' has invalid XML: %s\n") % (fileName,
                                                                str(inst)))

    def writexml(self, fileName):
        f = codecs.open(fileName,'w', "utf-8")
        f.write(self.dom.toprettyxml())
        f.close()

    def verifyRootTag(self):
        actual_roottag = self.rootNode().tagName
        if actual_roottag != self.rootTag:
            raise Error(_("Root tagname %s not identical to %s as expected") %
                        (actual_roottag, self.rootTag) )

    # construction helpers

    def newNode(self, tag):
        return self.dom.createElement(tag)

    def newTextNode(self, text):
        return self.dom.createTextNode(text)

    def newAttribute(self, attr):
        return self.dom.createAttribute(attr)

    # read helpers

    def getNode(self, tagPath = ""):
        """returns the *first* matching node for given tag path."""
        self.verifyRootTag()
        return getNode(self.dom.documentElement, tagPath)

    def getNodeText(self, tagPath):
        """returns the text of *first* matching node for given tag path."""
        node = self.getNode(tagPath)
        if not node:
            return None
        return getNodeText(node)

    def getAllNodes(self, tagPath):
        """returns all nodes matching a given tag path."""
        self.verifyRootTag()
        return getAllNodes(self.dom.documentElement, tagPath)

    def getChildren(self, tagpath):
        """ returns the children of the given path"""
        node = self.getNode(tagpath)
        return node.childNodes

    # get only elements of a given type
    #FIXME:  this doesn't work
    def getChildrenWithType(self, tagpath, type):
        """ returns the children of the given path, only with given type """
        node = self.getNode(tagpath)
        return filter(lambda x:x.nodeType == type, node.childNodes)

    # get only child elements
    def getChildElts(self, tagpath):
        """ returns the children of the given path, only with given type """
        node = self.getNode(tagpath)
        try:
            return filter(lambda x:x.nodeType == x.ELEMENT_NODE,
                          node.childNodes)
        except AttributeError:
            return None

    # write helpers

    def addNode(self, tagPath, newnode = None):
        "this adds the newnode under given tag path"
        self.verifyRootTag()
        return addNode(self.dom, self.dom.documentElement, tagPath,
                       newnode)

    def addNodeUnder(self, node, tagPath, newnode = None):
        "this adds the new stuff under node and then following tag path"
        self.verifyRootTag()
        return addNode(self.dom, node, tagPath, newnode)

    def addChild(self, newnode):
        "add a new child node right under root element document"
        self.dom.documentElement.appendChild(newnode)

    def addText(self, node, text):
        "add text to node"
        node.appendChild(self.newTextNode(text))

    def addTextNode(self, tagPath, text):
        "add a text node with given tag path"
        node = self.addNode(tagPath, self.newTextNode(text))
        return node

    def addTextNodeUnder(self, node, tagPath, text):
        "add a text node under given node with tag path (phew)"
        return self.addNodeUnder(node, tagPath, self.newTextNode(text))
