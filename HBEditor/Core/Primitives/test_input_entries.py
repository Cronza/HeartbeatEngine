import sys
import random
import pytest
from PyQt5 import QtWidgets
from HBEditor.Core.settings import Settings
from HBEditor.Core.Primitives import input_entries as entry


@pytest.fixture
def get_data_dict():
    return {"value":""}

@pytest.fixture
def get_list_data():
    return [random.randint(0, 255),random.randint(0, 255),random.randint(0, 255)]

@pytest.fixture
def get_options():
    return ["karin","himiko"]

@pytest.fixture
def get_filename():
    return random.choice(["hello_there.yaml","general_kenobi.yaml"])

@pytest.fixture
def get_text():
    return "hello there poeple of the earth!"

@pytest.fixture
def get_vector2():
    return [-1,1],[1,1],[223542435,24352345]

@pytest.fixture
def get_resolution():
    return [[1280, 720], [1920, 1080]]


def test_InputEntryColorSet(get_data_dict, get_list_data):
    app = QtWidgets.QApplication(sys.argv)
    test = entry.InputEntryColor(get_data_dict)
    test.Set(get_list_data)
    assert test.Get()["value"] == get_list_data

def test_InputEntryBoolSet(get_data_dict):
    app = QtWidgets.QApplication(sys.argv)
    test = entry.InputEntryBool(get_data_dict)
    test.Set(True)
    assert test.Get()["value"] == True
    test.Set(False)
    assert test.Get()["value"] == False

def test_InpuitEntryDropdownSet(get_data_dict, get_options):
    app = QtWidgets.QApplication(sys.argv)
    get_data_dict["options"] = get_options
    test = entry.InputEntryDropdown(get_data_dict)
    choice = random.choice(get_options)
    test.Set(choice)
    assert test.Get()["value"] == choice
    
def test_InputEntryfileSelectorSet(get_data_dict,get_filename):
    #TODO: Must implement GUI testing for OpenFilePrompt
    app = QtWidgets.QApplication(sys.argv)
    test = entry.InputEntryFileSelector(get_data_dict, None, Settings.getInstance().supported_content_types["Data"])
    test.Set(get_filename)
    assert test.Get()["value"] == get_filename
    
def test_InputEntryFloatSet(get_data_dict):
    app = QtWidgets.QApplication(sys.argv)
    test = entry.InputEntryFloat(get_data_dict)
    numbers = [-10,0,10,12301542.123456789]
    for i in range(len(numbers)):
        test.Set(numbers[i])
        assert test.Get()["value"] == numbers[i]
        
def test_InputEntryIntSet(get_data_dict):
    app = QtWidgets.QApplication(sys.argv)
    test = entry.InputEntryInt(get_data_dict)
    numbers = [-10,0,10,12301542]
    for i in range(len(numbers)):
        test.Set(numbers[i])
        assert test.Get()["value"] == numbers[i]
        
def test_InputEntryPragraphSet(get_data_dict,get_text):
    app = QtWidgets.QApplication(sys.argv)
    test = entry.InputEntryParagraph(get_data_dict)
    test.Set(get_text)
    assert test.Get()["value"] == get_text

def test_InputEntryTextSet(get_data_dict,get_text):
    app = QtWidgets.QApplication(sys.argv)
    test = entry.InputEntryText(get_data_dict)
    test.Set(get_text)
    assert test.Get()["value"] == get_text

def test_InputEntryTupleSet(get_data_dict,get_vector2):
    app = QtWidgets.QApplication(sys.argv)
    test = entry.InputEntryTuple(get_data_dict)
    test.Set(get_vector2)
    for i in range(len(get_vector2)):
        test.Set(get_vector2[i])
        assert test.Get()["value"] == get_vector2[i]
        
def test_InputEntryResolutionSet(get_data_dict,get_resolution):
    #TODO: Revisit when testing is capable of creating a project
    pass