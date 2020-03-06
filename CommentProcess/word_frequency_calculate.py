import word_preprocess
import os.path
from itertools import groupby, chain
from collections import Counter, defaultdict
from datetime import date

names = ['file1.tsv', 'file2.tsv', 'file3.tsv']
WEIGHT_INCREAMENT_PER_LEVEL=0.5

def main(arr_title, arr_comments, path_output):
    file1 = open(f'{path_output}/{names[0]}', 'w', encoding='utf-8')
    file1.write('review_id\ttext_freq\n')
    file1.write('\n'.join(wordFreq_perCom_lineiter(arr_comments)))
    file1.close()

    file2 = open(f'{path_output}/{names[1]}', 'w', encoding='utf-8')
    file2.write('review_id\ttext_freq\n')
    file2.write('\n'.join(wordFreq_perCom_modifedWeight_lineiter(arr_comments)))
    file2.close()

    file3 = open(f'{path_output}/{names[2]}', 'w', encoding='utf-8')
    file3.write('product_id\ttext_freq\n')
    file3.write('\n'.join(wordFreq_perCom_modifedWeight_lineiter(arr_comments)))
    file3.close()


def wordFreq_perCom_lineiter(arr_comments):
    for comment in arr_comments:
        review_id = comment.review_id
        counter = Counter(chain.from_iterable(comment.review_body_pcsed))
        text_freq = ';'.join(f'{k}:{round(100*v, 2)}%' for k, v in counter.items())
        yield f'{review_id}\t{text_freq}'


def wordFreq_perCom_modifedWeight_lineiter(arr_comments):
    cmp_key = lambda x: (x.customer_id, x.review_date)
    arr_comments.sort(key=cmp_key)
    for idx, (key, group) in enumerate(groupby(arr_comments, key=lambda x: x.customer_id)):
        for comment in group:
            def get_freq(cnt):
                return 100*(1+idx*WEIGHT_INCREAMENT_PER_LEVEL)*cnt
            counter = Counter(chain.from_iterable(comment.review_body_pcsed))
            text_freq =';'.join(f'{k}:{round(get_freq(v), 2)}%' for k, v in counter.items())
            yield f'{comment.review_id}\t{text_freq}'


def wordFreq_perProd_modifedWeight_lineiter(arr_comments):
    cmp_key = lambda x: (x.customer_id, x.review_date)
    arr_comments.sort(key=cmp_key)
    comments = defaultdict(Counter)
    comments_cnt = Counter()

    for idx, (key, group) in enumerate(groupby(arr_comments, key=lambda x: x.customer_id)):
        for comment in group:
            def get_freq(cnt):
                return 100*(1+idx*WEIGHT_INCREAMENT_PER_LEVEL)*cnt
            counter = Counter(chain.from_iterable(comment.review_body_pcsed))
            comments[key].update(counter)
            comments_cnt[key]+=1

    for prodid, counter in comments:
        text = ';'.join(f'{k}:{round(v/comments_cnt[prodid]),2}' for k, v in counter.items())
        yield f'{prodid}\t{text}'


if __name__ == '__main__':
    RANGE_FROM = date(2013, 1, 1)
    RANGE_TO = date(2015, 12, 31)

    path_dirOfMe = os.path.split(os.path.realpath(__file__))[0]
    arr_title, arr_comment = word_preprocess.main('/'.join(path_dirOfMe.split('\\')[:-1])+"/Dateset/pacifier1.tsv")
    path_output = '/'.join(path_dirOfMe.split('\\')[:-1])+"/Output"
    arr_comment = [comment for comment in arr_comment if RANGE_FROM <= comment.review_date <= RANGE_TO]
    main(arr_title, arr_comment, path_output)
