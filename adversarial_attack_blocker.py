# Imports:
import sys

from app.Gibberish_Detector.GibberishDetector import GibberishDetector

def attack_blocker(input_prompt):
    
    gibberish_detector = GibberishDetector()
    gibberish_detector.process_sentences(input_prompt)

    # Gibberish detector flag:
    if gibberish_detector.detected_gibberish:
        gibberish_detected = True
        passed_input_controls = False
    else:
        gibberish_detected = False

    print(gibberish_detected, gibberish_detector.gibberish_sentences)
    return gibberish_detected


if __name__ == "__main__":
    attack_blocker(sys.argv[1])