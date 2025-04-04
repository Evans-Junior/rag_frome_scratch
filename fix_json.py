import json

def fix_json_file(input_file, output_file):
    with open(input_file, 'r') as f:
        try:
            # Try to load as regular JSON array
            data = json.load(f)
            # Save as newline-delimited JSON
            with open(output_file, 'w') as out:
                for item in data:
                    out.write(json.dumps(item) + '\n')
            print(f"Successfully converted to newline-delimited JSON in {output_file}")
        except json.JSONDecodeError:
            print("Error: Input file is not valid JSON")

if __name__ == "__main__":
    fix_json_file("balanced_dataset.json", "fixed_dataset.json")