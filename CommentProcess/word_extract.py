import os.path
import word_preprocess
from itertools import chain
from collections import Counter
import nltk


names_files = ['hair_dryer.tsv', 'microwave.tsv', 'pacifier.tsv']
WORDS=500


def main(path_dirOfFile, path_output):
    word_prop_set = {'JJ', 'JJR', 'JJS', 'RB', 'RBR', 'RBS', 'VBD', 'VBG', 'VBN'}
    for name in names_files:
        counter_words = Counter()
        path_fileToRead = f'{path_dirOfFile}/{name}'
        path_outputFile = f'{path_output}/word_list_{name.replace("tsv", "txt")}'
        arr_title, arr_comment = word_preprocess.main(path_fileToRead)
        for comment in arr_comment:
            counter_words.update(chain.from_iterable(comment.review_body_pcsed))
        list_words = []
        for word, times in sorted(counter_words.most_common(), key=lambda x: x[1], reverse=True):
            text = nltk.word_tokenize(word)
            if nltk.pos_tag(text)[0][1] in word_prop_set:
                list_words.append((word, times))
        print(sum(x[1] for x in list_words[:WORDS])/sum(x[1] for x in list_words))
        file_out = open(path_outputFile, 'w', encoding='utf-8')
        file_out.write('\n'.join(f'{word}=' for word, times in list_words[:WORDS]))
        file_out.close()


if __name__ == '__main__':
    path_dirOfMe = os.path.split(os.path.realpath(__file__))[0]
    path_output = '/'.join(path_dirOfMe.split('\\')[:-1])+"/Output"
    path_dirOfFile = '/'.join(path_dirOfMe.split('\\')[:-1])+"/Dateset";
    main(path_dirOfFile, path_output)
