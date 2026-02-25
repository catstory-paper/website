import re

def process_css(input_file, output_file):
    with open(input_file, 'r') as f:
        content = f.read()

    # Split into blocks and comments roughly
    # A robust way is to use a simple parser
    
    # 1. replace :root { with .dark-theme {
    content = content.replace(':root {', '.dark-theme {')
    
    # 2. prefix body selectors
    content = re.sub(r'\bbody\s*\{', '.dark-theme {', content)
    
    # For other top-level rules, we can manually prefix them using a regex that looks for standard selectors
    # But since dark.css is a known 990-line file, let's write a simple block parser
    
    out_lines = []
    in_block = False
    in_media = False
    
    lines = content.split('\n')
    for line in lines:
        stripped = line.strip()
        
        # skip empty, comments, or at-rules
        if not stripped or stripped.startswith('/*') or stripped.startswith('@'):
            if stripped.startswith('@media'):
                in_media = True
            out_lines.append(line)
            continue
            
        if stripped == '}':
            if in_block:
                in_block = False
            elif in_media:
                in_media = False
            out_lines.append(line)
            continue
            
        if '{' in stripped and not in_block:
            in_block = True
            
            # This is a selector line
            if stripped.startswith('.dark-theme'):
                out_lines.append(line)
                continue
                
            # If it's keyframes or something, skip
            if 'keyframes' in stripped:
                out_lines.append(line)
                continue
            
            # split selectors by comma
            selectors = stripped.split('{')[0].split(',')
            new_selectors = []
            for sel in selectors:
                sel = sel.strip()
                if not sel: continue
                # if it's already prefixed, or pseudo element
                if sel.startswith('.dark-theme'):
                    new_selectors.append(sel)
                elif sel.startswith('::'):
                    new_selectors.append(f".dark-theme {sel}")
                elif sel.startswith('body'):
                    new_selectors.append(sel.replace('body', '.dark-theme', 1))
                else:
                    new_selectors.append(f".dark-theme {sel}")
            new_line = ', '.join(new_selectors) + ' {'
            
            # preserve leading whitespace
            indent = line[:len(line) - len(line.lstrip())]
            out_lines.append(indent + new_line)
        else:
            out_lines.append(line)

    with open(output_file, 'w') as f:
        f.write('\n'.join(out_lines))

if __name__ == "__main__":
    process_css('assets/stylesheets/dark.css', 'assets/stylesheets/dark.css')
