# -*- coding: utf-8 -*-
__author__ = 'isparks'

import unittest
from rwslib.builders import *
from xml.etree import cElementTree as ET
from test_builders import obj_to_doc, bool_to_yes_no

# Metadata object tests


class TestTranslatedText(unittest.TestCase):
    def test_builder(self):
        """XML produced"""
        tested = TranslatedText('en','A test')
        doc = obj_to_doc(tested)
        self.assertEquals(doc.tag, "TranslatedText")
        self.assertEquals("en", doc.attrib['xml:lang'])
        self.assertEquals("A test", doc.text)

    def test_accepts_no_children(self):
        with self.assertRaises(ValueError):
            TranslatedText('en','test') << object()


class TestSymbols(unittest.TestCase):
    def test_can_only_receive_translated_text(self):
        with self.assertRaises(ValueError):
            Symbol() << object()

    def test_translated_text_received(self):
        tested = Symbol()
        tested << TranslatedText('en','Test string')
        self.assertEqual(1, len(tested.translations))

    def test_builder(self):
        """XML produced"""
        tested = Symbol()(TranslatedText('en','Test string'))
        doc = obj_to_doc(tested)
        self.assertEquals(doc.tag, "Symbol")
        self.assertEquals(doc.getchildren()[0].tag, "TranslatedText")


class TestMeasurementUnits(unittest.TestCase):
    def test_basic(self):
        tested = MeasurementUnit('MU_OID', 'MU_NAME')
        self.assertEqual(1, tested.constant_a)
        self.assertEqual(1, tested.constant_b)
        self.assertEqual(0, tested.constant_c)
        self.assertEqual(0, tested.constant_k)
        self.assertEqual(0, len(tested.symbols))

    def test_kg(self):
        tested = MeasurementUnit("MSU00001", "KG", unit_dictionary_name='UN1', standard_unit=True)
        doc = obj_to_doc(tested)
        self.assertEquals(doc.attrib['mdsol:StandardUnit'],"Yes")

    def test_can_only_receive_symbol(self):
        with self.assertRaises(ValueError):
            MeasurementUnit('MU_OID','MU_NAME') << object()

    def test_symbol_received(self):
        tested = MeasurementUnit('MU_OID', 'MU_NAME')
        tested << Symbol()
        self.assertEqual(1, len(tested.symbols))

    def test_builder(self):
        """XML produced"""
        tested = MeasurementUnit('MU_OID', 'MU_NAME')(Symbol())
        doc = obj_to_doc(tested)
        self.assertEquals(doc.tag, "MeasurementUnit")
        self.assertEquals(doc.getchildren()[0].tag, "Symbol")


class TestBasicDefinitions(unittest.TestCase):
    def test_basic(self):
        tested = BasicDefinitions()
        self.assertEqual(0, len(tested.measurement_units))

    def test_mus_onlu(self):
        tested = BasicDefinitions()
        with self.assertRaises(ValueError):
            tested << object()

    def test_mus(self):
        tested = BasicDefinitions()
        tested << MeasurementUnit("MU_OID", "MUNAME")
        self.assertEqual(1, len(tested.measurement_units))

    def test_builder(self):
        """XML produced"""
        tested = BasicDefinitions()(MeasurementUnit("MU_OID", "MUNAME"))
        doc = obj_to_doc(tested)
        self.assertEquals(doc.tag, "BasicDefinitions")
        self.assertEquals(doc.getchildren()[0].tag, "MeasurementUnit")


class TestGlobalVariables(unittest.TestCase):
    """Test Global Variables class"""

    def test_basic(self):
        tested = GlobalVariables('project_name', 'name', 'description')
        self.assertEqual('project_name', tested.protocol_name)
        self.assertEqual('name', tested.name)
        self.assertEqual('description', tested.description)

    def test_defaults(self):
        tested = GlobalVariables('project_name')
        self.assertEqual('project_name', tested.protocol_name)
        self.assertEqual('project_name', tested.name) #Defaults to protocol_name
        self.assertEqual('', tested.description) #Defaults to empty string

    def test_no_children(self):
        """GlobalVariables accepts no children"""
        with self.assertRaises(ValueError):
            GlobalVariables('TEST') << object()

    def test_builder(self):
        """XML produced"""
        tested = GlobalVariables('project_name', description="A description")
        doc = obj_to_doc(tested)
        self.assertEquals(doc.tag, "GlobalVariables")
        self.assertEquals(doc.getchildren()[0].tag, "StudyName")
        self.assertEquals("project_name", doc.getchildren()[0].text)
        self.assertEquals(doc.getchildren()[1].tag, "StudyDescription")
        self.assertEquals("A description", doc.getchildren()[1].text)
        self.assertEquals(doc.getchildren()[2].tag, "ProtocolName")
        self.assertEquals("project_name", doc.getchildren()[2].text)


class TestStudyEventRef(unittest.TestCase):
    def test_cannot_accept_child(self):
        with self.assertRaises(ValueError):
            StudyEventRef("OID",2,False) << object()


