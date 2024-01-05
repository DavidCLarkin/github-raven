import json
import os
import logging

from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler
from fastapi import FastAPI, Request

from utils import _is_retry


app = App(
    token=os.getenv('SLACK_BOT_TOKEN'),
    signing_secret=os.getenv('SLACK_SIGNING_SECRET')
)
app_handler = SlackRequestHandler(app)

forward_channel_id = os.getenv('FORWARD_CHANNEL_ID')
noisy_github_bots = ['https://github.com/apps/sonarcloud']

logging.basicConfig(level=logging.INFO, filename='log.log',
                    filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')
# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# add the handler to the root logger
logging.getLogger('').addHandler(console)


@app.event("message")
def handle_message_event(body, logger, client, ack):
    ack()
    is_github_bot = body.get('event', {}).get(
        'bot_profile', {}).get('name', '') == 'GitHub'
    logger.info('Received slack message')

    if is_github_bot:
        attachments = body.get('event', {}).get('attachments')
        forward_attachments = []
        for attachment in attachments:
            logger.info(f'FROM: {attachment.get("pretext")}')
            github_user: str = attachment.get('pretext', '')
            attachment_text: str = attachment.get("text", "")
            is_noisy_bot = next(
                (True for bot in noisy_github_bots if github_user.find(bot) > -1), False)
            # filter out passing BlackDuck check messages, since they're just extra noise
            if "None of your dependencies violate policy!" in attachment_text:
                is_noisy_bot = True
            if not is_noisy_bot:
                forward_attachments.append(attachment)
        logger.info(f'Forwarding github: {json.dumps(forward_attachments, sort_keys=True, indent=4)}')
        # set whitespace char as text arg to silence Slack Bolt warning, see: https://github.com/slackapi/bolt-js/issues/1249#issuecomment-997113227
        client.chat_postMessage(channel=forward_channel_id, attachments=forward_attachments)


api = FastAPI()


@api.post("/slack/events")
async def endpoint(req: Request):
    return await app_handler.handle(req)


@api.get("/")
def hello():
    return 'Hello'


@app.use
def log_request_headers(logger, request, next):
    logger.info("REQUEST HEADERS", request.headers)
    next()


@app.use
def ignore_retry_request(request, ack, next, logger):
    # https://github.com/slackapi/bolt-python/issues/693#issuecomment-1206887767
    if _is_retry(request, logger):
        return ack()
    next()  # if this is not a retry, Bolt app should handle it
