import word_preprocess
import os.path
from itertools import groupby, chain
from collections import namedtuple
from datetime import date
from math import log, exp

WEIGHT_INCREAMENT_PER_LEVEL=0.5
RANGE_FROM = date(2013, 1, 1)
RANGE_TO = date(2015, 12, 31)

DimDate = namedtuple('fDimDate', ['func', 'econ', 'saft', 'beau'])


def main(path_input, path_output, name_files=['pacifier.tsv', 'microwave.tsv', 'hair_dryer.tsv']):
    for name_file in name_files:
        arr_title, arr_comment = word_preprocess.main(f'{path_input}/{name_file}')
        arr_comment = [comment for comment in arr_comment if RANGE_FROM <= comment.review_date <= RANGE_TO]
        wordFourDim_iniDate_calc(arr_comment, name_file[:-4])
        wordFourDim_weighedData_calc(arr_comment)
        arr_product = wordFourDim_product_calc(arr_comment)
        output(arr_comment, arr_product, name_file, path_output)


def wordFourDim_iniDate_calc(arr_comments, product_class):
    for comment in arr_comments:
        comment.posIniDate = [0, 0, 0, 0]
        comment.negIniDate = [0, 0, 0, 0]
        for word in chain.from_iterable(comment.review_body_pcsed):
            print(word)
            idx, val = word_grade(word, product_class)
            if idx >= 0:
                if val > 0:
                    comment.posIniDate[idx] += val
                else:
                    comment.negIniDate[idx] += -val
        comment.posIniDate = DimDate(*comment.posIniDate)
        comment.negIniDate = DimDate(*comment.negIniDate)


def wordFourDim_weighedData_calc(arr_comments):
    e = exp(1)
    assert all(getattr(comment, 'posIniDate', None) for comment in arr_comments)
    assert all(getattr(comment, 'negIniDate', None) for comment in arr_comments)
    arr_comments.sort(key=lambda x: (x.customer_id, x.product_parent, x.review_date))
    for (key, group) in groupby(arr_comments, key=lambda x: (x.customer_id, x.product_parent)):
        for idx, comment in enumerate(group):
            weight = 1
            if comment.verified_purchase == 'n':
                weight *= 0.5
            if comment.vine == 'y':
                weight *= 5
            elif comment.helpful_votes>0 and comment.total_votes>0:
                weight *= 5 * exp(-4.7/(comment.helpful_votes+4.7)) * \
                    log(e*(e-1)*comment.helpful_votes/comment.total_votes+e)
            weight *= 1+idx*WEIGHT_INCREAMENT_PER_LEVEL
            comment.weight = weight


class Product:

    def __init__(self, product_parent):
        self.product_parent = product_parent
        self.arr_comment = []

    def calculate_votes(self):
        assert self.arr_comment
        posIniDate = [0, 0, 0, 0]
        negIniDate = [0, 0, 0, 0]
        for i in range(4):
            posIniDate[i] += sum(comment.posIniDate[i]*comment.weight for comment in self.arr_comment)
            negIniDate[i] += sum(comment.negIniDate[i]*comment.weight for comment in self.arr_comment)
        self.posIniDate = DimDate(*posIniDate)
        self.negIniDate = DimDate(*negIniDate)


def wordFourDim_product_calc(arr_comment):
    parent_toProduct = dict()
    for comment in arr_comment:
        if comment not in parent_toProduct:
            parent_toProduct[comment.product_parent] = Product(comment.product_parent)
        parent_toProduct[comment.product_parent].arr_comment.append(comment)
    for product in parent_toProduct.values():
        product.calculate_votes()
    return list(parent_toProduct.values())


def output(arr_comment, arr_product, name_file, path_output):
    name_file = name_file[:-4]
    file1 = open(f'{path_output}/{name_file}_file1.tsv', 'w')
    file1.write('review_id\tpos_function\tpos_economy\tpos_safty\tpos_beauty\tneg_function\tneg_economy\tneg_safty\tneg_beauty\tweight\n')

    def each_comment(comment):
        pos = '\t'.join(str(val) for val in comment.posIniDate)
        neg = '\t'.join(str(val) for val in comment.negIniDate)
        return f'{comment.review_id}\t'+f'{pos}\t'+f'{neg}\t'+str(round(comment.weight, 2))

    file1.write('\n'.join(each_comment(comment) for comment in arr_comment))
    file1.close()

    file2 = open(f'{path_output}/{name_file}_file2.tsv', 'w')
    file2.write('parduct_parent\tpos_function\tpos_economy\tpos_safty\tpos_beauty\tneg_function\tneg_economy\tneg_safty\tneg_beauty\n')

    def each_product(product):
        pos = '\t'.join(str(val) for val in product.posIniDate)
        neg = '\t'.join(str(val) for val in product.negIniDate)
        return f'{product.product_parent}\t'+f'{pos}\t'+f'{neg}'

    file2.write('\n'.join(each_product(product) for product in arr_product))
    file2.close()


if __name__ == '__main__':
    path_dirOfMe = os.path.split(os.path.realpath(__file__))[0]
    os.chdir(path_dirOfMe)
    from word_fourDim_grade import word_grade
    path_output = '/'.join(path_dirOfMe.split('\\')[:-1])+"/Output"
    path_input = '/'.join(path_dirOfMe.split('\\')[:-1])+"/Dateset"
    main(path_input, path_output)
