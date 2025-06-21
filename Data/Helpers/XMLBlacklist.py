import os
import xml.etree.ElementTree as ET

BLACKLIST_FILE = os.path.join(os.path.dirname(__file__), "blacklist.xml")

def load_blacklist():
    try:
        tree = ET.parse(BLACKLIST_FILE)
        root = tree.getroot()
        list = [w.text for w in root.iter("word") if w.text]
        print(f"[DEBUG] Lista je {list}")
        return list
    except FileNotFoundError:
        print("[ERROR] blacklist.xml nije pronađen.")
        return []

def add_word_to_blacklist(word):
    tree = ET.parse(BLACKLIST_FILE)
    root = tree.getroot()
    new_word = ET.Element("word")
    new_word.text = word
    root.append(new_word)
    tree.write(BLACKLIST_FILE, encoding="utf-8", xml_declaration=True)

def remove_word_from_blacklist(word):
    tree = ET.parse(BLACKLIST_FILE)
    root = tree.getroot()
    for w in root.findall("word"):
        if w.text == word:
            root.remove(w)
            break
    tree.write(BLACKLIST_FILE, encoding="utf-8", xml_declaration=True)

def update_word_in_blacklist(old_word, new_word):
    tree = ET.parse(BLACKLIST_FILE)
    root = tree.getroot()
    for w in root.findall("word"):
        if w.text == old_word:
            w.text = new_word
            break
    tree.write(BLACKLIST_FILE, encoding="utf-8", xml_declaration=True)
