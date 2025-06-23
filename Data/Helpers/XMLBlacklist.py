import os
import xml.etree.ElementTree as ET

BLACKLIST_FILE = os.path.join(os.path.dirname(__file__), "blacklist.xml")

def loadBlacklist():
    try:
        tree = ET.parse(BLACKLIST_FILE)
        root = tree.getroot()
        lista = [w.text for w in root.iter("word") if w.text] # svaki ele koji nije prazan ispiši
        return lista
    except FileNotFoundError:
        print("blacklist.xml nije pronađen.")
        return []

def addWordToBlacklist(word):
    tree = ET.parse(BLACKLIST_FILE)
    root = tree.getroot()
    new_word = ET.Element("word")
    new_word.text = word
    root.append(new_word)
    tree.write(BLACKLIST_FILE, encoding="ISO-8859-2", xml_declaration=True)

def removeWordFromBlacklist(word):
    tree = ET.parse(BLACKLIST_FILE)
    root = tree.getroot()
    for w in root.findall("word"):
        if w.text == word:
            root.remove(w)
    tree.write(BLACKLIST_FILE, encoding="ISO-8859-2", xml_declaration=True)

def updateWordInBlacklist(old_word, new_word):
    tree = ET.parse(BLACKLIST_FILE)
    root = tree.getroot()
    for w in root.findall("word"):
        if w.text == old_word:
            w.text = new_word
    tree.write(BLACKLIST_FILE, encoding="ISO-8859-2", xml_declaration=True)
