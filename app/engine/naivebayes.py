import random

from nltk.tokenize import word_tokenize
from nltk.classify import NaiveBayesClassifier

from . import NHSTextMiner, NLPProcessor, NLP, raw_data, labels


def train_model(input_data, label, n=100, sample_size=.8):
    # TODO investigate different algorithm e.g. TF-IDF and Reinforcement NN
    print('starting to generate training data...', end='', flush=True)
    shuffled_feature_set = list()
    for key in input_data:
        words = word_tokenize(input_data[key])
        row = [tuple((NHSTextMiner.word_feat(random.sample(
            words, int(sample_size * len(words)))), label[key])) for r in range(n)]
        shuffled_feature_set += row
    print('done', flush=True)
    print('training classifier...it may take a few minutes...', end='', flush=True)
    trained_clf = NaiveBayesClassifier.train(shuffled_feature_set)
    print('done', flush=True)
    return trained_clf


def naive_bayes_classifier(query, engine, decision_boundary=.8, limit=5):
    """spell out most probable diseases and respective percentages."""
    options = list()
    words = NHSTextMiner.word_feat(word_tokenize(nlp.process(query)))
    print('understanding {}...'.format(words))
    objects = engine.prob_classify(words)
    keys = list(objects.samples())

    for key in keys:
        prob = objects.prob(key)
        options.append((key, prob))

    options.sort(key=lambda x: x[1], reverse=True)
    options = options[:limit]

    if options[0][1] > decision_boundary:
        return '{0} (~{1:.0%}))'.format(options[0][0], options[0][1]), 0
    elif options[0][1] > decision_boundary / 3:
        return ';\n'.join([pair[0] + ' (~{:.0%})'.format(pair[1])
                           for pair in options]), 1
    else:
        return None

nlp = NLPProcessor(attrs=NLP)
processed_data = nlp.process(raw_data)
Engine = train_model(processed_data, labels, n=100, sample_size=0.3)