class TestProtocol(unittest.TestCase):

    def test_can_accept_studyeventref_child(self):
        se = StudyEventRef('OID',2,True)
        tested = Protocol()(se)
        self.assertEqual(se, tested.study_event_refs[0])

    def test_cannot_accept_non_study_eventref_child(self):
        with self.assertRaises(ValueError):
            Protocol() << object()

    def test_builder(self):
        """XML produced"""
        doc = obj_to_doc(Protocol()(StudyEventRef("OID",1,True)))
        self.assertEquals(doc.tag, "Protocol")
        self.assertEquals(doc.getchildren()[0].tag, "StudyEventRef")


class TestFormRef(unittest.TestCase):

    def test_cannot_accept_any_child(self):
        with self.assertRaises(ValueError):
            FormRef('OID',1,False) << object()


class TestStudyEventDef(unittest.TestCase):
    def test_cannot_accept_non_formref_child(self):
        with self.assertRaises(ValueError):
            StudyEventDef("OID","Name", False, StudyEventDef.SCHEDULED) << object()

    def test_can_accept_formref_child(self):
        tested = StudyEventDef("OID","Name", False, StudyEventDef.SCHEDULED)(FormRef("FORMOID",1,False))
        self.assertEqual(1, len(tested.formrefs))

    def test_builder(self):
        tested = StudyEventDef("OID","Name", False,
                               StudyEventDef.SCHEDULED,
                               category = "Test Cat",
                               access_days= 1,
                               start_win_days = 2,
                               target_days = 3,
                               end_win_days = 4,
                               overdue_days = 5,
                               close_days = 6
                               )
        tested << FormRef("FORMOID",1,False)

        doc = obj_to_doc(tested)
        self.assertEquals(doc.tag, "StudyEventDef")
        self.assertEquals("OID", doc.attrib['OID'])
        self.assertEquals("Name", doc.attrib['Name'])
        self.assertEquals("Scheduled", doc.attrib['Type'])
        self.assertEquals("Test Cat", doc.attrib['Category'])
        self.assertEquals("1", doc.attrib['mdsol:AccessDays'])
        self.assertEquals("2", doc.attrib['mdsol:StartWinDays'])
        self.assertEquals("3", doc.attrib['mdsol:TargetDays'])
        self.assertEquals("4", doc.attrib['mdsol:EndWinDays'])
        self.assertEquals("5", doc.attrib['mdsol:OverDueDays'])
        self.assertEquals("6", doc.attrib['mdsol:CloseDays'])
        self.assertEquals("FormRef", doc.getchildren()[0].tag)


class TestItemGroupRef(unittest.TestCase):

   def test_accepts_no_children(self):
        with self.assertRaises(ValueError):
            ItemGroupRef("ItemGroup1",1) << object()

   def test_builder(self):
        tested = ItemGroupRef("ItemGroup1",1, mandatory=True)
        doc = obj_to_doc(tested)
        self.assertEquals(doc.tag, "ItemGroupRef")
        self.assertEquals("ItemGroup1", doc.attrib['ItemGroupOID'])
        self.assertEquals("1", doc.attrib['OrderNumber'])
        self.assertEquals("Yes", doc.attrib['Mandatory'])


class TestMdsolHelpTexts(unittest.TestCase):
    def test_build(self):
        tested = MdsolHelpText("en","This is a help text")
        doc = obj_to_doc(tested)
        self.assertEquals(doc.tag, "mdsol:HelpText")
        self.assertEquals("en", doc.attrib['xml:lang'])
        self.assertEquals("This is a help text", doc.text)

    def test_accepts_no_children(self):
        with self.assertRaises(ValueError):
            MdsolHelpText("en","Content") << object()


class TestFormDef(unittest.TestCase):

    def test_only_accept_itemgroup_ref(self):
        with self.assertRaises(ValueError):
            FormDef("VS","Vital Signs") << object()

    def test_accept_itemgroup_ref(self):
        tested = FormDef("DM", "Demog", order_number=1)(ItemGroupRef("ItemGroup1", 1))
        self.assertEqual(1, len(tested.itemgroup_refs))

    def test_builder(self):
        tested = FormDef("DM", "Demog", repeating=True,
                         order_number= 2,
                         link_form_oid='FRM1',
                         link_study_event_oid='EVT1')\

        tested << ItemGroupRef("ItemGroup1", 1)
        tested << MdsolHelpText("en","This is a help text")
        doc = obj_to_doc(tested)
        self.assertEquals(doc.tag, "FormDef")
        self.assertEquals("DM", doc.attrib['OID'])
        self.assertEquals("Demog", doc.attrib['Name'])
        self.assertEquals("Yes", doc.attrib['Repeating'])
        self.assertEquals("2", doc.attrib['mdsol:OrderNumber'])
        # Would not see LinkFormOID and LinkStudyEventOID together, they are mutually exclusive. Just for coverage.
        self.assertEquals("FRM1", doc.attrib['mdsol:LinkFormOID'])
        self.assertEquals("EVT1", doc.attrib['mdsol:LinkStudyEventOID'])
        self.assertEquals("ItemGroupRef", doc.getchildren()[0].tag)
        self.assertEquals("mdsol:HelpText", doc.getchildren()[1].tag)


