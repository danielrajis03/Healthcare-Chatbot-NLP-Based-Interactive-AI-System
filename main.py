import converse
import identity_management as idm
import intent_recognition as ir
from healthcare_booking import HealthcareBooking
import datetime
import json


# Function to return a time-based greeting based on the current hour
def get_time_based_greeting():
    current_hour = datetime.datetime.now().hour
    if 5 <= current_hour < 12:
        return "Good morning"
    elif 12 <= current_hour < 17:
        return "Good afternoon"
    else:
        return "Good evening"


# Main function to run the chatbot
def main():

    # Set up for intent recognition
    vectorizer, X, labels, questions, answers, healthcare_questions, healthcare_answers = ir.setup_intent_recognition('intents.json', 'qa_dataset.csv', 'healthcare_info.csv')

    # Initialize the booking system
    booking_system = HealthcareBooking('healthcare_bookings.db')

    with open('intents.json') as file:
        intents = json.load(file)['intents']

    # Set up conversation context with intent recognition details
    converse.setup(vectorizer, X, labels, questions, answers, healthcare_questions, healthcare_answers)
    identity_manager = idm.IdentityManager()

    # Initialize conversation context
    context = converse.ConversationContext()

    # Get and display time-based greeting
    time_based_greeting = get_time_based_greeting()
    print(f"{time_based_greeting}, welcome to Nottingham Healthcare Services. Firstly, could I take your name?")

    user_greeted = False  # Flag to check if user has been greeted

    # Main loop to handle user input
    while True:
        user_input = input("You: ").strip()

        # Handle exit commands
        if user_input.lower() == 'quit' or user_input.lower() == 'exit':
            print("Healthcare Bot: Goodbye! Take care of your health.")
            break

        # Greet user and extract name only once per session
        if not user_greeted and not context.data.get('user_id'):
            user_id = identity_manager.extract_name(user_input)
            if user_id:
                user_name = identity_manager.get_user_name(user_id)
                context.update_data('user_id', user_id)
                context.update_data('user_name', user_name)
                print(f"Healthcare Bot: Greetings, {user_name}! I'm here to assist with your healthcare needs. You can ask me any questions or choose from the options below:\n"
                      "  1. Book an Appointment\n"
                      "  2. View Appointments\n"
                      "  3. Cancel an Appointment\n"
                      "  4. Ask a question about our healthcare professionals\n"
                      "Just type the number of the option you'd like to select.")
                user_greeted = True
                continue

        # Menu selection based on user input
        if context.state is None and user_input in ["1", "2", "3", "4"]:
            if user_input == "1":
                context.set_state("book_appointment")
            elif user_input == "2":
                context.set_state("view_appointments")
            elif user_input == "3":
                context.set_state("cancel_appointment")
            elif user_input == "4":
                context.set_state("ask_question")
            response, context_state = converse.get_response("", context, booking_system, intents)
        else:
            response, context_state = converse.get_response(user_input, context, booking_system, intents)

        # Handle transactional dialogue if context state is set
        if context_state:
            handle_transactional_dialogue(response, context_state, context, booking_system)
        else:
            print(f"Healthcare Bot: {response}")
            if not context.state:
                print("Healthcare Bot: Is there anything else I can help with, or would you like to type 'exit' to leave?")


# Function to handle transactional dialogue based on context state
def handle_transactional_dialogue(response, context_state, context, booking_system):
    while context.state:
        if isinstance(response, tuple):
            prompt, _ = response
        else:
            prompt = response

        print(f"Healthcare Bot: {prompt}")

        user_input = input("You: ").strip()
        response, _ = converse.handle_state_based_response(user_input, context, booking_system)

        if not context.state:
            print("Healthcare Bot: Is there anything else I can help with, or would you like to type 'exit' to leave?")
            context.reset(keys_to_retain=['user_name'])


# Run the main function if the script is executed
if __name__ == "__main__":
    main()
