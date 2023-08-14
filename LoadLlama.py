import subprocess, sys

# Define the pip command to run
cmd = [sys.executable, '-m', 'pip', 'install', 'transformers']

# Run the pip command
subprocess.run(cmd)

from transformers import AutoTokenizer, AutoModelForCausalLM

tokenizer = AutoTokenizer.from_pretrained("Llama-2-13b-hf")
model = AutoModelForCausalLM.from_pretrained("Llama-2-13b-hf")


prompt = "Who is CR7?"

# Tokenize the prompt
input_ids = tokenizer.encode(prompt, return_tensors='pt')

# Generate text from the prompt
output = model.generate(input_ids, temperature=0.0)

# Decode the generated text
generated_text = tokenizer.decode(output[0], skip_special_tokens=True)

# Print the generated text
print(generated_text)
