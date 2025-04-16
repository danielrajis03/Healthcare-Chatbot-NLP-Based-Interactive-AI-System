import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.stem import WordNetLemmatizer
import csv
import re
from uuid import uuid4

# nltk downloads
nltk.download('punkt')
nltk.download('wordnet')

# Preprocesses text by tokenization, lemmatization, and removing non-alphabetic characters
def preprocess_text(text):
    lemmatizer = WordNetLemmatizer()
    tokens = nltk.word_tokenize(text.lower())
    tokens = [lemmatizer.lemmatize(token) for token in tokens if token.isalpha()]
    return ' '.join(tokens)

# Loads and returns intents, questions, and answers from given files
def load_data(intents_file, qa_file, healthcare_file):
    with open(intents_file) as file:
        intents = json.load(file)['intents']

    questions, answers = [], []
    # Load general QA data
    with open(qa_file, newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader, None)  # Skip header row
        for row in reader:
            questions.append(row[1])
            answers.append(row[2])

    # Load healthcare-specific questions and answers
    healthcare_questions, healthcare_answers = [], []
    with open(healthcare_file, newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader, None)  # Skip header row
        for row in reader:
            question = row[1]
            answer = row[2]
            healthcare_questions.append(question)
            healthcare_answers.append(answer)

    return intents, questions, answers, healthcare_questions, healthcare_answers

# Vectorizes text data and returns vectorizer, matrix X, and labels for intent recognition
def vectorize_data(intents, questions):
    vectorizer = TfidfVectorizer(ngram_range=(1, 2))  # Using bigrams in addition to unigrams
    labels, patterns = [], []

    for intent in intents:
        for pattern in intent['patterns']:
            labels.append(intent['tag'])
            patterns.append(preprocess_text(pattern))

    all_texts = patterns + questions
    X = vectorizer.fit_transform(all_texts)

    return vectorizer, X, labels

# Define similarity thresholds for intent recognition and question-answering
INTENT_SIMILARITY_THRESHOLD = 0.3  # Adjusted threshold for intents
QA_SIMILARITY_THRESHOLD = 0.15     # Threshold for QA pairs

# Recognizes intent or answers a question based on input text, using cosine similarity
def recognize_intent(input_text, vectorizer, X, labels, questions, answers):
    input_vec = vectorizer.transform([preprocess_text(input_text)])
    similarities = cosine_similarity(input_vec, X).flatten()
    best_match = np.argmax(similarities)
    best_similarity = similarities[best_match]

    if best_match < len(labels):
        if best_similarity < INTENT_SIMILARITY_THRESHOLD:
            return 'unknown', None
        return 'intent', labels[best_match]
    else:
        if best_similarity < QA_SIMILARITY_THRESHOLD:
            return 'unknown', None
        return 'qa', answers[best_match - len(labels)]

# Sets up intent recognition by loading data and vectorizing text
def setup_intent_recognition(intents_file, qa_file, healthcare_file):
    intents, questions, answers, healthcare_questions, healthcare_answers = load_data(intents_file, qa_file, healthcare_file)
    vectorizer, X, labels = vectorize_data(intents, questions + healthcare_questions)
    return vectorizer, X, labels, questions, answers, healthcare_questions, healthcare_answers

# Class to manage user identities
class IdentityManager:
    # Initializes the IdentityManager with an empty dictionary for user data
    def __init__(self):
        self.user_data = {}

    # Extracts a name from the input text and assigns a UUID to the extracted name
    def extract_name(self, text):
        patterns = [
            r"My name is ([\w\s]+)",
            r"I am ([\w\s]+)",
            r"Call me ([\w\s]+)",
            r"You can call me ([\w\s]+)",
            r"My name's ([\w\s]+)",
            r"I'm ([\w\s]+)",
            r"^([\w\s]+)$"
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                user_name = ' '.join(part.capitalize() for part in match.group(1).split())
                user_id = str(uuid4())
                self.user_data[user_id] = user_name
                return user_id

        return None

    # Retrieves the user's name from the stored user data using their unique ID
    def get_user_name(self, user_id):
        return self.user_data.get(user_id, None)

    # Retrieves the user's unique ID from the stored user data using their name
    def get_user_id(self, user_name):
        for id, name in self.user_data.items():
            if name == user_name:
                return id
        return None
