# Imports:
import sys

from app.Adversarial_Attack_Blocker.adversarial_attack_blocker import AttackDetector

def attack_blocker(input_prompt):
    
    attack_detector = AttackDetector()
    attack_detector.process_sentences_from_text(input_prompt)

    print(attack_detector.detected_attack)
    return attack_detector.detected_attack


if __name__ == "__main__":
    attack_blocker(sys.argv[1])