# Imports:
import sys

from app.Gibberish_Detector.gibberish_detector import GibberishDetector

def attack_blocker(input_prompt):
    
    gibberish_detector = GibberishDetector()
    gibberish_detector.process_sentences_from_text(input_prompt)

    print(gibberish_detector.detected_gibberish, gibberish_detector.gibberish_sentences)
    return gibberish_detector.detected_gibberish


if __name__ == "__main__":
    attack_blocker(sys.argv[1])