from typing import List
from nltk.tokenize import sent_tokenize
import pandas as pd
from transformers import pipeline

from app.Gibberish_Detector.utils_copy.transition_probability import Markov

class GibberishDetector(object):
    """
    Detector for gibberish and text to coerce/trick/confuse LLMs to carrying
    out malicious actions.

    Parameters
    ----------
    classification_threshold : float, default=0.7
        Threshold for classifying gibberish text.
    """
    def __init__(self, classification_threshold: float = 0.7) -> None:
        self.text_classification = pipeline("text-classification", model="madhurjindal/autonlp-Gibberish-Detector-492513457", top_k=None)
        self.weights = {'clean': 0, 'mild gibberish': 0.1, 'noise': 0.9, 'word salad': 1}
        self.detected_gibberish = False
        self.gibberish_sentences = []
        self.clean_sentences = []
        self.gibberish_words = []
        self.markov = Markov()
        self.markov_threshold = 0.045
        self.classification_threshold = classification_threshold


    def _reset_params(self) -> None:
        """Reset the internal states."""
        self.gibberish_sentences.clear()
        self.clean_sentences.clear()
        self._set_detected_gibberish(False)


    def _set_detected_gibberish(self, detected_gibberish_flag: bool) -> None:
        """
        Set the detected gibberish flag to the given boolean value.

        Parameters:
        - detected_gibberish_flag (bool): The boolean value to set the detected gibberish flag to.

        Returns:
        - None
        """
        self.detected_gibberish = detected_gibberish_flag


    def get_detected_gibberish(self) -> bool:
        """
        Get the detected gibberish flag.

        Parameters:
        - None

        Returns:
        - bool: The detected gibberish flag.
        """
        return self.detected_gibberish


    def get_gibberish_score(self, prompt: str) -> list:
        """
        Return the gibberish score for the given prompt using the HuggingFace text classification pipeline.

        Parameters:
        - prompt (str): The prompt to get the gibberish score for.

        Returns:
        - list: A list of dictionaries containing the gibberish score for each category.
        """
        return self.text_classification([prompt])


    def _generate_sentence_score(self, scores_dict: dict) -> float:
        """
        Generate a sentence score based on the given scores dictionary and the weights for different gibberish categories.

        Parameters:
        - scores_dict (dict): A dictionary containing the gibberish score for each category.

        Returns:
        - float: The sentence score.
        """
        return sum(score * self.weights[label] for label, score in scores_dict.items() if label in self.weights)


    def get_gibberish_sentences(self) -> list:
        """
        Get the list of gibberish at a sentence level.

        Parameters:
        - None

        Returns:
        - list: The list of gibberish sentences.
        """
        gibberish_list = []
        for gibberish in self.gibberish_sentences:
            gibberish_list.append(gibberish['sentence'])
        return gibberish_list

    
    def get_gibberish_words(self) -> list:
        """
        Get the list of gibberish at a word level. To prevent false positives, the threshold at word level is set higher to 85%.

        Parameters:
        - None

        Returns:
        - list: The list of gibberish words.
        """
        self.gibberish_words = [word for sentence in self.gibberish_sentences for word in sentence.split() if self.generate_confidence_score(word) > 0.85]
        return self.gibberish_words


    def get_clean_sentences(self) -> list:
        """
        Return the list of clean sentences.

        Parameters:
        - None

        Returns:
        - list: The list of clean sentences.
        """
        return self.clean_sentences


    def generate_confidence_score(self, sentence: str) -> float:
        """
        Generate a confidence score for the given sentence based on the gibberish score for each category and the weights
        for different gibberish categories.

        Parameters:
        - sentence (str): The sentence to generate the confidence score for.

        Returns:
        - float: The confidence score.
        """
        scores = self.get_gibberish_score(sentence)
        confidence = {score_dict['label']: score_dict['score'] for score_dict in scores[0]}
        return sum(score * self.weights[label] for label, score in confidence.items() if label in self.weights)


    def generate_word_confidence(self) -> list:
        """
        Generate a list of confidence scores for each gibberish word.

        Parameters:
        - None

        Returns:
        - list: The list of confidence scores.
        """
        return [self.generate_confidence_score(word) for word in self.get_gibberish_words()]


    def bulk_generate_confidence_score(self) -> list:
        """
        Generate a list of sentence scores for all gibberish sentences.

        Parameters:
        - None

        Returns:
        - list: The list of sentence scores.
        """
        return [self._generate_sentence_score({score_dict['label']: score_dict['score'] for score_dict in self.get_gibberish_score(sentence)[0]}) for sentence in self.gibberish_sentences]


    def results_as_dataframe(self, prompt_sentences: list) -> pd.DataFrame:
        """
        Generate a pandas dataframe containing the extracted gibberish sentences, the confidence score for each sentence,
        and a boolean flag indicating whether the Markov chain was detected.

        Parameters:
        - prompt_sentences (list): The list of prompt sentences to process.

        Returns:
        - pd.DataFrame: The pandas dataframe.
        """
        self.process_sentences(prompt_sentences)
        df = pd.DataFrame({
            "Extracted Sentences": self.get_gibberish_sentences(),
            "Confidence Score": self.bulk_generate_confidence_score()
        })
        df["Markov Chain Detected"] = [x < self.classification_threshold for x in df["Confidence Score"]]
        return df


    def words_as_dataframe(self) -> pd.DataFrame:
        """
        Generate a pandas dataframe containing the extracted gibberish words and the confidence score for each word.

        Parameters:
        - None

        Returns:
        - pd.DataFrame: The pandas dataframe.
        """
        return pd.DataFrame({
            "Extracted Words": self.get_gibberish_words(),
            "Confidence Score": self.generate_word_confidence()
        })

    
    def process_sentences(self, prompt_sentences: List[str]) -> None:
        """
        Process the provided sentences by generating a sentence score and
        transition probability. Each sentence is added to the gibberish or
        clean sentences list based on their score.

        Parameters:
        - prompt_sentences (list): The list of prompt sentences to process.

        Returns:
        - None
        """
        self._reset_params()
        for sentence in prompt_sentences:
            gibberish_scores = self.get_gibberish_score(sentence)
            scores_dict = {score_dict['label']: score_dict['score'] for score_dict in gibberish_scores[0]}

            # Find the highest-scoring label to return
            maxlabel, maxscore = None, -1.0
            for label, score in scores_dict.items():
                if score > maxscore:
                    maxlabel = label
                    maxscore = score

            if (gibberish_score:=self._generate_sentence_score(scores_dict)) > self.classification_threshold:
                self.detected_gibberish = True
                self.gibberish_sentences.append({"label": maxlabel,
                                                 "confidence": gibberish_score,
                                                 "sentence": sentence})
            else:
                self.clean_sentences.append(sentence)


    def process_sentences_from_text(self,
                                    text: str,
                                    use_nlp: bool = True,
                                    delimiter: str | None = None) -> None:
        """Convert prompt to a sentence level. Must specify a method to
        split up text: either `delimiter` is not `None`, or `use_nlp` is
        `True`.

        Parameters
        ----------
        text : str
            Text to parse as sentences.

        use_nlp : bool, default=True
            Use the NLTK library to split sentences.

        delimiter : str or None, default=None
            Delimiter to use to split sentences. Used if specified regardless
            of `use_nlp` value.
        """
        if delimiter is not None:
            self.process_sentences([s+delimiter for s in text.split(text) if s])
        elif delimiter is None and use_nlp is False:
            raise AttributeError("Delimiter cannot be None and use_nlp False.")
        else:
            self.process_sentences(sent_tokenize(text))
