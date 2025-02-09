import logging
import requests
import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from io import BytesIO
from PIL import Image

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Replace with your bot token and OpenAI API key
BOT_TOKEN = os.getenv('BOT_TOKEN')  # Set this as an environment variable
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')  # Set this as an environment variable

# Function to handle the /start command
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Welcome! Send me a prompt, and I will generate an image for you!")

# Function to generate an image using DALL·E or similar API
def generate_image(prompt: str):
    url = "https://api.openai.com/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024"
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.json()['data'][0]['url']
    else:
        logger.error(f"Error generating image: {response.status_code} - {response.text}")
        return None

# Function to handle text messages and generate the image
def handle_message(update: Update, context: CallbackContext) -> None:
    prompt = update.message.text
    update.message.reply_text("Generating your image... Please wait.")
    
    # Generate image from prompt
    image_url = generate_image(prompt)
    
    if image_url:
        img_response = requests.get(image_url)
        img = Image.open(BytesIO(img_response.content))
        
        # Save image to a file-like object
        img_path = '/tmp/generated_image.jpg'
        img.save(img_path)
        
        # Send the image back to the user
        update.message.reply_photo(photo=open(img_path, 'rb'))
        os.remove(img_path)  # Clean up the image after sending
    else:
        update.message.reply_text("Sorry, there was an error generating the image.")

def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token
    updater = Updater(BOT_TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Register command and message handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you send a signal to stop it
    updater.idle()

if __name__ == '__main__':
    main()
