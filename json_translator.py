import xml.etree.ElementTree as ElementTree
import os
from googletrans import Translator
import json



def translateJson(file, output_lang):
    root = {}
    try:
        with open(file, 'r', encoding='utf-8') as json_file:
            root = json.load(json_file)

        print(root)
    except FileNotFoundError:
        print(f"File not found: {file}")
    except json.JSONDecodeError as e:
        print(f"JSON decoding error: {e}")
    translator = Translator()

    for i in range(len(root)):

        value = root[i].get('description')

        if value is not None:
            input_text = value
            input_text = input_text.replace("\n", " ")
            if 'font color' in input_text:
                text = input_text
            text = str(translator.translate(input_text, dest=output_lang).text.title().strip())
            text = text.replace("%S", "%s")

            root[i]["description"] = text
            print(value + "-->" + root[i]["description"])

    translated_file = file

    try:
        with open(translated_file, 'w', encoding='utf-8') as file:
            json.dump(root, file, indent='\t', ensure_ascii=False)
        print("Data has been written to the file.")
    except IOError as e:
        print(f"Error writing to the file: {e}")