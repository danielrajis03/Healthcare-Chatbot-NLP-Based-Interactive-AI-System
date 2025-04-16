import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.stem import WordNetLemmatizer
import csv

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
            questions.append(preprocess_text(row[1]))
            answers.append(row[2])

    # Load healthcare-specific questions and answers
    healthcare_questions, healthcare_answers = [], []
    with open(healthcare_file, newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader, None)  # Skip header row
        for row in reader:
            question = preprocess_text(row[1])
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

#model is then trained on model and questions with fit_transform

    all_texts = patterns + questions
    X = vectorizer.fit_transform(all_texts)

    return vectorizer, X, labels

# Define similarity thresholds for intent recognition and question-answering
INTENT_SIMILARITY_THRESHOLD = 0.25  # Adjusted threshold for intents to be more inclusive
QA_SIMILARITY_THRESHOLD = 0.2       # Threshold for QA pairs

# Recognizes intent or answers a question based on input text, using cosine similarity
def recognize_intent(input_text, vectorizer, X, labels, questions, answers, healthcare_questions, healthcare_answers):
    preprocessed_input = preprocess_text(input_text)
    input_vec = vectorizer.transform([preprocessed_input])
    # calculates the similarity betqeen user input and whateevr is in X
    similarities = cosine_similarity(input_vec, X).flatten()
    best_match = np.argmax(similarities)
    best_similarity = similarities[best_match]

    num_labels = len(labels)
    num_questions = len(questions)

    # Prioritize intents over QA pairs when they are above the similarity threshold
    if best_match < num_labels and best_similarity >= INTENT_SIMILARITY_THRESHOLD:
        return 'intent', labels[best_match]

    # Otherwise, handle QA pairs
    if best_match < num_labels + num_questions:
        # It's a general QA match
        if best_similarity >= QA_SIMILARITY_THRESHOLD:
            return 'qa', answers[best_match - num_labels]
    else:
        # It's a healthcare QA match
        if best_similarity >= QA_SIMILARITY_THRESHOLD:
            return 'qa', healthcare_answers[best_match - num_labels - num_questions]

    # If no suitable match is found
    return 'unknown', None

# Sets up intent recognition by loading data and vectorizing text
def setup_intent_recognition(intents_file, qa_file, healthcare_file):
    intents, questions, answers, healthcare_questions, healthcare_answers = load_data(intents_file, qa_file, healthcare_file)
    vectorizer, X, labels = vectorize_data(intents, questions + healthcare_questions)
    return vectorizer, X, labels, questions, answers, healthcare_questions, healthcare_answers
