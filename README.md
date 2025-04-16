# 🏥 Healthcare Chatbot – NLP-Based Interactive AI System #
An intelligent, conversational AI system designed to assist patients with healthcare-related queries, appointment management, and general information retrieval. This chatbot leverages Natural Language Processing (NLP) techniques like TF-IDF vectorization and cosine similarity to deliver context-aware, human-like interactions with a focus on usability, personalisation, and efficient healthcare access.

# 🚀 Features #

Intent Recognition: Understands user queries (e.g., booking, cancellation, FAQs) using TF-IDF and cosine similarity.

Appointment Management: Books, views, and cancels appointments via a robust SQLite backend.

Identity Management: Assigns UUIDs and uses name extraction for personalised dialogue.

Information Retrieval: Answers healthcare-related questions using a structured CSV dataset.

Small Talk: Engages in light conversation to make interactions more natural.

State-Based Dialogue: Maintains context across sessions using structured conversational flow.

Error Handling: Handles ambiguous queries gracefully with fallback prompts.

Usability & Performance Tested: Achieved 88% intent accuracy and positive CUQ scores.

# 🛠️ Technologies Used #
Python

Natural Language Processing (TF-IDF, cosine similarity)

SQLite for persistent appointment data

Regex for name extraction

CSV for FAQ and healthcare data

# 📁 Project Structure
main.py – Entry point for the chatbot

converse.py – Core conversation logic and flow management

intent_recognition.py – Intent detection using NLP

healthcare_booking.py – Appointment management (book/view/cancel)

identity_management.py – Handles UUIDs and name personalisation

intents.json – Predefined small talk and task-based intents

healthcare_info.csv – Dataset of healthcare professionals/services

qa_dataset.csv – FAQs used in information retrieval

healthcare_bookings.db – SQLite database storing appointments

# Author
Daniel Duru-Rajis



