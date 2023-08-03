import tiktoken


phrase = """
We are pleased to announce Claude 2, our new model.
"""


def num_tokens_from_string(string: str, model_name: str = "gpt-3.5-turbo") -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.encoding_for_model(model_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


if __name__ == "__main__":
    counts = num_tokens_from_string(phrase, "gpt-3.5-turbo")
    print(counts)