
class LoadPrompt(object):
    """
    return PromptFile's data
    """
    
    def __init__(
        self,
        prompt_file: str,
        ):
        self.__prompt = self.__load_prompt(prompt_file)

    def __load_prompt(self, file):
        with open(file, 'r', encoding='utf-8') as f:
            data = f.read()
        return data
    
    @property
    def to_str(self):
        return self.__prompt

    def __str__(self):
        return self.__prompt


if __name__ == "__main__":
    print(type(LoadPrompt('prompts/prompt_extract_data.txt').to_str))