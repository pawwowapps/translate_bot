import xml.etree.ElementTree as ElementTree
import os
from googletrans import Translator
import xml.etree.ElementTree as ET



def translateXml(file, output_lang):
    translator = Translator()
    tree = ElementTree.parse(file)
    root = tree.getroot()

    for i in range(len(root)):
        element = root[i]
        if ('string-array' in element.tag):
            items = element.findall('item')
            for it in range(len(items)):
                value = root[i][it].text
                if value is not None:
                    input_text = value
                    text = translateAndParse(input_text, translator, output_lang)
                    root[i][it].text = text
                    print(value + "-->" + root[i][it].text)
        else:
            if 'translatable' not in element.attrib:
                value = root[i].text

                if value is not None:
                    input_text = value
                    text = translateAndParse(input_text, translator, output_lang)
                    root[i].text = text
                    print(value + "-->" + root[i].text)

    translated_file = file

    xml_str = ET.tostring(root, encoding="unicode", method="xml")
    xml_str = xml_str.replace("&gt;", ">")
    xml_str = xml_str.replace("&lt;", "<")
    with open(translated_file, "w", encoding="utf-8") as file:
        file.write(xml_str)

def translateAndParse(input_text, translator, language_to_translate):
    text = ""
    if 'font color' in input_text:
        text = input_text
    text = str(translator.translate(input_text, dest=language_to_translate, src='en').text.title().strip())
    text = text.replace("%S", "%s")
    text = text.replace("%A", "%s")
    text = text.replace("</B>", "</b>")
    text = text.replace("<B>", "<b>")
    text = text.replace("<Br", "<br")
    text = text.replace("<BR", "<br")
    text = text.replace("</I>", "</i>")
    text = text.replace("<I>", "<i>")
    text = text.replace("Fgcolor", "fgcolor")
    text = text.replace("FGCOLOR", "fgcolor")
    text = text.replace("<Font", "<font")
    text = text.replace("</Font", "</font")
    text = text.replace("font Color", "font color")
    text = text.replace("<br />", "<br/>")
    text = text.replace("\\N", "\\n")
    text = text.replace("\'", "\\'")
    text = text.replace(" ", "")
    return text