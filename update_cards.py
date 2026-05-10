import re

with open('index.html', 'r') as f:
    content = f.read()

# For cert-card
def replace_cert(match):
    full_match = match.group(0)
    data_cert = match.group(1)
    
    # Check if we already added a preview to avoid double addition
    if 'card-image-preview' in full_match:
        return full_match
        
    preview_html = f'\n                <div class="card-image-preview">\n                    <img src="{data_cert}" alt="Certificate Preview">\n                </div>'
    
    # insert preview_html right after the opening div
    # find the end of the opening tag
    tag_end = full_match.find('>') + 1
    return full_match[:tag_end] + preview_html + full_match[tag_end:]

content = re.sub(r'<div class="cert-card" data-certificate="([^"]+)">.*?(?=</div>\s*<div class="cert-card"|</div>\s*</div>)', replace_cert, content, flags=re.DOTALL)

# For award-card
def replace_award(match):
    full_match = match.group(0)
    data_cert = match.group(1)
    
    if 'card-image-preview' in full_match:
        return full_match
        
    preview_html = f'\n                <div class="card-image-preview">\n                    <img src="{data_cert}" alt="Award Preview">\n                </div>'
    
    # replace the award-icon div entirely
    full_match = re.sub(r'\s*<div class="award-icon">.*?</div>', '', full_match)
    
    tag_end = full_match.find('>') + 1
    return full_match[:tag_end] + preview_html + full_match[tag_end:]

content = re.sub(r'<div class="award-card" data-certificate="([^"]+)">.*?(?=</div>\s*<div class="award-card"|</div>\s*</section>|</div>\s*</div>)', replace_award, content, flags=re.DOTALL)

with open('index.html.new', 'w') as f:
    f.write(content)
