from bs4 import BeautifulSoup
from aiohttp import ClientSession
import asyncio
from requests_html import HTMLSession,AsyncHTMLSession
from fastapi import FastAPI, Path,Query,HTTPException,status
from fastapi.responses import JSONResponse
import re


app = FastAPI()

async def fetch_url_with_aiohttp(url:str) ->str:
    async with ClientSession() as session:
        response = await session.get(url)
        if response.status != 200:
            return await response.text(encoding="utf-8")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


async def fetch_url_with_requests_html(url:str) -> str:
    session = AsyncHTMLSession()
    response = await session.get(url)
    if response.status_code == 200:
        return response.html
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

url = "https://uk.wikipedia.org/wiki/%D0%92%D0%BE%D0%BB%D1%82_%D0%94%D1%96%D1%81%D0%BD%D0%B5%D0%B9"
tag = "b"
found_text = "До цього числа входять"

# ------------------------------------------------------


html = asyncio.run(fetch_url_with_aiohttp(url))

soup = BeautifulSoup(html, "lxml")
text = soup.find(string=re.compile(found_text)).find_parent(tag)

if text:
    print("text=",text.text)
    print("text=",text.get_text())
else:
    print("text not found")
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

# ------------------------------------------------------

html = asyncio.run(fetch_url_with_requests_html(url))

strings = html.xpath(f"//{tag}[contains(text(), '{found_text}')]//text()")

if strings:
    text = "".join(strings).replace("\n", "")
    print(f"{text=}")
else:
    print("text not found")
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
# ------------------------------------------------------

@app.get("/data/{tag}")
async def get_data(text: str = Query(...),url: str = Query(...)):
    html = await fetch_url_with_aiohttp(url)
    soup = BeautifulSoup(html, "lxml")
    text = soup.find(string=re.compile(text)).find_parent(tag)
    if text:
        return JSONResponse(content={"text": text.text})
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Тексту не знайдено")



