from bs4.element import NavigableString, Tag

def to_bbcode(tag: Tag) -> str:
    bbcode = ''

    for i, child in enumerate(tag.contents):
        if type(child) == NavigableString:
            child = child \
                .replace('\n', '') \
                .replace('©', '(c)') \
                .replace('™', '(tm)') \
                .replace('®', '(r)')
            
            if i == 0:
                child = child[16:]
            if i == len(tag.contents) - 1:
                child = child[:-12]
            
            bbcode += child
            continue
        
        if child.name == 'br':
            bbcode += '\n'
    
    return bbcode