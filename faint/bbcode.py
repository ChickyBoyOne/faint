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
        # Newlines
        elif child.name == 'br':
            bbcode += '\n'
        # All other tags
        elif (bbcode_tag_classes := [c for c in child['class'] if 'bbcode_' in c]) \
                and len(bbcode_tag_parts := bbcode_tag_classes[0].split("_")) == 2:
            if (bbcode_tag := bbcode_tag_parts[-1]) == 'quote':
                contents = to_bbcode(child, descendant=True)

                if (author := child.find("span", class_="bbcode_quote_name", recursive=False)):
                    bbcode += f'[quote={author.get_text().split()[0]}]{contents}[/quote]'
                else:
                    bbcode += f'[quote]{contents}[/quote]'
            elif bbcode_tag == 'hr':
                bbcode += '-----'
            else:
                bbcode += f'[{bbcode_tag}]{to_bbcode(child, descendant=True)}[/{bbcode_tag}]'
        elif child.name == 'span' and (style := child.get('style', '')):
            bbcode += f'[color={style.split()[-1][:-1]}]{to_bbcode(child, descendant=True)}[/color]'
    
    return bbcode