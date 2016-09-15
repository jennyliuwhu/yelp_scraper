# -*- coding: UTF-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import re

__author__ = 'jialingliu'

tag_open = re.compile(r"<(\w+)([^>]*?)>", re.DOTALL)
tag_close = re.compile(r"</(\w+)([^>]*?)>|/>", re.DOTALL)
tag_open_close = re.compile(r"<(\w+[^>]*?)\s*?([^>]*?)/>", re.DOTALL)

comment = re.compile(r"<!--(.*?)-->", re.DOTALL)
xml_prolog = re.compile(r"<\?([^>]*)\?>", re.DOTALL)
html_declaration = re.compile(r"<!([\w\s]*?)>", re.DOTALL)

# test_snippet = """<?xml version="1.0" encoding="UTF-8"?>
# <!DOCTYPE xml> <!-- not actually valid xml-->
# <!-- This is a comment -->
# <note date="8/31/12">
#     <note date="8/31/12">Tove</note>
#     <from>Jani</from>
#     <heading type="Reminder"/>
#     <body>Don't forget me this weekend!</body>
#     <!-- This is a multiline comment,
#          which take a bit of care to parse -->
# </note>
# """
# course_webpage = requests.get("http://www.datasciencecourse.org").content

# multi_comment = """<!--[if lt IE 9]>
#         <script src="https://oss.maxcdn.com/libs/html5shiv/3.7.0/html5shiv.js"></script>
#         <script src="https://oss.maxcdn.com/libs/respond.js/1.4.2/respond.min.js"></script>
#     <![endif]-->"""

# print comment.findall(multi_comment)
# print comment1.findall(multi_comment)
# print att.findall("""""")

# print tag_open.findall(test_snippet)
# print tag_close.findall(test_snippet)
# print tag_open.match(test_snippet, 211)
# print tag_close.match(test_snippet, 211)
# print comment.findall(test_snippet)
# print comment1.findall(test_snippet)
# print xml_prolog.match(test_snippet, 211)
# print html_declaration.match(test_snippet, 211)
# print blank.match(test_snippet, 211)
# print test_snippet[211:]

# print test_snippet[39:]
# print "----------------------------------------"
# print test_snippet[54:]
# print "----------------------------------------"
# print test_snippet[85:]
# print "----------------------------------------"
# print test_snippet[140:]
# print "----------------------------------------"
# print test_snippet[304:335]
# print "----------------------------------------"


class XMLNode:
    def __init__(self, tag, attributes, raw_content):
        self.tag = tag
        self.attributes = attributes
        self.content = raw_content
        self.children = []
        pos = raw_content.find("<")
        while raw_content[pos:].find("<") != -1:
            pos = raw_content[pos:].find("<") + pos
            match_open_close = tag_open_close.match(raw_content, pos)
            match_open = tag_open.match(raw_content, pos)
            match_close = tag_close.match(raw_content, pos)

            match_comment = comment.match(raw_content, pos)
            match_prolog = xml_prolog.match(raw_content, pos)
            match_declaration = html_declaration.match(raw_content, pos)

            if match_comment or match_prolog or match_declaration:
                if match_comment:
                    pos = match_comment.end()
                if match_prolog:
                    pos = match_prolog.end()
                if match_declaration:
                    pos = match_declaration.end()
                continue

            if match_open_close:
                new_attribute = parse_attributes(match_open_close.group(2))
                self.children.append(XMLNode(match_open_close.group(1), new_attribute, ""))
                pos = match_open_close.end()
                continue
            if match_open:
                new_attribute = parse_attributes(match_open.group(2))
                self.children.append(XMLNode(match_open.group(1), new_attribute, raw_content[match_open.end():]))
                if hasattr(self.children[-1], "endpos"):
                    pos = match_open.end() + self.children[-1].endpos
                else:
                    pos = match_open.end()
                continue
            if match_close:
                if match_close.group(1) != tag:
                    raise Exception("Error: <{0}> tag closed with {1}".format(tag, match_close.group()))
                else:
                    self.content = self.content[:match_close.start()]
                    self.endpos = match_close.end()
                break

    def find(self, tag, **kwargs):
        """
        Search for a given tag and atributes anywhere in the XML tree

        Args:
            tag (string): tag to match
            kwargs (dictionary): list of attribute name / attribute value pairs to match

        Returns:
            (list): a list of XMLNode objects that match from anywhere in the tree
        """
        result = []
        self.find_helper(tag, result, **kwargs)
        return result

    def find_helper(self, tag, result, **kwargs):
        contains_all = all(item in self.attributes.items() for item in kwargs.items())
        if self.tag == tag and contains_all:
            result.append(self)
        for child in self.children:
            child.find_helper(tag, result, **kwargs)


