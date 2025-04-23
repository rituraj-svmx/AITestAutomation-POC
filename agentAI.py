import asyncio
import os

from browser_use import Agent
from browser_use.agent.views import ActionResult
from browser_use.browser.context import BrowserContext
from browser_use.controller.service import Controller
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from pydantic import SecretStr, BaseModel
from dotenv import load_dotenv


class CheckoutResult(BaseModel):
    login_status: str
    cart_status: str
    checkout_status: str
    total_update_status: str
    delivery_location_status: str
    confirmation_message: str

controller = Controller(output_model = CheckoutResult)

@controller.action('Launch the Application')
async def open_website(browser : BrowserContext):
    page = await browser.get_current_page()
    await page.goto('https://rahulshettyacademy.com/loginpagePractise/')
    return ActionResult(extracted_content = "app launched")

@controller.action('Get Attribute and url of the page')
async def get_attribute_url(browser : BrowserContext):
    page = await browser.get_current_page()
    current_url = page.url
    attr = await page.get_by_text("Shop Name").get_attribute('class')
    return ActionResult(extracted_result = f'current url is {current_url} and the attribute is {attr}')


async def cart_validation():
    task = (
        'Important : I am UI Automation tester validating the tasks'
        'Open website with this url "https://rahulshettyacademy.com/loginpagePractise/"'
        'Login with username and password. username and paasword are available in the same page'
        'After login you need to add 3 products which are displayed on this screen by clicking on "Add" button'
        'Then checkout and store the total value you see in screen'
        'Increase the quantity of any product and check if total value update accordingly'
        'checkout and select country, agree terms and purchase '
        'verify thankyou message is displayed'
    )
    load_dotenv(dotenv_path='C:/Users/XW334BQ/PycharmProjects/AITestAutomation/test.env')
    print("GEMINI_API_KEY : ", os.environ.get("GEMINI_API_KEY"))
    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in the environment variables")

    llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash-exp-image-generation', api_key=SecretStr(api_key))
    # api_key = os.environ.get("GEMINI_API_KEY")
    #llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash-exp-image-generation',api_key= SecretStr(api_key))
    #llm = ChatOpenAI(model = 'omni-moderation-2024-09-26',api_key= SecretStr(api_key))
    agent = Agent(task=task,controller=controller,llm=llm,use_vision=True)
    history = await agent.run()
    history.save_to_file("agentresult.json")
    result = history.final_result()
    validated_result = CheckoutResult.model_validate_json(result)
    print(result)
    assert validated_result.confirmation_message=="Thank you!"

asyncio.run(cart_validation())

