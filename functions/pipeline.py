from keywordToSlug import keyword_to_slug
from speakKeyword import speak

keyword_input = input()

def pipeline(input):
    ## function 1
    slug = keyword_to_slug(input) ## input: tu khoa -> slug = "tukhoa"

    ## function 2
    message = speak(slug)

    print(message)
    return message


pipeline(keyword_input)
