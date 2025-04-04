import json
from pathlib import Path

def fix_json_file(file_path):
    # Read the raw content
    with open(file_path, 'r') as f:
        content = f.read().strip()
    
    # Remove existing brackets if present
    if content.startswith('[') and content.endswith(']'):
        content = content[1:-1]
    
    # Split into lines and clean entries
    entries = []
    for line in content.split('\n'):
        line = line.strip()
        if line:  # Skip empty lines
            if line.endswith(','):
                line = line[:-1]  # Remove trailing comma
            entries.append(line)
    
    # Rebuild as valid JSON
    fixed_content = '[\n' + ',\n'.join(entries) + '\n]'
    
    # Validate the JSON
    try:
        json.loads(fixed_content)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON after fixing: {e}")
        return False
    
    # Write the fixed content back
    with open(file_path, 'w') as f:
        f.write(fixed_content)
    
    return True

if __name__ == "__main__":
    file_path = "balanced_dataset.json"
    if Path(file_path).exists():
        success = fix_json_file(file_path)
        if success:
            print(f"Successfully fixed {file_path}")
        else:
            print(f"Failed to fix {file_path}")
    else:
        print(f"Error: File {file_path} not found")