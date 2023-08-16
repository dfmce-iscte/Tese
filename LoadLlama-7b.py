
print("Entrou no LoadLlama.py")
import subprocess, sys

# # Define the pip command to run
# cmd = [sys.executable, '-m', 'pip', 'install', 'transformers']
#
# # Run the pip command
# subprocess.run(cmd)

from transformers import AutoTokenizer, AutoModelForCausalLM

from huggingface_hub import login

import torch

login()

tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-chat-hf", torch_dtype=torch.float16)
print("Loaded tokenizer")
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-chat-hf", torch_dtype=torch.float16)
print("Loaded model")


prompt = "Who is CR7?"

# Tokenize the prompt
input_ids = tokenizer.encode(prompt, return_tensors='pt')
print("Loaded encode")

# Generate text from the prompt
output = model.generate(input_ids, temperature=0.0000001)
print("Loaded output")

# Decode the generated text
generated_text = tokenizer.decode(output[0], skip_special_tokens=True)

# Print the generated text
print(generated_text)
