# -----------------------------------------------------
# AIRouter module by Ricardo Santos.
# Defines the algorithm to select the best agent to
# handle a given interaction with a given customer.
# -----------------------------------------------------

# Dependencies
import numpy as np      # Installation: pip3 install numpy==1.14.3
from TextAnalytics import TextAnalytics
from CRM import CRM
from Agents import Agents
from RankingNetwork import RankingNetwork


class AIRouter(object):
    """ Selects the best human agent to chat with the customer.
        The algorithm, based on recommender systems, is divided in 2 steps:
        1. Candidate generation (selects n candidates from all the agents)
        2. Ranking (ranks the candidates in order to choose the best one for the interaction)
    """

    def __init__(self, crm, agents):
        # Text analytics will be used to detect language, sentiment and intent in user input.
        self.text_analytics = TextAnalytics()

        self.crm = crm
        self.agents = agents
        self.ranking_network = RankingNetwork(self.crm, self.agents)

        # Determines the maximum number of candidates for ranking
        self.max_number_of_candidates = 3


    def generate_candidates(self, language, intent, verbose=False):
        """ Returns a list with a number of candidates (yet to be ranked).
            Candidates are selected according to their skills for handling
            the language and intent of the interaction.
        """
        candidates = []

        en_weight = 0.0
        es_weight = 0.0
        sales_weight = 0.0
        support_weight = 0.0

        if language=="en":
            en_weight = 1.0  # English skill needed
        elif language=="es":
            es_weight = 1.0  # Spanish skill needed

        if intent=="sales":
            sales_weight = 1.0      # Sales skill needed
        elif intent=="support":
            support_weight = 1.0    # Support skill needed

        for agent in self.agents.agents:
            skill_for_the_job = \
                en_weight * agent["en"] + \
                es_weight * agent["es"] + \
                sales_weight * agent["sales"] + \
                support_weight * agent["support"]        
            # In a real case we may want to filter here the unavailable agents
            # (not logged, not ready to work or already busy)
            # or the ones that do not verify some minimum skills
            # In this example we filter only those who have absolutely
            # no skills for the job.
            if skill_for_the_job > 0.:
                candidates.append((agent["agent id"], skill_for_the_job))
         
        # Sort by 'skill_for_the_job' column
        candidates = sorted(candidates, key=lambda entry: entry[1], reverse=True)   

        # We want the first N only
        candidates = candidates[:self.max_number_of_candidates]

        if verbose:
            if len(candidates) == 0:
                print("No candidates found")
            else:
                print("Candidates found:")
                for candidate in candidates:
                    print("{0} (skill for the job = {1})".format(self.agents.get_agent_name(candidate[0]), candidate[1]))

        # Return the agent ids
        return [row[0] for row in candidates]        


    def rank_candidates(self, contact_id, language, sentiment, intent, candidates):
        """ Ranks a list of candidates. 
            Rank is calculated according to customer, agent and interaction features.
            Returns a sorted list of tuples (agent id, score). First has the best score.
        """
        results = self.ranking_network.predict(contact_id, language, sentiment, intent, candidates)

        ranked_candidates = []

        for i in range(len(results)):
            ranked_candidates.append([candidates[i], results[i]])

        return sorted(ranked_candidates, key=lambda entry: entry[1], reverse=True)


    def route_to_best_agent(self, contact_id, question):
        """ Routes the interaction to the best available agent.
            Because this is just a sample we'll not route anything,
            we'll just return a reply saying which agent was selected
            or a default message if no agent could be chosen.
        """

        # Get the contact from the CRM
        contact = self.crm.get_contact_by_id(contact_id)

        # Take a guess at the language
        language = self.text_analytics.guess_language(question, verbose=True)

        # Take a guess at the sentiment
        sentiment = self.text_analytics.guess_sentiment(question, language, verbose=False)

        # Take a guess at the intent
        intent = self.text_analytics.guess_intent(question, language, verbose=True)

        print("Received question from {0}: '{1}'".format(contact["name"], question))
        print("Language={0}, Sentiment={1}, Intent={2}".format(language, sentiment, intent))

        if intent == "other":
            # Intent was not discovered... return a default message in the proper language
            if language == "es":
                return "Perdona {}, pero no te entiendo...".format(contact["name"])
            else:
                return "Sorry {}, I couldn't understand your message...".format(contact["name"])
        else:
            # Generate n candidates to rank
            candidates = self.generate_candidates(language, intent, verbose=True)

            if len(candidates) == 0:
                # No candidates case
                if language=="es":
                    return "Todos los agentes humanos están ocupados en este momento. Por favor espera, tu pregunta será respondida lo más rápido posible."
                else:
                    return "All human agents are busy at this moment. Please wait, your question will be answered as soon as possible."
            else:
                print("Candidates found: predicting success")

                # Predict the success for each candidate
                ranked_candidates = self.rank_candidates(contact_id, language, sentiment, intent, candidates)

                print("The best agents to handle the interaction are:")
                for ranked_candidate in ranked_candidates:
                    print("{0} (predicted success = {1})".format(self.agents.get_agent_name(ranked_candidate[0]), ranked_candidate[1]))

                # Choose the best one
                best_agent = ranked_candidates[0]
                
                ret = ""

                if language=="es":
                    if intent=="sales":
                        department = "ventas"
                    else:
                        department = "soporte"
                    ret = "Transfiriendo a {0}, del departamento de {1}. ¡Encantado de hablar contigo!".format(self.agents.get_agent_name(best_agent[0]), department)
                else:
                    return "Directing to {0}, from {1} department. Nice talking to you!".format(self.agents.get_agent_name(best_agent[0]), intent)

                return ret


    def train(self):
        self.ranking_network.train(500)
