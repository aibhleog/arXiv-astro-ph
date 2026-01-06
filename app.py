import os, subprocess
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Initializes your app with your bot token and socket mode handler
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# Listens to incoming messages that contain "hello"
# To learn available listener arguments,
# visit https://docs.slack.dev/tools/bolt-python/reference/kwargs_injection/args.html
@app.message("hello")
def message_hello(message, say):
    # say() sends a message to the channel where the event was triggered
    say(f"Hey there <@{message['user']}>!")


# @app.event("app_mention")
# def message_hello(message, say):
#     # say() sends a message to the channel where the event was triggered
#     say(f"Hey there!")

@app.event("message")
def handle_message_events(body, logger):
    logger.info(body)


# running the arxiv call
@app.event("app_mention")
def call_arxiv(say):
    say(f"Here's the arxiv posting for today!")

    result = subprocess.check_output('python3 access-arxiv.py', shell=True, text=True)
    say(result)


    

# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()