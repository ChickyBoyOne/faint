from bs4.element import NavigableString, Tag

def to_bbcode(tag: Tag) -> str:
    bbcode = ''

    for i, child in enumerate(tag.contents):
        if type(child) == NavigableString:
            child = child.replace('\n', '')

            if i == 0:
                bbcode += child[16:]
            elif i == len(tag.contents) - 1:
                bbcode += child[:-12]
            else:
                bbcode += child
            
            continue
        
        if child.name == 'br':
            bbcode += '\n'
    
    return bbcode