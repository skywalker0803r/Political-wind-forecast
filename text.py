from translate import Translator

text = "我愛你"
translator = Translator(from_lang="chinese", to_lang="english")
print(translator.translate(text))
