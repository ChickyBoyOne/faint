from typing import Optional

from bs4.element import NavigableString, Tag

SIMPLE_TAGS = {
    'strong': 'b',
    'i': 'i',
    'u': 'u',
    's': 's',
    'sup': 'sup',
    'sub': 'sub',
}

def to_bbcode(tag: Tag, descendant: bool = False) -> str:
    bbcode = ''

    for i, child in enumerate(tag.contents):
        # Text fragments
        # - Newlines are duplicated between text and tags
        # - First and last bounded by 16 and 12 spaces, respectively
        if type(child) == NavigableString:
            child = child \
                .replace('\n', '') \
                .replace('©', '(c)') \
                .replace('™', '(tm)') \
                .replace('®', '(r)')
            
            if not descendant:
                if i == 0:
                    child = child[16:]
                if i == len(tag.contents) - 1:
                    child = child[:-12]
            
            bbcode += child
            continue
        
        # Newlines
        if child.name == 'br':
            bbcode += '\n'
        # Simple tags
        elif child.name in SIMPLE_TAGS:
            bbcode_tag = SIMPLE_TAGS[child.name]
            bbcode += f'[{bbcode_tag}]{to_bbcode(child, descendant=True)}[/{bbcode_tag}]'
    
    return bbcode