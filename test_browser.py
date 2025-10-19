from stagehand import Stagehand, StagehandConfig
from dotenv import load_dotenv
import os
import asyncio
import litellm

load_dotenv()

# Set the API key as environment variable for litellm
os.environ["OPENAI_API_KEY"] = "dummy-openai-key"
os.environ["OPENAI_API_BASE"] = "http://localhost:8000/v1"

# Drop unsupported params
litellm.drop_params = True

async def main():
    config = StagehandConfig(
        env="LOCAL",
        api_key="dummy-openai-key",
        model_name="openai/gpt-4",
        model_client_options={
            "base_url": "http://localhost:8000/v1",
        },
        headless=False,
    )

    stagehand = Stagehand(
        config=config
    )

    await stagehand.init()
    await stagehand.page.goto("https://example.com")
    await stagehand.page.act("Click the first link on the page")
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())