# -----------------------------------------------------
# Facebook Messenger bot sample by Ricardo Santos.
# Creates a very simple Facebook Messenger bot.
# Uses Facebook Graph API 3.0.
# -----------------------------------------------------

# Dependencies
from flask import Flask, request    # Installation: pip3 install Flask==1.0
import requests                     # Installation: pip3 install requests==2.18.4
from pprint import pprint


# app will be used to create a light web server that will receive the user input 
# (from a FB Messenger client) and respond
app = Flask(__name__)

# The page access token must be generated in Facebook for Developers. 
# This token is required to access Facebook APIs.
ACCESS_TOKEN = 'EAACLY8QmFuoBAOB5tZCy3BcfptdJkZBGLFdCCb2P1CReMYTGreySGlY1w48EO0oN57c4kYaYEzy4G20bnrJzaZA91s9rjCjdV51liyQWiVrdY84lxe37lJLzR3vdInLEYhlNaxwksqFsUkODXgbVIZADemhU1ZCVNZCsxKc3jP34s56xBBwg1ZB'

# This other token is used to verify if any message that reaches the bot
# is an authentic request sent by Facebook. This will protect the bot from
# unauthorized access. You must specify the token in Facebook for Developers,
# when you define the webhook for this bot.
VERIFY_TOKEN = 'AIRoutingBotToken'


@app.route('/', methods=['GET', 'POST'])
def handle_user_input():

  try:
      if request.method == 'GET':
        # Before allowing people to message your bot, Facebook has implemented a verify token
        # that confirms all requests that your bot receives came from Facebook. 
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
      else:    
        # Get whatever message a user sent the bot
        output = request.get_json()
        
        pprint(output)

        for event in output['entry']:
          messaging = event['messaging']
          for message in messaging:
            if message.get('message'):
              text = message['message'].get('text')                

              # Facebook Messenger ID from user so we know where to send response back to
              recipient_id = message['sender']['id']
                                       
              if text:
                print("Received '{0}' from {1}".format(text, recipient_id))
                # Return this message to the user
                response = "Welcome to Appliances of the Future!"
                print("My response: '{}'".format(response))
                send_message(recipient_id, response, True)                
            
  except Exception as e:
      print("Error handling user input: {}".format(e))

  return "My response"


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


if __name__ == '__main__':
    app.run(port=5001, debug=True)
