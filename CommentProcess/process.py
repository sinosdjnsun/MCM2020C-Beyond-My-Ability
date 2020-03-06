import os.path
import re
from datetime import date
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

class Comment:

    wnl=WordNetLemmatizer()
    stop=set(stopwords.words('english'))

    def __init__(self, text: str):
        arr = text.split('\t')
        self.marketplace = arr[0].lower()
        self.customer_id = arr[1]
        self.review_id = arr[2]
        self.product_id = arr[3]
        self.product_parent = arr[4]
        self.product_title = arr[5]
        self.product_category = arr[6]
        self.star_rating = int(arr[7])
        self.helpful_votes = int(arr[8])
        self.total_votes = int(arr[9])
        self.vine = arr[10].lower()
        self.verified_purchase = arr[11].lower()
        self.review_headline = arr[12]
        self.review_body = arr[13]
        arr_datePart = list(map(int, arr[14].split('/')))
        arr_datePart.insert(0, arr_datePart.pop())
        self.review_date = date(*arr_datePart)
        self.preprocessing_comment()

    def preprocessing_comment(self):
        # Remove not text part
        review_body_pcsed = re.sub(r'[^\x00-\x7F]', '', self.review_body)
        review_body_pcsed = re.sub(r'\<[\S\s]+\>', ' ', review_body_pcsed)
        review_body_pcsed = re.sub(r'[-\+\/\\\*$\%\^&@#(&#34;)"\']', '', review_body_pcsed)
        review_body_pcsed = re.sub(r'[\(\)\[\]\{\}]', '.', review_body_pcsed)
        # split into words and convert to lowercase
        lines = re.split(r'[\.!\?:;\|~,]', review_body_pcsed)
        # Remove stop words
        lines = [[word.lower() for word in line.split(' ') \
                  if word and word.lower() not in self.stop] for line in lines]
        lines = [line for line in lines if line]
        # Lemmatization
        lines = list(list(map(self.wnl.lemmatize, line)) for line in lines)

        self.review_body_pcsed = lines


def main(path_flieToRead):
    file = open(path_flieToRead, 'r', encoding='utf-8')
    arr_title = file.readline()[:-1].split('\t')
    arr_comment = [Comment(text) for text in file.read().split('\n')[:-1]]
    print(arr_title)
    print('\n'.join(str(comment.review_body_pcsed) for comment in arr_comment[:30]))


if __name__ == '__main__':
    path_dirOfMe = os.path.split(os.path.realpath(__file__))[0]
    main('/'.join(path_dirOfMe.split('\\')[:-1])+"/Dateset/pacifier1.tsv")
