def clean_wordlist(input_file, output_file):
    with open(input_file, 'r') as f:
        lines = f.readlines()

    cleaned_lines = []
    for line in lines:
        line = line.rstrip('\n')
        if line.endswith('/') or line.endswith('\\'):
            line = line[:-1]
        cleaned_lines.append(line)

    with open(output_file, 'w') as f:
        f.write('\n'.join(cleaned_lines))

    print(f"Wordlist cleaned successfully. Cleaned wordlist saved to {output_file}.")

if __name__ == "__main__":
    input_file = input("Enter the path to the input wordlist file: ")
    output_file = input("Enter the path to save the cleaned wordlist file: ")

    clean_wordlist(input_file, output_file)
