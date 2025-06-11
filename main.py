import re
import os
import shutil
import sys

def build_test():
    build("file:///home/leaf/projects/site/dist",".html")

def build_deploy():
    build("https://leafmotive.com")

def build(domain,path_ending=""):
    consts = {}
    for html_file in [f for f in os.listdir(".") if f.endswith(".html")]:
        with open(html_file,"r") as f:
            consts[html_file] = f.read()
    consts["domain"] = domain
    consts["path_ending"] = path_ending
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    os.mkdir("dist")
    for f in os.listdir("pages"):
        _convert_pages_entity_to_html(f,None,consts)

def _convert_pages_entity_to_html(fname,full_path, consts):
    if full_path is None: full_path = fname
    file_path = f"pages/{full_path}"
    if os.path.isdir(full_path):
        os.mkdir(f"dist/{full_path}")
        for f in os.listdir(file_path):
            _convert_pages_entity_to_html(f,f"{full_path}/{f}",consts)
        return
    assert(os.path.isfile(file_path))
    full_path, extension = full_path.split(".")
    html = ""
    if extension == "html":
        with open(file_path,"r") as f:
            html = f.read()
    elif extension == "md":
        with open(file_path,"r") as f:
            html = md_to_html(f.read(),consts["domain"],consts["path_ending"])
    with open(f"dist/{full_path}.html","w+") as f:
        f.write(consts["base.html"].replace("{{CONTENT}}",html))




def md_to_html(md, domain="https://mydomain.com",path_ending=""):
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
    html = re.sub(r'(?<!#)\[([^\]]+)\](?!\()', lambda m: f'<a href="{domain}/{m.group(1)}{path_ending}">{m.group(1)}</a>', html)
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

if len(sys.argv) == 2 and sys.argv[1] == "deploy":
    build_deploy()
