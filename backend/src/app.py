from dotenv import dotenv_values
import openai
from langkit import injections, extract
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import torch

tokenizer = AutoTokenizer.from_pretrained("ProtectAI/deberta-v3-base-prompt-injection")
model = AutoModelForSequenceClassification.from_pretrained("ProtectAI/deberta-v3-base-prompt-injection")

def gptAnswer(question: str) -> str:
    config = dotenv_values('.env')
    openai.api_key = config["GPT_KEY"]

    models = {
        "text-only": "gpt-3.5-turbo",
        "txt-img": "gpt-4-vision-preview"
    }

    context = "we are inside the museum of natural history in NYC and you are currently helping an individuals with various disabilities such as blindness, deafness, near sightedness etc."

    gpt_response = openai.chat.completions.create( #input transcribed text as GPT prompt
        model=models["text-only"],
        messages=[
            {"role": "system", "content": "you are a concise and helpful robotic quadruped dog named spot made by boston dynamics, that is a tour guide with a texan accent"}, # give a personality to the model
            {"role": "assistant", "content": context}, # add extra context to the user's req
            {"role": "user", "content": question} # user's req/prompt
        ],
        max_tokens = 250 #cap the length of the response
    )

    return gpt_response.choices[0].message.content


def checkPrompt(prompt: str) -> bool:
    schema = injections.init()

    langKitCheck = extract({"prompt":prompt},schema=schema) 
    classifier = pipeline(
        "text-classification",
        model=model,
        tokenizer=tokenizer,
        truncation=True,
        max_length=512,
        device=torch.device("cuda" if torch.cuda.is_available() else "cpu"),
    )
    huggingFaceCheck = classifier(prompt)

    return langKitCheck['prompt.injection'] >= 0.5 and huggingFaceCheck[0]['score'] >= 0.5
