import spacy
from spacy.matcher import Matcher

class spacy_process:
    def __init__(self) -> None:
        if spacy.prefer_gpu():
            print("GPU is enabled")
        else:
            print("GPU is not available, using CPU instead")
        # 启用 GPU
        spacy.require_gpu()
        # 加载模型
        self.nlp = spacy.load("zh_core_web_sm")
        # 初始化Matcher
        self.matcher = Matcher(self.nlp.vocab)

    def get_time_text(self,query):
        # 处理句子
        doc = self.nlp(query)
        # 提取时间相关的词汇,格式为["",""]
        time_words = [ent.text for ent in doc.ents if ent.label_ == "DATE"]
        return time_words
        

    def get_plan(self,query=None):
        pass

