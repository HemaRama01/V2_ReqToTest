from difflib import ndiff

def calculate_text_diff(original, matched):
    diff_lines = [
        line for line in ndiff(str(original).split(), str(matched).split())
        if line.startswith("(old) ") or line.startswith("(new) ")
    ]
    return "\n".join(diff_lines)
