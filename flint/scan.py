import google.generativeai as genai
import config

# Connect using the key from your config file
genai.configure(api_key=config.GEMINI_API_KEY)

print("Here are the models you can use:")
# Ask Google for the list and print the names
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)