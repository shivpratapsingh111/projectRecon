import aiohttp, asyncio

async def fetch_response_size_streaming(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            size = 0
            async for chunk in response.content.iter_any():
                size += len(chunk)  # Count bytes as they stream in
            return size

url = "https://assets.ab-destinations.bolt.eu/appsflyer.min.js"
size = asyncio.run(fetch_response_size_streaming(url))
print(f"Response size (streaming): {size} bytes")
