from gensim.utils import simple_preprocess


def preprocess(text):
    return " ".join(simple_preprocess(text))
