# -----------------------------------------------------
# Example of an AI-powered routing bot capable of
# detecting the language, sentiment and intent of
# a customer question (using machine learning cloud services)
# and select the best agent according to customer profile, 
# history and agent info (using a deep learning model).
#
# By Ricardo Santos, 2018
# -----------------------------------------------------


# Dependencies
import sys
import random
from flask import Flask, request    # Installation: pip3 install Flask==1.0
import requests                     # Installation: pip3 install requests==2.18.4
from pprint import pprint
from TextAnalytics import TextAnalytics
from AIRouter import AIRouter
from CRM import CRM
from Agents import Agents


# We start by creating our bot endpoint.

# app will be used to create a light web server that will receive the user input 
# (from a FB Messenger client) and respond
app = Flask(__name__)

# The page access token must be generated in Facebook for Developers. 
# This token is required to access Facebook APIs.
ACCESS_TOKEN = 'Your access token'

# This other token is used to verify if any message that reaches the bot
# is an authentic request sent by Facebook. This will protect the bot from
# unauthorized access. You must specify the token in Facebook for Developers,
# when you define the webhook for this bot.
VERIFY_TOKEN = 'AIRoutingBotToken'


# Our bot will not have complex flows with a real authentication phase...
# For the sake of simplicity, the conversation will have 3 stages only,
# one to start a conversation, one for asking the contact id and 
# a last one to receive the question from the user.
waiting_for_greeting = 0
waiting_for_contact_id = 1
waiting_for_question = 2


# Text analytics will be used to detect the language of the user input.
text_analytics = TextAnalytics()


class ConversationContext(object):
    """ 
        Here we'll keep the contact id from the user
        (if contact_id >= 0, the user is registered in our CRM)
        and the conversation stage.
    """

    def __init__(self):
        self.reset()

    def reset(self):        
        self.contact_id = -1
        self.language = "en"        
        self.conversation_stage = waiting_for_greeting


# Here we'll keep the connections context. 
# Each connection is an association between a FB recipient id (the user)
# and a conversation context.
connections_context = {}


def get_connection_context(recipient_id):
    global connections_context
    if recipient_id in connections_context:
        return connections_context[recipient_id]
    else:
        connections_context[recipient_id] = ConversationContext()
        return connections_context[recipient_id]


# Let's create our small "CRM" and our agents
crm = CRM()
agents = Agents()

# Let's create a AIRouter object to handle the routing part
router = AIRouter(crm, agents)

# We will receive messages that Facebook Messenger sends to our bot at this endpoint
@app.route('/', methods=['GET', 'POST'])
def handle_user_input():    
    
    print("Handling user input....")

    try:
        if request.method == 'GET':
            # Before allowing people to message your bot, Facebook has implemented a verify token
            # that confirms all requests that your bot receives came from Facebook. 
            token_sent = request.args.get("hub.verify_token")
            return verify_fb_token(token_sent)
        # If the request was not GET, it must be POST and we can just proceed with sending a message 
        # back to the user
        else:
            # Get whatever message a user sent the bot
           output = request.get_json()
           for event in output['entry']:
              messaging = event['messaging']
              for message in messaging:
                if message.get('message'):
                    text = message['message'].get('text')                

                    # Facebook Messenger ID from user so we know where to send response back to
                    recipient_id = message['sender']['id']
                                       
                    if text:
                        print("User {0} sent '{1}'".format(recipient_id, text))

                        # Get the context of this interaction
                        context = get_connection_context(recipient_id)
                        
                        # React according to the conversation stage                                               
                        if context.conversation_stage == waiting_for_greeting:                            
                            # Detect language
                            context.language = text_analytics.guess_language(text, verbose=False)                            
                            
                            if context.language=='es':
                                # Start by asking the contact id
                                send_message(recipient_id, "¡Bienvenido a Appliances of the Future! Usted está hablando con un chatbot. ¿Cuál es tu número de cliente?") 
                            else:
                                # Any language that is not spanish will default to english
                                context.language=='en'
                                # Start by asking the contact id
                                send_message(recipient_id, "Welcome to Appliances of the Future! You're talking to a chatbot. What is your customer number?") 
                            
                            context.conversation_stage = waiting_for_contact_id
                        elif context.conversation_stage == waiting_for_contact_id:
                            # Does the input contain the customer id?
                            id = get_number_from_text(text)                            
                            if id >= 0:
                                contact = crm.get_contact_by_id(id)
                                if not contact is None:
                                    # Contact identified, let's keep it and move on
                                    context.contact_id = id
                                    if context.language=='es':
                                        send_message(recipient_id, "Ola {}, ¿como puedo ayudarte? Por favor haz tu pregunta.".format(contact["name"]))                                         
                                    else:
                                        send_message(recipient_id, "Hi {}, how can I help you? Please state your question.".format(contact["name"])) 
                                    context.conversation_stage = waiting_for_question
                                else:
                                    if context.language=='es':
                                        send_message(recipient_id, "Lo siento, no estás registrado en el sistema. Por favor, registrate primero.")                                        
                                    else:
                                        send_message(recipient_id, "I'm sorry, you're not registered in the system. Please sign up first.")
                                    context.conversation_stage = waiting_for_greeting
                            else:
                                if context.language=='es':
                                    send_message(recipient_id, "Por favor ingrese un número valido...")
                                else:
                                    send_message(recipient_id, "Please enter a valid number...")
                        else:
                            # Handle the user question now, routing it to the best agent                            
                            response_text = router.route_to_best_agent(context.contact_id, text)
                            send_message(recipient_id, response_text)
                            # Done with this contact - reset flow                            
                            context.conversation_stage = waiting_for_greeting

    except Exception as e:
        print("Error handling user input: {}".format(e))

    return "Message processed"


def verify_fb_token(token_sent):
    """ Take token sent by facebook and verify it matches the verify token you sent
    if they match, allow the request, else return an error 
    """
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")

    return 'Invalid verification token'



def send_message(recipient_id, message, verbose=False):
    '''Send text message to the specified recipient.
    https://developers.facebook.com/docs/messenger-platform/send-api-reference/text-message
    Input:
        recipient_id: recipient id to send to
        message: message to send
    Output:
        Response from API as <dict>
    '''
    params = {
        "access_token": ACCESS_TOKEN
    }    
    payload = {        
        'messaging_type': 'RESPONSE',
        'recipient': {
            'id': recipient_id
        },
        'message': {
            'text': message
        }        
    }
    response  = requests.post("https://graph.facebook.com/v3.0/me/messages", params=params, json=payload)
    result = response.json()

    if verbose:
        print("send_message result:")
        pprint(result)

    return result



def get_number_from_text(text):
    """
    Get the first number in the text. 
    Used to get the contact id from the user input.
    """
    ret = -1
    for s in text.split():
        if s.isdigit():
            ret = int(s)
            break
    return ret


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1]=="-train":
        router.train()
    else:
        app.run(port=5001, debug=True)



