'''
extracts the main idea from a blog post/ article
mini summarizer that focuses on key insights

- utilizes sentence_transformers  to understand meaning of sentences
- uses sent_tokenize from nltk to break up article/ blohg into individual sentences
- ranks sentences based on how close they are to the average topic
- return the top 1- 2 most important sentences (thesis)

'''

from sentence_transformers import SentenceTransformer, util
import nltk
from nltk.tokenize import sent_tokenize

# Download the tokenizer (first time only)
nltk.download('punkt')

# Load the sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

def extract_thesis(content: str, top_n: int = 2) -> list[str]:
    '''
    extract the top_n most central sentences from a blog post.
    '''
    sentences = sent_tokenize(content)

    if len(sentences) == 0:
        return []

    if len(sentences) <= top_n:
        return sentences  # return all if fewer than top_n

    # convert to embeddings
    embeddings = model.encode(sentences, convert_to_tensor=True)

    # compute similarity matrix
    cosine_scores = util.pytorch_cos_sim(embeddings, embeddings)

    # centrality = sum of similarities
    centrality_scores = cosine_scores.sum(axis=1)

    # get indices of top_n most central sentences
    top_indices = centrality_scores.argsort(descending=True)[:top_n]

    return [sentences[i] for i in top_indices]
