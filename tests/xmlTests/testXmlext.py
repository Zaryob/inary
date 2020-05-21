import unittest

try:
    from inary.sxml import xmlext_iks as xmliks
    import ciksemel

except BaseException:
    raise("Ciksemel not found")

from inary.sxml import xmlext_minidom as xmlmdom
import xml.dom.minidom
import shutil


class XmlextTestCase(unittest.TestCase):

    def setUp(self):
        self.xmlscript = '<a><b atrib="something">something in b tag.<c>something in c tag.</c></b><d>something in d tag.</d></a>'
        self.parsedmdom = xmlmdom.parseString(self.xmlscript)
        self.parsediks = xmliks.parseString(self.xmlscript)

    def testParse(self):
        with open("tests/deneme.xml", "w") as a:
            a.write(self.xmlscript)
            a.flush()
            a.close()
        self.assertEqual(
            xmlmdom.toString(
                xmlmdom.parse("tests/deneme.xml")),
            xmliks.toString(
                xmliks.parse("tests/deneme.xml")))

    def testAddNode(self):
        xmliks.addNode(self.parsediks, "newtag")
        xmliks.addNode(xmliks.getNode(self.parsediks, "b"), "newtag")
        xmlmdom.addNode(self.parsedmdom, "newtag")
        xmlmdom.addNode(xmlmdom.getNode(self.parsedmdom, "b"), "newtag")
        self.assertEqual(
            xmliks.toString(
                self.parsediks), xmlmdom.toString(
                self.parsedmdom))

    def testAddText(self):
        xmliks.addText(
            self.parsediks,
            "newtag",
            "Something else in newtag under a")
        xmliks.addText(
            xmliks.getNode(
                self.parsediks,
                "b"),
            "newtag",
            "Something else in newtag under b")
        xmlmdom.addText(
            self.parsedmdom,
            "newtag",
            "Something else in newtag under a")
        xmlmdom.addText(
            xmlmdom.getNode(
                self.parsedmdom,
                "b"),
            "newtag",
            "Something else in newtag under b")
        self.assertEqual(
            xmliks.toString(
                self.parsediks), xmlmdom.toString(
                self.parsedmdom))

    def testGetNode(self):
        self.assertEqual(
            xmliks.getNode(
                xmliks.getNode(
                    self.parsediks,
                    "b"),
                "c").toString(),
            '<c>something in c tag.</c>')
        self.assertEqual(
            xmlmdom.getNode(
                xmlmdom.getNode(
                    self.parsedmdom,
                    "b"),
                "c").toxml(),
            '<c>something in c tag.</c>')
        self.assertEqual(xmliks.getNode(xmliks.getNode(self.parsediks, "b"), "c").toString(),
                         xmlmdom.getNode(xmlmdom.getNode(self.parsedmdom, "b"), "c").toxml())

    def testGetChildElts(self):
        self.assertEqual([xmliks.getNodeText(x) for x in xmliks.getChildElts(self.parsediks)],
                         [xmlmdom.getNodeText(x) for x in xmlmdom.getChildElts(self.parsedmdom)])

    def testGetTagByName(self):
        self.assertEqual(xmliks.getNodeText(xmliks.getTagByName(self.parsediks, "b")[0]),
                         xmlmdom.getNodeText(xmlmdom.getTagByName(self.parsedmdom, "b")[0]))
        self.assertEqual(xmliks.getNodeText(xmliks.getTagByName(self.parsediks, "d")[0]),
                         xmlmdom.getNodeText(xmlmdom.getTagByName(self.parsedmdom, "d")[0]))

    def testGetChildText(self):
        self.assertEqual(xmliks.getChildText(self.parsediks, "b"),
                         xmlmdom.getChildText(self.parsedmdom, "b"))
        self.assertEqual(xmliks.getChildText(self.parsediks, "d"),
                         xmlmdom.getChildText(self.parsedmdom, "d"))
        self.assertEqual(xmliks.getChildText(xmliks.getNode(self.parsediks, "b"), "c"),
                         xmlmdom.getChildText(xmlmdom.getNode(self.parsedmdom, "b"), "c"))

    def testGetAllNodes(self):
        self.assertEqual(
            type(
                xmlmdom.getAllNodes(
                    self.parsedmdom,
                    "b")[0]),
            xml.dom.minidom.Element)
        self.assertEqual(
            type(
                xmliks.getAllNodes(
                    self.parsediks,
                    "b")[0]),
            ciksemel.Node)
        self.assertEqual(
            type(
                xmlmdom.getAllNodes(
                    self.parsedmdom,
                    "d")[0]),
            xml.dom.minidom.Element)
        self.assertEqual(
            type(
                xmliks.getAllNodes(
                    self.parsediks,
                    "d")[0]),
            ciksemel.Node)

    def testGetNodeText(self):
        self.assertEqual(
            xmliks.getNodeText(
                self.parsediks,
                "b"),
            "something in b tag.")
        self.assertEqual(
            xmlmdom.getNodeText(
                self.parsedmdom,
                "b"),
            "something in b tag.")
        self.assertEqual(
            xmliks.getNodeText(
                self.parsediks, "b"), xmlmdom.getNodeText(
                self.parsedmdom, "b"))

        self.assertEqual(
            xmliks.getNodeText(
                self.parsediks,
                "d"),
            "something in d tag.")
        self.assertEqual(
            xmlmdom.getNodeText(
                self.parsedmdom,
                "d"),
            "something in d tag.")
        self.assertEqual(
            xmliks.getNodeText(
                self.parsediks, "d"), xmlmdom.getNodeText(
                self.parsedmdom, "d"))

    def testGetNodeAttribute(self):
        self.assertEqual(
            xmliks.getNodeAttribute(
                xmliks.getNode(
                    self.parsediks,
                    "b"),
                "atrib"),
            "something")
        self.assertEqual(
            xmlmdom.getNodeAttribute(
                xmlmdom.getNode(
                    self.parsedmdom,
                    "b"),
                "atrib"),
            "something")
        self.assertEqual(xmliks.getNodeAttribute(xmliks.getNode(self.parsediks, "b"), "atrib"),
                         xmlmdom.getNodeAttribute(xmlmdom.getNode(self.parsedmdom, "b"), "atrib"))

        self.assertEqual(
            xmliks.getNodeAttribute(
                xmliks.getNode(
                    self.parsediks,
                    "b"),
                "actrib"),
            None)
        self.assertEqual(
            xmlmdom.getNodeAttribute(
                xmlmdom.getNode(
                    self.parsedmdom,
                    "b"),
                "actrib"),
            None)
        self.assertEqual(xmliks.getNodeAttribute(xmliks.getNode(self.parsediks, "b"), "actrib"),
                         xmlmdom.getNodeAttribute(xmlmdom.getNode(self.parsedmdom, "b"), "actrib"))

        self.assertEqual(
            xmliks.getNodeAttribute(
                xmliks.getNode(
                    self.parsediks,
                    "d"),
                "atrib"),
            None)
        self.assertEqual(
            xmlmdom.getNodeAttribute(
                xmlmdom.getNode(
                    self.parsedmdom,
                    "d"),
                "atrib"),
            None)
        self.assertEqual(xmliks.getNodeAttribute(xmliks.getNode(self.parsediks, "d"), "atrib"),
                         xmlmdom.getNodeAttribute(xmlmdom.getNode(self.parsedmdom, "d"), "atrib"))

    def testSetNodeAttribute(self):
        xmliks.setNodeAttribute(
            xmliks.getNode(
                self.parsediks,
                "b"),
            "atrib",
            "everything")
        xmlmdom.setNodeAttribute(
            xmlmdom.getNode(
                self.parsedmdom,
                "b"),
            "atrib",
            "everything")
        self.assertEqual(
            xmliks.getNodeAttribute(
                xmliks.getNode(
                    self.parsediks,
                    "b"),
                "atrib"),
            "everything")
        self.assertEqual(
            xmlmdom.getNodeAttribute(
                xmlmdom.getNode(
                    self.parsedmdom,
                    "b"),
                "atrib"),
            "everything")
        self.assertEqual(xmliks.getNodeAttribute(xmliks.getNode(self.parsediks, "b"), "atrib"),
                         xmlmdom.getNodeAttribute(xmlmdom.getNode(self.parsedmdom, "b"), "atrib"))

        xmliks.setNodeAttribute(
            xmliks.getNode(
                self.parsediks,
                "d"),
            "atrib",
            "anything")
        xmlmdom.setNodeAttribute(
            xmlmdom.getNode(
                self.parsedmdom,
                "d"),
            "atrib",
            "anything")
        self.assertEqual(
            xmliks.getNodeAttribute(
                xmliks.getNode(
                    self.parsediks,
                    "d"),
                "atrib"),
            "anything")
        self.assertEqual(
            xmlmdom.getNodeAttribute(
                xmlmdom.getNode(
                    self.parsedmdom,
                    "d"),
                "atrib"),
            "anything")
        self.assertEqual(xmliks.getNodeAttribute(xmliks.getNode(self.parsediks, "d"), "atrib"),
                         xmlmdom.getNodeAttribute(xmlmdom.getNode(self.parsedmdom, "d"), "atrib"))

    def testRemoveChild(self):
        xmliks.removeChild(xmliks.getNode(self.parsediks, "d"), self.parsediks)
        xmlmdom.removeChild(
            xmlmdom.getNode(
                self.parsedmdom,
                "d"),
            self.parsedmdom)
        self.assertEqual(
            xmliks.toString(
                self.parsediks), xmlmdom.toString(
                self.parsedmdom))

    def testRemoveChildText(self):
        xmliks.removeChildText(xmliks.getNode(self.parsediks, "d"))
        xmlmdom.removeChildText(xmlmdom.getNode(self.parsedmdom, "d"))
        self.assertEqual(
            xmliks.toString(
                self.parsediks),
            '<a><b atrib="something">something in b tag.<c>something in c tag.</c></b><d/></a>')
        self.assertEqual(
            xmlmdom.toString(
                self.parsedmdom),
            '<a><b atrib="something">something in b tag.<c>something in c tag.</c></b><d></d></a>')

    def testNewNode(self):
        newiks = xmliks.newNode(self.parsediks, "a")
        newdom = xmlmdom.newNode(self.parsedmdom, "a")
        xmliks.addText(newiks, "b", "something under b")
        xmlmdom.addText(newdom, "b", "something under b")
        self.assertEqual(xmliks.toString(newiks), xmlmdom.toString(newdom))

    def testNewDocument(self):
        self.assertEqual(xmlmdom.toString(xmlmdom.newDocument("newdocument")),
                         xmliks.toString(xmliks.newDocument("newdocument")))

    def testToString(self):
        self.assertEqual(
            xmliks.toString(
                self.parsediks), xmlmdom.toString(
                self.parsedmdom))

    def testToPretty(self):
        self.assertEqual(xmliks.toPretty(self.parsediks),
                         """<a>
    <b atrib="something">something in b tag.<c>something in c tag.</c>
    </b>
    <d>something in d tag.</d>
</a>""")
        self.assertEqual(xmlmdom.toPretty(self.parsedmdom),
                         """<a>
	<b atrib="something">
		something in b tag.
		<c>something in c tag.</c>
	</b>
	<d>something in d tag.</d>
</a>
""")
