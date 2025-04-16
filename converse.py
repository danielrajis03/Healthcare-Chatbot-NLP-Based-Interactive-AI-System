import json
import random
import intent_recognition as ir
from healthcare_booking import HealthcareBooking
import re
import datetime
from uuid import uuid4

# Class to manage conversation context, holding the state and data of the conversation
class ConversationContext:
    def __init__(self):
        self.state = None
        self.data = {}

    # Sets the state of the conversation
    def set_state(self, state):
        self.state = state
        
    # Updates a specific data key-value pair within the conversation
    def update_data(self, key, value):
        self.data[key] = value

    # Retrieves a specific data value by its key
    def get_data(self, key):
        return self.data.get(key)

    # Resets the conversation context (state and data)
    def reset(self, keys_to_retain=[]):
        # Create a temporary dictionary to store the data to be retained
        retained_data = {key: self.data[key] for key in keys_to_retain if key in self.data}

        # Reset state and data
        self.state = None
        self.data.clear()

        # Restore the retained data back into the context
        self.data.update(retained_data)

# Loads response templates from the intents JSON file
def load_responses(intents_file):
    with open(intents_file) as file:
        intents_data = json.load(file)
        responses = {intent['tag']: intent['responses'] for intent in intents_data['intents']}
    return responses

# Global variables to store the components for intent recognition
vectorizer = None
X = None
labels = None
questions = None
answers = None
healthcare_questions = None  
healthcare_answers = None    

# Setup function to initialize global variables for intent recognition
def setup(vect, mat, lbls, qsts, answs, hc_qsts, hc_answs):
    global vectorizer, X, labels, questions, answers, healthcare_questions, healthcare_answers
    vectorizer = vect
    X = mat
    labels = lbls
    questions = qsts
    answers = answs
    healthcare_questions = hc_qsts  
    healthcare_answers = hc_answs

responses = load_responses('intents.json')

# Processes user input and generates a response based on the current context and booking system

def get_response(user_input, context, booking_system, intents):
    global vectorizer, X, labels, questions, answers, healthcare_questions, healthcare_answers

    # Handle user input based on current conversation state
    if context.state is None:
        # Recognize the type and specific tag of the user's intent
        intent_type, response_tag = ir.recognize_intent(
            user_input, 
            vectorizer, 
            X, 
            labels, 
            questions, 
            answers, 
            healthcare_questions, 
            healthcare_answers
        )
        
        if intent_type == 'intent':
            # Respond based on the recognized intent tag
            if response_tag == 'name_query':
                user_name = context.get_data('user_name')
                if user_name:
                    # Fetch the response templates for the 'name_query' intent
                    response_templates = next((item['responses'] for item in intents if item['tag'] == 'name_query'), [])
                    # Choose a random response template
                    response_template = random.choice(response_templates) if response_templates else "I'm not sure of your name yet."
                    # Replace the placeholder with the actual user name
                    response = response_template.replace("{detected_name}", user_name)
                else:
                    response = "I'm not sure of your name yet. Could you tell me your name again?"
                return response, None
            elif response_tag == 'how_are_you':
                context.set_state('responded_how_are_you')
                return "I'm a chatbot, so I don't have feelings, but thanks for asking! How are you?", None
            elif response_tag == 'view_appointments':
                context.set_state('view_appointments')
                return "Ok, I'm going to need your appointment ID first please.", None          
            elif response_tag == 'book_appointment':
                context.set_state('book_appointment')
                return "Wonderful, let's book an appointment. Could you please tell me the type of healthcare service you need? (e.g., general practitioner, dentist, specialist)", None
            elif response_tag == 'cancel_appointment':
                context.set_state('cancel_appointment')
                return "I'm sorry to hear that you'd like to cancel your appointment. Firstly, please provide your appointment ID.", None
            elif response_tag == 'ask_question':
                context.set_state('ask_question')
                return "Please ask a question about our healthcare professionals.", None
            else:
                return random.choice(responses.get(response_tag, ["I'm not sure how to respond to that, could you rephrase that?"])), None
        elif intent_type == 'qa':
            if response_tag in healthcare_answers:
                return response_tag, None
            else:
                return response_tag, None
        elif intent_type == 'unknown':
            return "I'm sorry, I didn't understand that. Could you rephrase or ask something else?", None
    # Handling responses based on the current state of the conversation  
    else:
        # Special handling for empty string in specific states
        if user_input == "":
            if context.state == "book_appointment":
                return "Wonderful, let's book an appointment. Could you please tell me the type of healthcare service you need?", None
            elif context.state == "view_appointments":
                return "Ok, I'm going to need your appointment ID first please.", None
            elif context.state == "cancel_appointment":
                return "I'm sorry to hear that you'd like to cancel your appointment. Firstly, please provide your appointment ID.", None
            elif context.state == "ask_question":
                return "Please ask a question about our healthcare professionals.", None

        # Handle state-based response for non-empty input
        state_response = handle_state_based_response(user_input, context, booking_system)
        if state_response is not None:
            return state_response
        else:
            return "I'm sorry, something went wrong. Could you try again?", None

