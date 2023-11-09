import math
import pickle
import yaml

class Markov(object):
    def __init__(self):
        with open('app/Gibberish_Detector/utils/markov_characters.yaml', 'r') as yaml_file:
            yaml_data = yaml.safe_load(yaml_file)
            
        self.accepted_chars = yaml_data['markov_characters']
        self.pos = {char: idx for idx, char in enumerate(self.accepted_chars)}
        self.gibberish_model = pickle.load(open('app/Gibberish_Detector/utils/markov_model.pki', 'rb'))

    def normalize(self, sentence: str) -> list:
        """
        Normalize the sentence by returning only the subset of characters from the accepted characters string.

        Parameters:
        - line (str): The sentence to normalize.

        Returns:
        - list: The normalized sentence.
        """
        return [c.lower() for c in sentence if c.lower() in self.accepted_chars]

    def ngram(self, n: int, sentence: str) -> iter:
        """
        Generate all n-grams from the given sentence after normalizing.

        Parameters:
        - n (int): The length of the n-grams to generate.
        - sentence (str): The sentence to generate n-grams from.

        Returns:
        - iter: An iterator over the generated n-grams.
        """
        filtered = self.normalize(sentence)
        for start in range(0, len(filtered) - n + 1):
            yield ''.join(filtered[start:start + n])

    def avg_transition_prob(self, sentence: str, matrix: list) -> float:
        """
        Calculate the average transition probability for the given sentence using the given transition probability matrix.

        Parameters:
        - sentence (str): The sentence to calculate the average transition probability for.
        - matrix (list): The transition probability matrix.

        Returns:
        - float: The average transition probability.
        """
        log_probability = 0.0
        transition_count = 0
        for a, b, c in self.ngram(3, sentence):
            #The transition probability of character 'c' is determined by the 2 previous characters 'a' and 'b'.
            log_probability += matrix[self.pos[a]][self.pos[b]][self.pos[c]]
            transition_count += 1
        # The exponentiation translates from log probs to probs.
        return math.exp(log_probability / (transition_count or 1))
    
    def transition_probability(self, sentence: str, markov_threshold) -> bool:
        """
        Generate the tranistion (Markov) probability for the given sentence using the pickled model.

        Parameters:
        - sentence (str): The sentence to generate the transition probability for.

        Returns:
        - bool: True if the average transition probability is less than 0.045, else False
        """
        model_matrix = self.gibberish_model['mat']
        return self.avg_transition_prob(sentence, model_matrix) < markov_threshold
    
