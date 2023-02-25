from pydantic import BaseModel

class art_response(BaseModel):
    original_prompt: str
    inverted_prompt: str
    imageURL: str