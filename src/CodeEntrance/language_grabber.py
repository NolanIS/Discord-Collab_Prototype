from CodeEntrance.a_language_driver import ALanguageDriver
from Langs import * # Needed for ALanguageDriver.__subclasses__() to function properly

def get_languages(output_stream, input_stream):
    languages = []
    l = ALanguageDriver.__subclasses__()
    for i in l:
        languages.append(i(output_stream, input_stream))
    return l, languages
