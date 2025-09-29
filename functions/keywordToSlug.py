# keyword_example = 'từ khóa'
'''
expected output:
slug = 'tu-khoa'
'''

## function turn keyword into slug
def keyword_to_slug(keyword: str) -> str:
    slug = keyword.replace(" ", '')
    return slug


# keyword_to_slug(keyword_example)