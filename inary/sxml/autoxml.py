# -*- coding: utf-8 -*-
#
# Main fork Pisi: Copyright (C) 2005 - 2011, Tubitak/UEKAE
#
# Copyright (C) 2016 - 2020, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

"""
 autoxml is a metaclass for automatic XML translation, using
 a miniature type system. (w00t!) This is based on an excellent
 high-level XML processing prototype that Gurer prepared.

 Method names are mixedCase for compatibility with minidom,
 an old library.
"""

# Standart Python Libraries
import io
import re
import sys
import locale
import inspect
import formatter

# Standart Python Libraries
import inary.errors
import inary.util as util
import inary.context as ctx
import inary.sxml.xmlfile as xmlfile
import inary.sxml.xmlext as xmlext
import inary.sxml.oo as oo

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

# INARY


class Error(inary.errors.Error):
    pass


# requirement specs

mandatory, optional = list(range(2))  # poor man's enum

# basic types

String = str
Text = bytes
Integer = int
Long = int
Float = float


class datatype(type):
    def __init__(cls, name, bases, dict):
        """entry point for metaclass code"""
        # standard initialization
        super(autoxml, cls).__init__(name, bases, dict)


class LocalText(dict):
    """Handles XML tags with localized text"""

    def __init__(self, tag="", req=optional):
        self.tag = tag
        self.req = req
        dict.__init__(self)

    def decode(self, node, errs, where=""):
        # flags, tag name, instance attribute
        assert self.tag != ''
        nodes = xmlext.getAllNodes(node, self.tag)
        if not nodes:
            if self.req == mandatory:
                errs.append(
                    where + ': ' + _("At least one '{}' tag should have local text.").format(self.tag))
        else:
            for node in nodes:
                lang = xmlext.getNodeAttribute(node, 'xml:lang')
                c = xmlext.getNodeText(node)
                if not c:
                    errs.append(
                        where + ': ' + _("'{0}' language of tag '{1}' is empty.").format(lang, self.tag))
                # FIXME: check for dups and 'en'
                if not lang:
                    lang = 'en'
                self[lang] = str(c)

    def encode(self, node, errs):
        assert self.tag != ''
        for key in list(self.keys()):
            newnode = xmlext.addNode(node, self.tag)
            xmlext.setNodeAttribute(newnode, 'xml:lang', key)
            xmlext.addText(newnode, '', self[key])

    # FIXME: maybe more appropriate for inary.util
    @staticmethod
    def get_lang():
        try:
            (lang, encoding) = locale.getlocale()
            if not lang:
                (lang, encoding) = locale.getdefaultlocale()
            if lang is None:  # stupid python means it is C locale
                return 'en'
            else:
                return lang[0:2]
        except KeyboardInterrupt:
            raise
        except Exception:  # FIXME: what exception could we catch here, replace with that.
            raise Error(
                _('LocalText: unable to get either current or default locale.'))

    def errors(self, where=str()):
        errs = []
        langs = [LocalText.get_lang(), 'en', 'tr', ]
        if list(self.keys()) and not util.any(lambda x: x in self, langs):
            errs.append(where + ': ' + _(
                "Tag should have at least the current locale, or failing that an English or Turkish version."))
        # FIXME: check if all entries are unicode
        return errs

    def format(self, f, errs):
        L = LocalText.get_lang()
        if L in self:
            f.add_flowing_data(self[L])
        elif 'en' in self:
            # fallback to English, blah
            f.add_flowing_data(self['en'])
        elif 'tr' in self:
            # fallback to Turkish
            f.add_flowing_data(self['tr'])
        else:
            errs.append(
                _("Tag should have at least the current locale, or failing that an English or Turkish version."))

    # FIXME: factor out these common routines
    def print_text(self, file=sys.stdout):
        w = Writer(file)  # plain text
        f = formatter.AbstractFormatter(w)
        errs = []
        self.format(f, errs)
        if errs:
            for x in errs:
                ctx.ui.warning(x)

    def __str__(self):
        L = LocalText.get_lang()
        if L in self:
            return str(self[L])
        elif 'en' in self:
            # fallback to English, blah
            return str(self['en'])
        elif 'tr' in self:
            # fallback to Turkish
            return str(self['tr'])
        else:
            return str()


