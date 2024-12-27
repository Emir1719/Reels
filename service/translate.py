from googletrans import Translator
# import deepl

class Translate:
    def translateWithGoogle(self, sentence):
        translator = Translator()
        value = translator.translate(sentence, dest='tr')
        
        return value.text
    
    """def translateWithDeepl(self, sentence):
       # şu an key olmadığı için çalışmaz
       translator = deepl.Translator("auth_key")
       result = translator.translate_text(sentence, target_lang="TR")
       
       return result.text"""