# Handles user input based on the current state in a state-based conversation
def handle_state_based_response(user_input, context, booking_system):
    # View appointments state: handle requests to view appointment details
    if context.state == 'view_appointments':
        appointment_id = user_input.strip()  # Assuming the user inputs the appointment ID

        if appointment_id.isdigit() and booking_system.appointment_exists(appointment_id):
            appointment = booking_system.get_appointment_by_id(appointment_id)
            if appointment:
                # Format the appointment details
                formatted_appointment = f"Here are your appointment details for Appointment ID({appointment[0]}): Service: {appointment[2]}, Date: {appointment[3]}, Time: {appointment[4]}, Doctor: {appointment[5]}"
                context.set_state(None)  # Reset state after viewing
                return formatted_appointment, None
            else:
                return "Appointment details not found for the provided ID. Please enter a valid appointment ID:", 'view_appointments'
        else:
            return "Invalid appointment ID. Please enter a valid appointment ID:", 'view_appointments'

    # Cancel appointment state: handle requests to cancel an appointment
    if context.state == 'cancel_appointment':
        if 'appointment_id' not in context.data:
            appointment_id = user_input.strip()  # Assuming the user inputs the appointment ID

            if appointment_id.isdigit() and booking_system.appointment_exists(appointment_id):
                appointment = booking_system.get_appointment_by_id(appointment_id)
                if appointment:
                    # Format the appointment details
                    formatted_appointment = f"Here are your appointment details for Appointment ID({appointment[0]}): Service: {appointment[2]}, Date: {appointment[3]}, Time: {appointment[4]}, Doctor: {appointment[5]}"
                    context.update_data('appointment_id', appointment_id)
                    return formatted_appointment + "\nWould you like to proceed with cancelling this appointment? (yes/no)", 'cancel_appointment'
                else:
                    return "Appointment details not found for the provided ID. Please enter a valid appointment ID:", 'cancel_appointment'
            else:
                return "Invalid appointment ID. Please enter a valid appointment ID:", 'cancel_appointment'
        else:
            if user_input.lower() == 'yes':
                appointment_id = context.get_data('appointment_id')
                success, message = booking_system.cancel_appointment(appointment_id)
                if success:
                    context.set_state(None)
                    return f"Your appointment with ID({appointment_id}) has been successfully cancelled.", None
                else:
                    return message, 'cancel_appointment'
            elif user_input.lower() == 'no':
                context.set_state(None)
                return "Cancellation process has been aborted. Is there anything else I can help you with?", None
            else:
                return "Please respond with 'yes' or 'no' to proceed with the cancellation.", 'cancel_appointment'

    # Responded to 'how are you': handle responses to the bot's wellbeing inquiry
    if context.state == 'responded_how_are_you':
        # Look for keywords indicating positive or negative sentiment
        positive_keywords = ['good', 'great', 'well', 'fantastic', 'happy', 'ecstatic']
        negative_keywords = ['bad', 'sad', 'unhappy', 'terrible', 'not well', 'not great', 'not good', 'down']

        # Check for positive sentiment
        if any(word in user_input.lower() for word in positive_keywords):
            response = "That's wonderful to hear!"
        # Check for negative sentiment
        elif any(word in user_input.lower() for word in negative_keywords):
            response = "I'm sorry to hear that, hopefully you'll feel better soon. If your symptoms are severe, please consider calling 999 for immediate assistance."
        # Neutral or unclear sentiment
        else:
            response = "Thanks for sharing."

        context.set_state(None)  # Reset state after handling
        return response, None

    # Ask question about healthcare professionals
    if context.state == 'ask_question':
        answer = handle_healthcare_question(user_input)
        context.set_state(None)
        return answer, None

    # Book appointment state: guide through the appointment booking process
    if context.state == 'book_appointment':
        if 'service_type' not in context.data:
            context.update_data('service_type', user_input.title())
            return "Great! What date would you like to book the appointment for? (in DD-MM-YYYY format)", None
        elif 'appointment_date' not in context.data:
            # Extract the date from user input
            match = re.search(r'\b(\d{2}-\d{2}-\d{4})\b', user_input)
            if match:
                date_str = match.group(1)
                try:
                    # Validate/format date (DD-MM-YYYY)
                    appointment_date = datetime.datetime.strptime(date_str, '%d-%m-%Y').date()
                    current_date = datetime.datetime.now().date()
                    # Check if the entered date is not in the past
                    if appointment_date < current_date:
                        return "Sorry, you cannot book an appointment for a past date. Please enter a future date.", None
                    context.update_data('appointment_date', appointment_date.strftime('%d-%m-%Y'))
                    return "What time would you like the appointment? (in HH:MM format)", None
                except ValueError:
                    return "Sorry, that's an invalid date format. Please enter the date in DD-MM-YYYY format.", None
            else:
                return "Sorry, that's an invalid date format. Please enter the date in DD-MM-YYYY format.", None
        elif 'appointment_time' not in context.data:
            # Extract time from user input
            match = re.search(r'\b(\d{2}:\d{2})\b', user_input)
            if match:
                time_str = match.group(1)
                try:
                    # Validate/format time (HH:MM)
                    appointment_time = datetime.datetime.strptime(time_str, '%H:%M').time()
                    context.update_data('appointment_time', appointment_time.strftime('%H:%M'))
                    user_id = context.get_data('user_id') or str(uuid4())
                    context.update_data('user_id', user_id)
                    full_name = context.get_data('full_name') or "Guest User"
                    success, message, appointment_id = booking_system.book_appointment(
                        user_id, context.get_data('appointment_date'), context.get_data('appointment_time'),
                        context.get_data('service_type'), full_name)
                    
                    if success:
                        response_message = f"{message} Your appointment is confirmed. Take care!"
                        context.reset()
                        context.update_data('user_id', user_id)
                        return response_message, None
                    else:
                        return message, None
                except ValueError:
                    return "Sorry, that's an invalid time format. Please enter the time in HH:MM format.", None
            else:
                return "Sorry, that's an invalid time format. Please enter the time in HH:MM format.", None

# Function to handle questions about healthcare professionals based on the CSV file
def handle_healthcare_question(question):
    # A function to search the healthcare information and return a relevant answer
    # Placeholder response, should be replaced with logic to parse the CSV and answer questions accordingly
    return "I'm not sure about that yet, but I'm learning more about our healthcare professionals every day."