def total_count(n):
    """ Gets the total number of nodes in an XMLNode tree. """
    return len(n.children) + sum(total_count(c) for c in n.children)


def parse_attributes(s):
    splited = re.compile(r"[\"\']").split(s)[:-1]
    attributes = dict()
    for i in range(len(splited)):
        if i % 2 == 0:
            # key
            key = splited[i].split("=")[0].strip()
        else:
            # value
            val = splited[i]
            attributes[key] = val
    return attributes

# root = XMLNode("", {}, test_snippet)
#
# print "root.tag: ", root.tag
# print "root.attributes: ", root.attributes
# print "root.content: ", repr(root.content)
# print "root.children: ", root.children
# print ""
# print "note.tag: ", root.children[0].tag
# print "note.attributes: ", root.children[0].attributes
# print "note.content: ", repr(root.children[0].content)
# print "note.children: ", root.children[0].children
# print ""
# print "to.tag: ", root.children[0].children[0].tag
# print "to.attributes: ", root.children[0].children[0].attributes
# print "to.content: ", repr(root.children[0].children[0].content)
# print "to.children: ", root.children[0].children[0].children
# print ""
# print "heading.tag: ", root.children[0].children[2].tag
# print "heading.attributes: ", root.children[0].children[2].attributes
# print "heading.content: ", repr(root.children[0].children[2].content)
# print "heading.children: ", root.children[0].children[2].children
#
#
# root = XMLNode("", {}, course_webpage)
# print total_count(root)
# print root.find("")[0].content
# print[l.attributes["href"] for l in links]
# tbody = root.find("section", id="schedule")[0].find("table")[0].find("tbody")[0]
# # a = tbody.find("tr")[1]
# # print a.find("td")[0].content
# # print tbody.find("tr")
# # for a in tbody.find("tr"):
# #     print a.tag
# #     if len(a.find("td")) > 1:
# #         print a.find("td")[0].content
# #         print "----------------"
# print [a.find("td")[0].content for a in tbody.find("tr") if len(a.find("td")) > 1]

#
# test = """<a name="access</a>"""
#
# root = XMLNode("", {}, test)
# # print root.find("a")[0].tag
#
# test_snippet = """<?xml version="1.0" encoding="UTF-8"?>
# <!DOCTYPE xml> <!-- not actually valid xml-->
# <!-- This is a comment -->
# <!--[if lt IE 9]>
#     <script src="https://oss.maxcdn.com/libs/html5shiv/3.7.0/html5shiv.js"></script>
#     <script src="https://oss.maxcdn.com/libs/respond.js/1.4.2/respond.min.js"></script>
#     <haha />
#     <to>Tove</to>
#     <li>
#     </li>
#     <from>Jani</from>
# <![endif]-->
# <note date="8/31/12" a = "b" haha = 'haha '  class="col-lg-10 col-lg-offset-1" c = 'p '  >
#     <to>Tove</to>
#     <li></li>
#     <from>Jani</from>
#     <heading type='Reminder' />
#     <body>Don't forget me this weekend!</body>
#     <!-- This is a multiline comment,
#          which take a bit of care to parse -->
# </note>
# """

# root = XMLNode("", {}, test_snippet)
# # print total_count(root)
#
# print root.find("note")[0].attributes

# test_att = """ date="8/31/12" a = "b" haha = 'haha    '  class="col-lg-10 col-lg-offset-1" c = 'p '"""
# print re.compile(r"[\"\']").split(test_att)
# splited = []
# for part in test_att.split("="):
# print parse_attributes(test_att)
