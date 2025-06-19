import xml
import xml.etree.ElementTree as ET
import os
from xml import etree


def save_chat_to_xml(messages):
    filename="Data/Helpers/chat.xml"
    if not os.path.exists(filename):
        root = ET.Element("chat")
        tree = ET.ElementTree(root)
    else:
        try:
            tree = ET.parse(filename)
            root = tree.getroot()
        except ET.ParseError:
            root = ET.Element("chat")
            tree = ET.ElementTree(root)

    for msg in messages:
        message_el = ET.SubElement(root, "message")

        sender_el = ET.SubElement(message_el, "sender")
        sender_el.text = msg["sender"]

        timestamp_el = ET.SubElement(message_el, "timestamp")
        timestamp_el.text = msg["timestamp"]

        content_el = ET.SubElement(message_el, "content")
        content_el.text = msg["content"]

    print("Probaj writeat u xml")
    tree.write(filename, encoding="utf-8", xml_declaration=True)
