
print("Entrou no LoadLlama.py")
import subprocess, sys

# # Define the pip command to run
# cmd = [sys.executable, '-m', 'pip', 'install', 'transformers']
#
# # Run the pip command
# subprocess.run(cmd)

# from huggingface_hub import login

from transformers import AutoTokenizer, AutoModelForCausalLM

#
# login()

tokenizer = AutoTokenizer.from_pretrained("TheBloke/stablecode-instruct-alpha-3b-GPTQ")
print("Loaded tokenizer_")
model = AutoModelForCausalLM.from_pretrained("TheBloke/stablecode-instruct-alpha-3b-GPTQ")
print("Loaded model")


prompt = "Who is CR7?"

# Tokenize the prompt
input_ids = tokenizer.encode(prompt, return_tensors='pt')
print("Loaded encode")

# Generate text from the prompt
output = model.generate(input_ids, temperature=0.0)
print("Loaded output")

# Decode the generated text
generated_text = tokenizer.decode(output[0], skip_special_tokens=True)

# Print the generated text
print(generated_text)
