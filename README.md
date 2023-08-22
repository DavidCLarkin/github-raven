# Github Raven

Filter out github bot slack messages.
Inspired by [Christian Sepulveda](https://medium.com/justideas-io/slack-notifications-filter-4760ed642457v)
since [this](https://github.com/integrations/slack/issues/1408) is still an issue.

## Local dev

First set up your `.env`
```
export SLACK_BOT_TOKEN=<>
export SLACK_SIGNING_SECRET=<>
export FORWARD_CHANNEL_ID=<>
```

Install [ngrok](https://ngrok.com/download) and run it
```
ngrok http 300
```

In another terminal set up python and run the local server:
```
source .env
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip3 install -r requirements.txt
 ./.venv/bin/uvicorn app:api --reload --port 3000 --log-level warning
```


## Deploying

Slack bot token: https://api.slack.com/apps/A04B2CURD6K/oauth?
Slack Signing Secret: https://api.slack.com/apps/A04B2CURD6K/general?
Forward channel id: ~good luck~ Go to the #twig-internal channel, click the name at the top to open the info modal, and on the About tab, scroll all the way down - you should see the channel ID there.

Install fly.io, log in and run:
```
flyctl launch, choose a unique name, choose a region, No PSQL, No Redis, No need for .dockerignore, don't deploy just yet
fly set secrets ... for each individual secret in the .env
fly deploy
```


## Troubleshooting

- There was a time when GitHub Raven stopped working, without any explanation. After some investigation, it wasn't really clear what the issue was. In this sort of situation, you can:
  - Go to https://api.slack.com/methods/auth.test/test. Paste the `SLACK_BOT_TOKEN` and check that you get a good response from the Slack API (`"ok": true`, etc.)
  - Ultimately, re-deploying the app by resetting the secrets on Fly.io and then running `fly deploy` helped. Not sure why though...
