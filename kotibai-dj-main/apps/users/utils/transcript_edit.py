import asyncio

import tiktoken

from users.utils import send_request_openai


def split_text_by_tokens(text, max_tokens=1500):
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    tokens = encoding.encode(text)

    chunks = [tokens[i:i + max_tokens] for i in range(0, len(tokens), max_tokens)]

    text_chunks = [encoding.decode(chunk) for chunk in chunks]

    return text_chunks


def transcript_edit_openai(prompt, text, model="gpt-4o", user=None):
    text_chunks = split_text_by_tokens(text)
    all_responses = []

    for i, chunk in enumerate(text_chunks):
        print(f"Bo'lak {i + 1}/{len(text_chunks)} jo'natilmoqda...")
        result_answer = send_request_openai(prompt, chunk, model, user)
        all_responses.append(result_answer)
        print(f"Bo'lak {i + 1} dan javob olingan.")

    combined_response = "\n".join(all_responses)

    return combined_response
