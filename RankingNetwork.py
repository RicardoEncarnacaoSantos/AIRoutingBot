# -----------------------------------------------------
# RankingNetwork module by Ricardo Santos.
# Defines a deep learning model to predict the success
# of an agent handling an interaction, 
# based on agent, customer and interaction info.
# -----------------------------------------------------


# Dependencies
import numpy as np                          # Installation: pip3 install numpy==1.14.3
import tensorflow as tf                     # Installation: pip3 install tensorflow==1.8.0
from keras.models import Sequential, Model  # Installation: pip3 install keras==2.1.6
from keras.layers.normalization import BatchNormalization
from keras.layers import Dense, Dropout
from CRM import CRM
from Agents import Agents
from Geocoding import get_GPS_coordinates


class RankingNetwork(object):
    """ Defines an artificial neural network than predicts the 
        success of an agent handling an interaction.
        Used to rank agents.
    """

    def __init__(self, crm, agents):
        self.input_size = 11
        self.crm = crm
        self.agents = agents
        self.model = self.create_network()
        try:
            # Loads weights from a trained network, if available
            self.model.load_weights("weights.h5")
            print("Weights loaded")
        except:
            pass
        self.graph = tf.get_default_graph()


    def create_network(self):
        """ Creates the neural network. 
        """
        model = Sequential()

        model.add(Dense(50, input_shape=(self.input_size,), activation="relu"))
        model.add(BatchNormalization())
        model.add(Dense(35, activation="relu")) 
        model.add(Dropout(0.15))       
        model.add(Dense(20, activation="relu"))
        model.add(Dense(1))

        model.compile(optimizer='adam', loss='mse', metrics=['mae', 'mse'])

        return model


    def build_language_embedding(self, language):
        """ Generates an embedding (vector) for the language.
            Because this is an example and we have 2 languages only,
            we'll keep things simple and hardcode small vectors.
            With more languages, an alternative would be to use the 
            HashingVectorizer from the scikit-learn package.
        """
        if language == "en":
            return [0,1]
        elif language == "es":
            return [1,0]
        else:
            return [0,0]


    def build_category_embedding(self, category):
        """ Generates an embedding (vector) for the category.
            Because this is an example and we have 2 languages only,
            we'll keep things simple and hardcode small vectors.
            With more categories, an alternative would be to use the 
            HashingVectorizer from the scikit-learn package.
        """
        if category == "sales":
            return [0,1]
        elif category == "support":
            return [1,0]
        else:
            return [0,0]


    def build_input_sample(self, contact_id, language, sentiment, category, agent_id):
        """ Assembles all the info into a sample (vector) to feed the network.
        """
        sample = []

        # contact info: id, age, GPS coordinates (approximate latitude and longitude of the postal code)

        contact = self.crm.get_contact_by_id(contact_id)
        sample = [contact_id, contact["age"]]
        if not "GPS" in contact:
            # We get the GPS coordinates once per contact for performance reasons
            contact["GPS"] = get_GPS_coordinates(contact["postal code"])
        sample = sample + contact["GPS"]
              
        # interaction info: language, sentiment, category
        # language and category are text fields and we must convert them to vectors
        # (embeddings)

        sample = sample + self.build_language_embedding(language)
        sample.append(sentiment)
        sample = sample + self.build_category_embedding(category)

        # agent info: id, language skill (the one that matches the interaction language)

        agent = self.agents.get_agent_by_id(agent_id)
        if language=="en":
            language_skill = agent["en"]
        elif language=="es":
            language_skill = agent["es"]
        else:
            language_skill = 0.0
        sample += [agent_id, language_skill]

        return sample        


    def predict(self, contact_id, language, sentiment, category, candidates):
        """ Makes a prediction of success for all the candidates.
        """
        with self.graph.as_default():
            # Let's first assemble the input data
            x = []  # Input data

            print("Creating the input vectors...")

            for candidate in candidates:
                sample = self.build_input_sample(
                    contact_id,
                    language,
                    sentiment,
                    category,
                    candidate)
                x.append(sample)

            x = np.array(x)

            print("Predicting...")

            results = self.model.predict(x)

            print("Done")

            return results


    def train(self, epochs):
        """ Trains the network with the crm data. 
        """
        # Let's first assemble the training set to feed the network
        x = []  # Input data
        y = []  # Labels

        print("Creating the training dataset...")

        for interaction in self.crm.history:
            sample = self.build_input_sample(
                interaction["contact id"], 
                interaction["language"], 
                interaction["sentiment"], 
                interaction["category"], 
                interaction["handled by"])
            x.append(sample)
            y.append(interaction["score"])

        x = np.array(x)
        y = np.array(y) 

        print("Training for {} epochs".format(epochs))

        # Train for n epochs
        results = self.model.fit(x=x, y=y, epochs=epochs, batch_size=32)
        
        print("Model is trained")

        # Saves weights (network state after training)
        # to be loaded on future executions
        self.model.save_weights("weights.h5")


