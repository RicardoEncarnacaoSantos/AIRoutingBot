# -----------------------------------------------------
# Text analytics module by Ricardo Santos.
# Guesses the language, sentiment and intent of user input.
# APIs used: Microsoft Language API, Microsoft Sentiment API 
# and Microsoft LUIS.
# -----------------------------------------------------

# Dependencies
import requests             # Installation: pip3 install requests==2.18.4
from pprint import pprint



class TextAnalytics(object):
    """ Uses Microsoft Text Analytics and Microsoft LUIS
        to extract relevant content from the user input.
    """

    def __init__(self):
        # Needed for Microsoft Text Analytics services
        self.text_analytics_subscription_key = "Replace by your Text Analytics subscription key"
        self.text_analytics_base_url = "https://westeurope.api.cognitive.microsoft.com/text/analytics/v2.0/"

        # Needed for Microsoft Language Understanding (LUIS) service        
        self.LUIS_subscription_key = "Replace by your LUIS subscription key"
        self.LUIS_en_base_url = "Replace by your LUIS endpoint for English text" # ex: https://westeurope.api.cognitive.microsoft.com/luis/v2.0/apps/xxxxx
        self.LUIS_es_base_url = "Replace by your LUIS endpoint for Spanish text" # ex: https://westeurope.api.cognitive.microsoft.com/luis/v2.0/apps/yyyyy


    def guess_language(self, text, verbose=False):
        """ Guesses the language of a given text.
            Returns the ISO-6391 identifier of the language ("en" or "es"). 
        """

        language_api_url = self.text_analytics_base_url + "languages"

        documents = { 'documents': [
            { 'id': '1', 'text': text },    
        ]}

        headers   = {"Ocp-Apim-Subscription-Key": self.text_analytics_subscription_key}
        response  = requests.post(language_api_url, headers=headers, json=documents)
        languages = response.json()
    
        try:         
            ret = languages["documents"][0]["detectedLanguages"][0]["iso6391Name"]
        except Exception as e:
            print("Error in guess_language: {}".format(e))
            ret = ""

        if verbose:
            print("Language API return for input '{}':".format(text))
            pprint(languages)        

        # We'll only support 2 languages: "en" and "es"
        # Catalan will default to "es"
        if ret=="ca":
            ret = "es"
        # Any other language will default to "en"
        if not ret=="es" and not ret=="en":
            ret = "en"

        if verbose:
            print("guess_language returning '{}'".format(ret))

        return ret


    def guess_sentiment(self, text, language, verbose=False):
        """ Guesses the sentiment of a given text.
            Returns a number from 0 (negative sentiment) to 1 (positive sentiment). 
        """

        sentiment_api_url = self.text_analytics_base_url + "sentiment"

        documents = { 'documents': [
            { 'id': '1', 'language': language, 'text': text }
        ]}

        headers   = {"Ocp-Apim-Subscription-Key": self.text_analytics_subscription_key}
        response  = requests.post(sentiment_api_url, headers=headers, json=documents)
        sentiments = response.json()
    
        try:         
            ret = sentiments["documents"][0]["score"]
        except Exception as e:
            print("Error in guess_sentiment: {}".format(e))
            ret = 0.5

        if verbose:
            print("Sentiment API return for input '{0}' in language '{1}':".format(text, language))
            pprint(sentiments)        
            print("guess_sentiment returning '{}'".format(ret))

        return ret


    def guess_intent(self, text, language, verbose=False):
        """ Guesses the intent of a given text.
            Returns the intent: "sales", "support" or "other". 
            Note: this method uses Microsoft LUIS to extract the intent,
            which in turn must be configured and trained manually in the LUIS website
            (the european version https://eu.luis.ai/home was used in this sample).
        """

        headers = {
            # Request headers
            'Ocp-Apim-Subscription-Key': self.LUIS_subscription_key,
        }

        params ={
            # Query parameter
            'q': text,
            # Optional request parameters, set to default values
            'timezoneOffset': '0',
            'verbose': 'true',
            'spellCheck': 'false',
            'staging': 'false',
        }

        ret = "other"

        try:
            if language=="es":
                # Spanish culture
                response = requests.get(self.LUIS_es_base_url, headers=headers, params=params)
                intents = response.json()                       
                top_scoring_intent = intents["topScoringIntent"]
                if top_scoring_intent["intent"] == "Ventas":
                    ret = "sales"
                if top_scoring_intent["intent"] == "Soporte":
                    ret = "support"        
                score = top_scoring_intent["score"]
                if score < 0.4:
                    # Return "other" if there is not enough confidence on any known intent...
                    ret = "other"
            else:
                # English culture
                response = requests.get(self.LUIS_en_base_url, headers=headers, params=params)
                intents = response.json()                       
                top_scoring_intent = intents["topScoringIntent"]
                if top_scoring_intent["intent"] == "Sales":
                    ret = "sales"
                if top_scoring_intent["intent"] == "Support":
                    ret = "support"        
                score = top_scoring_intent["score"]
                if score < 0.4:
                    # Return "other" if there is not enough confidence on any known intent...
                    ret = "other"
        except Exception as e:
            print("Error in guess_intent: {}".format(e))
            ret = "other"

        if verbose:
            print("LUIS return for input '{}':".format(text))
            pprint(intents)        
            print("guess_intent returning '{}'".format(ret))

        return ret




