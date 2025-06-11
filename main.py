import re

def md_to_html(md, domain="https://mydomain.com"):
    html = md
    # Headings (# ## ### etc) - convert to h1, h2, h3 with IDs
    html = re.sub(r'^(#{1,6})\s+(.+)$', lambda m: f'<h{len(m.group(1))} id="{m.group(2).lower().replace(" ", "-")}">{m.group(2)}</h{len(m.group(1))}>', html, flags=re.MULTILINE)
    # Bold + italic (*** text ***)
    html = re.sub(r'\*\*\*(.*?)\*\*\*', r'<strong><em>\1</em></strong>', html)
    # Bold (** text **)
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    # Italic (* text *)
    html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
    # Navigation to headings [#heading#]
    html = re.sub(r'\[#([^#]+)#\]', r'<a href="#\1">\1</a>', html)
    # Links ([text](url))
    html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)
    # Relative links [about] - only if not followed by ( and not preceded by #
    html = re.sub(r'(?<!#)\[([^\]]+)\](?!\()', lambda m: f'<a href="{domain}/{m.group(1)}">{m.group(1)}</a>', html)
    # Split by double newlines for paragraphs
    paragraphs = html.split('\n\n')
    result = []
    for p in paragraphs:
        lines = p.strip().split('\n')
        # Skip if it's already a heading
        if any(line.strip().startswith('<h') for line in lines):
            result.append(p.strip())
        # Check for lists
        elif any(line.strip().startswith(('- ', '* ', '+ ')) for line in lines):
            # Unordered list
            items = [re.sub(r'^[-*+] ', '', line.strip()) for line in lines if line.strip().startswith(('- ', '* ', '+ '))]
            result.append('<ul>' + ''.join(f'<li>{item}</li>' for item in items) + '</ul>')
        elif any(re.match(r'^\d+\. ', line.strip()) for line in lines):
            # Ordered list
            items = [re.sub(r'^\d+\. ', '', line.strip()) for line in lines if re.match(r'^\d+\. ', line.strip())]
            result.append('<ol>' + ''.join(f'<li>{item}</li>' for item in items) + '</ol>')
        else:
            # Regular paragraph
            if p.strip():
                result.append(f'<p>{p.strip()}</p>')
    return ''.join(result)
