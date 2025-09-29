'''
input: <string>
output: "Hello <string>!"
'''
## define variable for testing
# keyword_example = "SEONGON"


## define function
def speak(keyword: str) -> str:
    message = f"Hello {keyword}!"
    return message

# speak(keyword_example)