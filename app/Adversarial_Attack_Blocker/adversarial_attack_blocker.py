from nltk import sent_tokenize
from transformers import pipeline

import warnings
warnings.simplefilter('ignore')

class AttackDetector(object):
    """
    Detector for prompt and code injections. Identifies sentences which
    could be considered attacking the llm systems.

    Classification Model
    --------------------
    Name : deepset/deberta-v3-base-injection
    License : MIT

    Parameters
    ----------
    score_threshold : float, default=0.7
        Threshold for considering text attacking.
    """    
    def __init__(self,
                injection_threshold: float = 0.7,
                debug: bool = False) -> None:

        self._pipe = pipeline("text-classification", 
                              model="deepset/deberta-v3-base-injection", 
                              )
        self.injection_threshold: float = injection_threshold
        self.debug = debug
        self.detected_attack: bool = False
        self.attack_sentences: list[dict] = []
        

    def _get_attack_score(self, text: str) -> (str, float):
        return self._pipe(text)
    

    def _reset_params(self) -> None:
        self.attack_sentences = []
        self.detected_attack = False


    def process_sentences_from_text(self,
                                    text: str,
                                    use_nlp: bool = True,
                                    delimiter: str | None = None) -> None:
        """Processes text to screen for toxicity. Must specify a method to
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
    

    def process_sentences(self, sentences: list[str]) -> None:
        '''Check if the prompt sentences contain attack'''
        self._reset_params()

        for sentence in sentences:
            scores = self._get_attack_score(sentence)
            if self.debug:
                print(sentence, scores)
            res = max(scores, key=lambda x : x['label'])
            result_dict = {
                "label": res['label'],
                "confidence": res['score'],
                "sentence": sentence
            }
            if result_dict['label']=='INJECTION' and result_dict["confidence"] > self.injection_threshold:
                self.attack_sentences.append(result_dict)
                self.detected_attack = True
            else:
                pass
