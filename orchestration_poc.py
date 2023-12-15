# Imports:

import sys
from setfit import SetFitModel


# Class definitions:

class PromptOrchestrator():

    def __init__(self, user_prompt: str):

        self.user_prompt = user_prompt
        self.transformer = SetFitModel._from_pretrained('orchestration_transformer')
        self.threshold = 0.65

    def orchestrate_prompt(self) -> str:

        prediction_probabilities = self.transformer.predict_proba([self.user_prompt]).tolist()[0][:5]

        filtered_probailities = list(map(lambda x: x > 0.65, prediction_probabilities))

        if True in filtered_probailities:
            prompt_type = filtered_probailities.index(True)
        else:
            prompt_type = None

        return_action = [
            'Run powerpoint creator prompts',
            'Run email creator prompts',
            'Run tone changer prompts',
            'Run summariser prompts',
            'Run proofreader prompts',
        ]

        if prompt_type is None:
            print('Run normal LLM prompt')
        else:
            print(return_action[prompt_type])


if __name__ == "__main__":
    prompt_orchestrator = PromptOrchestrator(sys.argv[1])
    prompt_orchestrator.orchestrate_prompt()