class TestMetaDataVersion(unittest.TestCase):
    """Contains Metadata for study design. Rave only allows one, the spec allows many in an ODM doc"""

    def test_cannot_accept_non_protocol_child(self):
        with self.assertRaises(ValueError):
            MetaDataVersion("OID","NAME") << object()

    def test_can_accept_protocol_child(self):
        prot = Protocol()
        tested = MetaDataVersion("OID","NAME")(prot)
        self.assertEqual(prot, tested.protocol)

    def test_can_accept_study_eventdef_child(self):
        sed = StudyEventDef("OID","Name", False, StudyEventDef.SCHEDULED)
        tested = MetaDataVersion("OID","NAME")(sed)
        self.assertEqual(sed, tested.study_event_defs[0])

    def test_builder(self):
        """XML produced"""
        tested =  MetaDataVersion("OID","NAME", description="A description",
                                  primary_formoid="DM",
                                  default_matrix_oid="DEFAULT",
                                  signature_prompt='I confirm.',
                                  delete_existing=True)

        tested << Protocol()
        tested << StudyEventDef("OID","Name", False, StudyEventDef.SCHEDULED)


        doc = obj_to_doc(tested)
        self.assertEquals(doc.tag, "MetaDataVersion")
        self.assertEquals("OID", doc.attrib['OID'])
        self.assertEquals("NAME", doc.attrib['Name'])
        self.assertEquals("A description", doc.attrib['Description'])
        self.assertEquals("DEFAULT", doc.attrib['mdsol:DefaultMatrixOID'])
        self.assertEquals("I confirm.", doc.attrib['mdsol:SignaturePrompt'])
        self.assertEquals("DM", doc.attrib['mdsol:PrimaryFormOID'])
        self.assertEquals("Yes", doc.attrib['mdsol:DeleteExisting'])
        self.assertEquals("Protocol", doc.getchildren()[0].tag)
        self.assertEquals("StudyEventDef", doc.getchildren()[1].tag)


class TestStudy(unittest.TestCase):
    """Test Study Metadata class"""

    def test_oid(self):
        tested = Study('oid1')
        self.assertEqual('oid1', tested.oid)

    def test_default_project_type(self):
        tested = Study('oid1')
        self.assertEqual('Project', tested.project_type)

    def test_invalid_project_type(self):
        with self.assertRaises(ValueError):
            Study('oid1', project_type='Prijket')

    def test_provided_project_type(self):
        tested = Study('oid1', 'GlobalLibrary Volume')
        self.assertEqual('GlobalLibrary Volume', tested.project_type)

    def test_cannot_accept_itemdata(self):
        tested = Study('oid')
        with self.assertRaises(ValueError):
            tested << ItemData("Field1", "ValueC")

    def test_can_accept_globalvariables(self):
        tested = Study('oid')
        gv = GlobalVariables('MY_TEST_PROJECT')
        tested << gv
        self.assertEqual(gv, tested.global_variables)

    def test_cannot_accept_two_globalvariables(self):
        tested = Study('oid')(GlobalVariables('MY_TEST_PROJECT'))
        with self.assertRaises(ValueError):
            tested << GlobalVariables('Another_one')

    def test_can_accept_basic_definitions(self):
        tested = Study('oid')
        bd = BasicDefinitions()
        tested << bd
        self.assertEqual(bd, tested.basic_definitions)

    def test_cannot_accept_two_basic_definitions(self):
        tested = Study('oid')(BasicDefinitions())
        with self.assertRaises(ValueError):
            tested << BasicDefinitions()

    def test_can_accept_metadata_version(self):
        tested = Study('oid')
        mv = MetaDataVersion('OID','Name')
        tested << mv
        self.assertEqual(mv, tested.metadata_version)

    def test_cannot_accept_two_metadata_versions(self):
        tested = Study('oid')(MetaDataVersion('OID1','NAME1'))
        with self.assertRaises(ValueError):
            tested << MetaDataVersion('OID2','NAME2')

    def test_builder(self):
        """XML produced"""
        tested = Study('oid1', 'GlobalLibrary Volume')(
                                                       GlobalVariables('MY_TEST_PROJECT'),
                                                       BasicDefinitions(),
                                                       MetaDataVersion("OID","NAME")
                                                       )
        doc = obj_to_doc(tested)
        self.assertEquals(doc.tag, "Study")
        self.assertEquals(doc.attrib['mdsol:ProjectType'], "GlobalLibrary Volume")
        self.assertEquals(doc.getchildren()[0].tag, "GlobalVariables")
        self.assertEquals(doc.getchildren()[1].tag, "BasicDefinitions")
        self.assertEquals(doc.getchildren()[2].tag, "MetaDataVersion")


if __name__ == '__main__':
    unittest.main()
