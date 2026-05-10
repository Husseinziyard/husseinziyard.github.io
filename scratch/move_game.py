import re

with open('index.html', 'r') as f:
    content = f.read()

# Extract the game section
game_match = re.search(r'\s*<!-- Basketball Game Section -->.*?</section>', content, flags=re.DOTALL)
if game_match:
    game_html = game_match.group(0)
    # Remove it from the original place
    content = content.replace(game_html, '')
    
    # Insert it before Certifications Section
    content = content.replace('    <!-- Certifications Section -->', game_html + '\n\n    <!-- Certifications Section -->')

with open('index.html', 'w') as f:
    f.write(content)

