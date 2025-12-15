import sys

path = 'examples/scenario_analysis_measles.ipynb'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace single backslashes in the problematic lines with double backslashes
# specifically targeting the known problematic strings
new_content = content.replace('($\\beta$)', '(\\\\beta$)').replace('($\\epsilon$)', '(\\\\epsilon$)')

# Just in case my previous analysis of the content was slightly off on what's in the file vs what view_file showed
# I saw: "2. ... ($\beta$).\n"
# In the file it's likely literally: ... ($\beta$) ...
# Wait, if it's already `\beta` in the file, reading it as string gives `\beta`.
# If I write it back, I want `\\beta`.
# But `replace` works on strings.
# '($\beta$)' in python string literal is '($\x08eta$)' because \b is backspace.
# So I should use raw strings.

new_content = content.replace(r'($\beta$)', r'($\\beta$)')
new_content = new_content.replace(r'($\epsilon$)', r'($\\epsilon$)')

if content == new_content:
    print("No replacement made. Checking for raw match...")
    # Maybe the file has them as non-escaped already?
    # View file showed: ... ($\epsilon$) ...
    # That means the bytes are ( ... \ ... )
    pass

with open(path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"Fixed {path}")