class Writer(formatter.DumbWriter):
    """adds unicode support"""

    def __init__(self, file=None, maxcol=78):
        formatter.DumbWriter.__init__(self, file, maxcol)

    def send_literal_data(self, data):
        self.file.write(data.encode("utf-8"))
        i = data.rfind('\n')
        if i >= 0:
            self.col = 0
            data = data[i + 1:]
        data = data.expandtabs()
        self.col += len(data)
        self.atbreak = 0


class autoxml(oo.autosuper, oo.autoprop):
    """High-level automatic XML transformation interface for xmlfile.
    The idea is to declare a class for each XML tag. Inside the
    class the tags and attributes nested in the tag are further
    elaborated. A simple example follows:

    class Employee(metaclass=autoxml):
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

    class Position(metaclass=autoxml):
         t_Name = [xmlfile.Text, xmlfile.mandatory]
         t_Description = [xmlfile.Text, xmlfile.optional]

    which we can add to our Employee class.

    class Employee(metaclass=autoxml):
         t_Name = [xmlfile.Text, xmlfile.mandatory]
         a_Type = [xmlfile.Integer, xmlfile.optional]
         t_Position = [Position, xmlfile.mandatory]

    Note some unfortunate redundancy here with Position; this is
    justified by the implementation (kidding). Still, you might
    want to assign a different name than the class name that
    goes in there, which may be fully qualified.

    There is more! Suppose we want to define a company, with
    of course many employees.

    class Company(metaclass=autoxml):
        t_Employees = [ [Employee], xmlfile.mandatory, 'Employees/Employee']

    Logically, inside the Company/Employees tag, we will have several
    Employee tags, which are inserted to the Employees instance variable of
    Company in order of appearance. We can define lists of any other valid
    type. Here we used a list of an autoxml class defined above.

    The mandatory flag here asserts that at least one such record
    is to be found.

    You see, it works like magic, when it works of course. All of it
    done without a single brain exploding.

    """

    def __init__(cls, name, bases, dict):
        """entry point for metaclass code"""
        # print 'generating class', name

        # standard initialization
        super().__init__(name, bases, dict)

        xmlfile_support = xmlfile.XmlFile in bases

        cls.autoxml_bases = [
            base for base in bases if isinstance(
                base, autoxml)]

        # TODO: initialize class attribute __xml_tags
        # setattr(cls, 'xml_variables', [])

        # default class tag is class name
        if 'tag' not in dict:
            cls.tag = name

        # generate helper routines, for each XML component
        names = []
        inits = []
        decoders = []
        encoders = []
        errorss = []
        formatters = []

        # FIXME: What is this? Remove this crap and try to fix autoxml, if can not be fixed then
        # really throw whole autoxml to junk. But not this.

        # read declaration order from source
        # code contributed by bahadir kandemir
        try:
            fn = re.compile(r'\s*([tas]_[a-zA-Z]+).*').findall

            inspect.linecache.clearcache()
            lines = list(filter(fn, inspect.getsourcelines(cls)[0]))
            decl_order = [x.split()[0] for x in lines]
        except IOError:
            decl_order = list(dict.keys())

        # there should be at most one str member, and it should be
        # the first to process

        order = [x for x in decl_order if not x.startswith('s_')]

        # find string member
        str_members = [x for x in decl_order if x.startswith('s_')]
        if len(str_members) > 1:
            raise Error('Only one str member can be defined')
        elif len(str_members) == 1:
            order.insert(0, str_members[0])

        for var in order:
            if var.startswith('t_') or var.startswith(
                    'a_') or var.startswith('s_'):
                name = var[2:]
                if var.startswith('a_'):
                    x = autoxml.gen_attr_member(cls, name)
                elif var.startswith('t_'):
                    x = autoxml.gen_tag_member(cls, name)
                elif var.startswith('s_'):
                    x = autoxml.gen_str_member(cls, name)
                (name, init, decoder, encoder, errors, format_x) = x
                names.append(name)
                inits.append(init)
                decoders.append(decoder)
                encoders.append(encoder)
                errorss.append(errors)
                formatters.append(format_x)

        # generate top-level helper functions
        cls.initializers = inits

        def initialize(self, uri=None, keepDoc=False, tmpDir='/tmp',
                       **args):
            if xmlfile_support:
                if 'tag' in args:
                    xmlfile.XmlFile.__init__(self, tag=args['tag'])
                else:
                    xmlfile.XmlFile.__init__(self, tag=cls.tag)
            for base in cls.autoxml_bases:
                base.__init__(self)
            for init in inits:
                init(self)
            for x in list(args.keys()):
                setattr(self, x, args[x])
            # init hook
            if hasattr(self, 'init'):
                self.init()
            if xmlfile_support and uri:
                self.read(uri, keepDoc, tmpDir)

        cls.__init__ = initialize

        cls.decoders = decoders

        def decode(self, node, errs, where=String(cls.tag)):
            for base in cls.autoxml_bases:
                base.decode(self, node, errs, where)
            for decode_member in decoders:  # self.__class__.decoders:
                decode_member(self, node, errs, where)
            if hasattr(self, 'decode_hook'):
                self.decode_hook(node, errs, where)

        cls.decode = decode

        cls.encoders = encoders

        def encode(self, node, errs):
            for base in cls.autoxml_bases:
                base.encode(self, node, errs)
            for encode_member in encoders:  # self.__class__.encoders:
                encode_member(self, node, errs)
            if hasattr(self, 'encode_hook'):
                self.encode_hook(node, errs)

        cls.encode = encode

        cls.errorss = errorss

        def errors(self, where=String(name)):
            errs = []
            for base in cls.autoxml_bases:
                errs.extend(base.errors(self, where))
            for errors in errorss:  # self.__class__.errorss:
                errs.extend(errors(self, where))
            if hasattr(self, 'errors_hook'):
                errs.extend(self.errors_hook(where))
            return errs

        cls.errors = errors

        def check(self):
            errs = self.errors()
            if errs:
                errs.append(_("autoxml.check: '{}' errors.").format(len(errs)))
                raise Error(*errs)

        cls.check = check

        cls.formatters = formatters

        def format(self, f, errs):
            for base in cls.autoxml_bases:
                base.format(self, f, errs)
            for formatter in formatters:  # self.__class__.formatters:
                formatter(self, f, errs)

        cls.format = format

        def print_text(self, file=sys.stdout):
            w = Writer(file)  # plain text
            f = formatter.AbstractFormatter(w)
            errs = []
            self.format(f, errs)
            if errs:
                for x in errs:
                    ctx.ui.warning(x)

        cls.print_text = print_text
        if '__str__' not in dict:
            def str(self):
                strfile = io.StringIO()
                self.print_text(strfile)
                str = strfile.getvalue()
                strfile.close()
                return str

            cls.__str__ = str

        if '__eq__' not in dict:
            def equal(self, other):
                # handle None
                if other is None:
                    return False  # well, must be False at this point :)
                for name in names:
                    try:
                        if getattr(self, name) != getattr(other, name):
                            return False
                    except KeyboardInterrupt:
                        raise
                    except Exception:  # FIXME: what exception could we catch here, replace with that.
                        return False
                return True

            def notequal(self, other):
                return not self.__eq__(other)

            cls.__eq__ = equal
            cls.__ne__ = notequal

        if xmlfile_support:
            def parse(self, xml, keepDoc=False):
                """parse XML string and decode it into a python object"""
                self.parsexml(xml)
                errs = []
                self.decode(self.rootNode(), errs)
                if errs:
                    errs.append(
                        _("autoxml.parse: String '{}' has errors.").format(xml))
                    raise Error(*errs)
                if hasattr(self, 'read_hook'):
                    self.read_hook(errs)

                if not keepDoc:
                    self.unlink()  # get rid of the tree

                errs = self.errors()
                if errs:
                    errs.append(
                        _("autoxml.parse: String '{}' has errors.").format(xml))

            def read(self, uri, keepDoc=False, tmpDir='/tmp',
                     sha1sum=False, compress=None, sign=None, copylocal=False, nodecode=False):
                """read XML file and decode it into a python object"""
                read_xml = self.readxml(uri, tmpDir, sha1sum=sha1sum,
                                        compress=compress, sign=sign, copylocal=copylocal)

                if nodecode:
                    return read_xml

                errs = []
                self.decode(self.rootNode(), errs)
                if errs:
                    errs.append(
                        _("autoxml.read: File '{}' has errors.").format(uri))
                    raise Error(*errs)
                if hasattr(self, 'read_hook'):
                    self.read_hook(errs)

                if not keepDoc:
                    self.unlink()  # get rid of the tree

                errs = self.errors()
                if errs:
                    errs.append(
                        _("autoxml.read: File '{}' has errors.").format(uri))
                    raise Error(*errs)

            def write(self, uri, keepDoc=False, tmpDir='/tmp',
                      sha1sum=False, compress=None, sign=None):
                """encode the contents of the python object into an XML file"""
                errs = self.errors()
                if errs:
                    errs.append(
                        _("autoxml.write: object validation has failed."))
                    raise Error(*errs)
                errs = []
                self.newDocument()
                self.encode(self.rootNode(), errs)
                if hasattr(self, 'write_hook'):
                    self.write_hook(errs)
                if errs:
                    errs.append(
                        _("autoxml.write: File encoding '{}' has errors.").format(uri))
                    raise Error(*errs)
                self.writexml(
                    uri,
                    tmpDir,
                    sha1sum=sha1sum,
                    compress=compress,
                    sign=sign)
                if not keepDoc:
                    self.unlink()  # get rid of the tree

            cls.read = read
            cls.write = write
            cls.parse = parse

    def gen_attr_member(cls, attr):
        """generate readers and writers for an attribute member"""
        # print 'attr:', attr
        spec = getattr(cls, 'a_' + attr)
        tag_type = spec[0]
        assert isinstance(tag_type, type(type))

        def readtext(node, attr):
            return xmlext.getNodeAttribute(node, attr)

        def writetext(node, attr, text):
            # print 'write attr', attr, text
            xmlext.setNodeAttribute(node, attr, text)

        anonfuns = cls.gen_anon_basic(attr, spec, readtext, writetext)
        return cls.gen_named_comp(attr, spec, anonfuns)

    def gen_tag_member(cls, tag):
        """generate helper funs for tag member of class"""
        # print 'tag:', tag
        spec = getattr(cls, 't_' + tag)
        anonfuns = cls.gen_tag(tag, spec)
        return cls.gen_named_comp(tag, spec, anonfuns)

    def gen_tag(cls, tag, spec):
        """generate readers and writers for the tag"""
        tag_type = spec[0]
        if isinstance(tag_type, type) and \
                tag_type in autoxml.basic_cons_map:
            def readtext(node, tagpath):
                # print 'read tag', node, tagpath
                return xmlext.getNodeText(node, tagpath)

            def writetext(node, tagpath, text):
                # print 'write tag', node, tagpath, text
                xmlext.addText(node, tagpath, text)

            return cls.gen_anon_basic(tag, spec, readtext, writetext)
        elif isinstance(tag_type, list):
            return cls.gen_list_tag(tag, spec)
        elif tag_type is LocalText:
            return cls.gen_insetclass_tag(tag, spec)
        elif isinstance(tag_type, autoxml) or isinstance(tag_type, type):
            return cls.gen_class_tag(tag, spec)
        else:
            raise Error(
                _('gen_tag: unrecognized tag type {} in spec.').format(
                    str(tag_type)))

    def gen_str_member(cls, token):
        """generate readers and writers for a string member"""
        spec = getattr(cls, 's_' + token)
        tag_type = spec[0]
        assert isinstance(tag_type, type(type))

        def readtext(node, blah):
            try:
                node.normalize()  # iksemel doesn't have this
            except BaseException:
                pass
            return xmlext.getNodeText(node)

        def writetext(node, blah, text):
            xmlext.addText(node, "", text)

        anonfuns = cls.gen_anon_basic(token, spec, readtext, writetext)
        return cls.gen_named_comp(token, spec, anonfuns)

    def gen_named_comp(cls, token, spec, anonfuns):
        """generate a named component tag/attr. a decoration of
        anonymous functions that do not bind to variable names"""
        name = cls.mixed_case(token)
        req = spec[1]
        (init_a, decode_a, encode_a, errors_a, format_a) = anonfuns

        def init(self):
            """initialize component"""
            setattr(self, name, init_a())

        def decode(self, node, errs, where):
            """decode component from DOM node"""
            setattr(self, name, decode_a(node, errs, where + '.' + str(name)))

        def encode(self, node, errs):
            """encode self inside, possibly new, DOM node using xml"""
            if hasattr(self, name):
                value = getattr(self, name)
            else:
                value = None
            encode_a(node, value, errs)

        def errors(self, where):
            """return errors in the object"""
            errs = []
            if hasattr(self, name) and getattr(self, name):
                value = getattr(self, name)
                errs.extend(errors_a(value, where + '.' + name))
            else:
                if req == mandatory:
                    errs.append(
                        where + ': ' + _('Mandatory variable {} not available.').format(name))
            return errs

        def format(self, f, errs):
            if hasattr(self, name):
                value = getattr(self, name)
                f.add_literal_data(token + ': ')
                format_a(value, f, errs)
                f.add_line_break()
            else:
                if req == mandatory:
                    errs.append(
                        _('Mandatory variable {} not available.').format(name))

        return name, init, decode, encode, errors, format

    @staticmethod
    def mixed_case(identifier):
        """helper function to turn token name into mixed case"""
        if identifier == "":
            return ""
        else:
            if identifier[0] == 'I':
                lowly = 'i'  # because of pythonic idiots we can't choose locale in lower
            else:
                lowly = identifier[0].lower()
            return lowly + identifier[1:]

    @staticmethod
    def tagpath_head_last(tagpath):
        """returns split of the tag path into last tag and the rest"""
        try:
            lastsep = tagpath.rindex('/')
        except ValueError:
            return '', tagpath
        return tagpath[:lastsep], tagpath[lastsep + 1:]

    def parse_spec(cls, token, spec):
        """decompose member specification"""
        name = cls.mixed_case(token)
        token_type = spec[0]
        req = spec[1]

        if len(spec) >= 3:
            path = spec[2]  # an alternative path specified
        elif isinstance(token_type, type([])):
            if isinstance(token_type[0], autoxml):
                # if list of class, by default nested like in most PSPEC
                path = token + '/' + token_type[0].tag
            else:
                # if list of ordinary type, just take the name for
                path = token
        elif isinstance(token_type, autoxml):
            # if a class, by default its tag
            path = token_type.tag
        else:
            path = token  # otherwise it's the same name as
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

        def decode(node, errs, where):
            """decode from DOM node, the value, watching the spec"""
            text = readtext(node, token)
            # print 'read text ', text
            if text:
                try:
                    value = autoxml.basic_cons_map[token_type](text)
                except KeyboardInterrupt:
                    raise
                except Exception:  # FIXME: what exception could we catch here, replace with that.
                    value = None
                    errs.append(
                        where + ': ' + _('Type mismatch: read text cannot be decoded.'))
                return value
            else:
                if req == mandatory:
                    raise Exception(_('Mandatory token {} not available.').format(
                        token)+"\n  {}".format(where))
                return None

        def encode(node, value, errs):
            """encode given value inside DOM node"""
            if value is not None:
                writetext(node, token, str(value))
            else:
                if req == mandatory:
                    raise Exception(_('Mandatory token {} not available.').format(
                        token)+"\n  {}".format(value))

        def errors(value, where):
            errs = []
            if value and not isinstance(value, token_type):
                errs.append(
                    where + ': ' + _('Type mismatch. Expected {0}, got {1}').format(token_type, type(value)))
            return errs

        def format(value, f, errs):
            """format value for pretty printing"""
            f.add_literal_data(str(value))

        return initialize, decode, encode, errors, format

    def gen_class_tag(cls, tag, spec):
        """generate a class datatype"""
        name, tag_type, req, path = cls.parse_spec(tag, spec)

        def make_object():
            obj = tag_type.__new__(tag_type)
            obj.__init__(tag=tag, req=req)
            return obj

        def init():
            return make_object()

        def decode(node, errs, where):
            node = xmlext.getNode(node, tag)
            if node:
                try:
                    obj = make_object()
                    obj.decode(node, errs, where)
                    return obj
                except Error:
                    errs.append(
                        where + ': ' + _('Type mismatch: DOM cannot be decoded.'))
            else:
                if req == mandatory:
                    errs.append(
                        where + ': ' + _('Mandatory argument not available.'))
            return None

        def encode(node, obj, errs):
            if node and obj:
                try:
                    # FIXME: this doesn't look pretty
                    classnode = xmlext.newNode(node, tag)
                    obj.encode(classnode, errs)
                    xmlext.addNode(node, '', classnode)
                except Error:
                    if req == mandatory:
                        # note: we can receive an error if obj has no content
                        errs.append(_('Object cannot be encoded.'))
            else:
                if req == mandatory:
                    errs.append(_('Mandatory argument not available.'))

        def errors(obj, where):
            return obj.errors(where)

        def format(obj, f, errs):
            if obj:
                try:
                    obj.format(f, errs)
                except Error:
                    if req == mandatory:
                        errs.append(_('Object cannot be formatted.'))
            else:
                if req == mandatory:
                    errs.append(_('Mandatory argument not available.'))

        return init, decode, encode, errors, format

    def gen_list_tag(cls, tag, spec):
        """generate a list datatype. stores comps in tag/comp_tag"""
        name, tag_type, req, path = cls.parse_spec(tag, spec)

        pathcomps = path.split('/')
        comp_tag = pathcomps.pop()
        list_tagpath = util.makepath(pathcomps, sep='/', relative=True)

        if len(tag_type) != 1:
            raise Error(_('List type must contain only one element.'))

        x = cls.gen_tag(comp_tag, [tag_type[0], mandatory])
        (init_item, decode_item, encode_item, errors_item, format_item) = x

        def init():
            return []

        def decode(node, errs, where):
            lst = []
            nodes = xmlext.getAllNodes(node, path)
            # print node, tag + '/' + comp_tag, nodes
            if len(nodes) == 0 and req == mandatory:
                errs.append(
                    where + ': ' + _('Mandatory list "{0}" under "{1}" node is empty.').format(path, node.name()))
            ix = 1
            for node in nodes:
                dummy = xmlext.newNode(node, "Dummy")
                xmlext.addNode(dummy, '', node)
                lst.append(decode_item(
                    dummy, errs, where + str("[{}]".format(ix))))
                ix += 1
            return lst

        def encode(node, lst, errs):
            if lst:
                for item in lst:
                    if list_tagpath:
                        listnode = xmlext.addNode(
                            node, list_tagpath, branch=False)
                    else:
                        listnode = node
                    encode_item(listnode, item, errs)
                    # encode_item(node, item, errs)
            else:
                if req is mandatory:
                    errs.append(
                        _('Mandatory list "{0}" under "{1}" node is empty.').format(
                            path, node.name()))

        def errors(lst, where):
            errs = []
            ix = 1
            for node in lst:
                errs.extend(errors_item(node, where + '[{}]'.format(ix)))
                ix += 1
            return errs

        def format(lst, f, errs):
            lst.sort()
            for node in lst:
                format_item(node, f, errs)
                f.add_literal_data(' ')

        return init, decode, encode, errors, format

    def gen_insetclass_tag(cls, tag, spec):
        """generate a class datatype that is highly integrated
           don't worry if that means nothing to you. this is a silly
           hack to implement local text quickly. it's not the most
           elegant thing in the world. it's basically a copy of
           class tag"""
        name, tag_type, req, path = cls.parse_spec(tag, spec)

        def make_object():
            obj = tag_type.__new__(tag_type)
            obj.__init__(tag=tag, req=req)
            return obj

        def init():
            return make_object()

        def decode(node, errs, where):
            if node:
                try:
                    obj = make_object()
                    obj.decode(node, errs, where)
                    return obj
                except Error:
                    errs.append(
                        where + ': ' + _('Type mismatch: DOM cannot be decoded.'))
            else:
                if req == mandatory:
                    errs.append(
                        where + ': ' + _('Mandatory argument not available.'))
            return None

        def encode(node, obj, errs):
            if node and obj:
                try:
                    # FIXME: this doesn't look pretty
                    obj.encode(node, errs)
                except Error:
                    if req == mandatory:
                        # note: we can receive an error if obj has no content
                        errs.append(_('Object cannot be encoded.'))
            else:
                if req == mandatory:
                    errs.append(_('Mandatory argument not available.'))

        def errors(obj, where):
            return obj.errors(where)

        def format(obj, f, errs):
            if obj:
                try:
                    obj.format(f, errs)
                except Error:
                    if req == mandatory:
                        errs.append(_('Object cannot be formatted.'))
            else:
                if req == mandatory:
                    errs.append(_('Mandatory argument not available.'))

        return init, decode, encode, errors, format

    basic_cons_map = {
        bytes: bytes,
        str: str,
        int: int,
        float: float
    }
