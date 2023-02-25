import creds
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import art_response
import requests
import re
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import openai

app = FastAPI()

class MyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = 0
        response = await call_next(request)
        process_time = 0 - start_time
        response.headers['X-Process-Time'] = str(process_time)
        return response

app.add_middleware(MyMiddleware)

origins = ["http://localhost:8000", "http://localhost:3000", "https://negaart-website.pages.dev", "https://main.d2gbfssz1qw5je.amplifyapp.com/"]
app.add_middleware(CORSMiddleware, allow_origins=origins)

@app.get("/")
async def root() -> str:
    return "This is an API that will get take in the prompt, invert the prompt, and return the AI image from openAI"

@app.get("/generate_image/{prompt}")
async def get_art(prompt: str):
    words: list[str] = re.sub(r"[^a-zA-Z0-9]"," ", prompt).lower().split()
    url_left: str = "https://wordsapiv1.p.rapidapi.com/words/"
    url_right: str = "/antonyms"
    headers = {
        "X-RapidAPI-Key": "2b9fc0c12amsh52a4bfcc76b3102p166597jsn845631d0a045",
        "X-RapidAPI-Host": "wordsapiv1.p.rapidapi.com"
    }

    inverseWords: list[str] = list()
    for word in words:
        try:
            response = requests.get(url_left + word + url_right, headers=creds.rapidapi_headers).json()
            
                
            if response["antonyms"]:
                inverseWords.append(response["antonyms"][0])
            else:
                inverseWords.append(word)
            inverseWords.append(" ")
        except Exception:
            inverseWords.append(word)
            inverseWords.append(" ")

    inverseWords.pop()


    invertedPrompt: str = "".join(inverseWords)

    #call openai's DALL-E for image generation
    openai.api_key = creds.openai_key
    image = openai.Image.create(
                    prompt=invertedPrompt,
                    n=1,
                    size="1024x1024"
                )

    return art_response(
        original_prompt=prompt,
        inverted_prompt=invertedPrompt,
        imageURL=image['data'][0]['url']
        )
