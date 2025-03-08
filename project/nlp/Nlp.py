from konlpy.tag import Okt
from collections import Counter


class Nlp:
    
    def __init__(self):
        pass
    
    def KonlpyOkt(querys):

        okt = Okt()

        for query in querys:
            nouns = okt.nouns(result.get('description', ''))
            filtered_noun = [word for word in nouns if len(word) > 1]
            count = Counter(filtered_noun)
            noun_list = count.most_common(5)
            # most_lst = [x for x, _ in noun_list]
            result['keywords'] = noun_list
