import json
import indicoio

indicoio.config.api_key = '0955c59916d6cd98d8ddbcbd7aeacd65'

""" Helper Functions """


def load_data(filename):
    """loads JSON data from a file"""
    with open(filename, 'rb') as f:
        return [json.loads(l) for l in f]


def dump_data(filename, data):
    """dumps  JSON data to a file"""
    with open(filename, 'wb') as outfile:
        json.dump(data, outfile)


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i+n]


""" Task 1: Augment Articles with Text Tags to identify Topics """


def add_indico_text_tags(chunk):
    article_texts = [article['content'] for article in chunk]
    text_tags_dicts = indicoio.text_tags(article_texts, threshold=0.1)
    for i in range(len(chunk)):
        text_tag_dict = text_tags_dicts[i]
        chunk[i]['text_tags'] = text_tag_dict.items()
    return chunk


def augment_data():
    data = load_data('articles.ndjson')[0]

    for chunk in chunks(data, 100):
        add_indico_text_tags(chunk)

    with open('indicoed_articles.ndjson', 'wb') as outfile:
        json.dump(data, outfile)


""" Task 2: Choose articles to show a user based on a statement """


def score_by_tag_match(article, interests):
    score = 0
    for article_tag in article['text_tags']:
        for interest_tag in interests:
            if article_tag[0] == interest_tag[0]:
                score += article_tag[1] * interest_tag[1]
    return score


def get_tags(text):
    tag_dict = indicoio.text_tags(text)
    sorted_tags = sorted(tag_dict.items(), key=lambda tup: -tup[1])[:5]
    return sorted_tags


def recommend(user_statement):
    interests = get_tags(user_statement)
    data = load_data('indicoed_articles.ndjson')[0]
    sorted_by_score = sorted(data, key=lambda x: score_by_tag_match(x, interests), reverse=True)
    del sorted_by_score[10:]
    return sorted_by_score


""" Try it out! """


def run():
    augment_data()
    recommended_articles = recommend("I wish I was a painter")
    recommended_titles = [article['title'] for article in recommended_articles]
    print recommended_titles
