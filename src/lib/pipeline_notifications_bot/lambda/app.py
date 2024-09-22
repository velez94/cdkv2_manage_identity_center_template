import os

import pymsteams
from get_secret import get_secret
import json

def lambda_handler(event, context):
    print(event)
    #
    # Initialization WebHook
    #
    webhook_secret_url = get_secret()
    team_message = pymsteams.connectorcard(webhook_secret_url)
    print("Sending message to Teams through webhook...")
    team_message.color("7b9683")
    stage = pymsteams.cardsection()
    # Section Title
    stage.title("Pipeline State")

    #
    # Select message
    #
    if event['detail']['state'] == 'FAILED':

        team_message.title(f"Pipeline Fail")
        stage.text( event['detail'])
        stage.activityImage(
            "https://support.content.office.net/en-us/media/c9ed80c9-a24c-40b0-ba59-a6af25dc56fb.png")

    elif event['detail']['state'] == 'SUCCEEDED':
        team_message.title(f"Pipeline run Successfully")
        stage.text(event['detail'])
        stage.activityImage(
            "https://support.content.office.net/en-us/media/47588200-0bf0-46e9-977e-e668978f459c.png")
    #
    # send the message
    #
    team_message.addSection(stage)
    team_message.send()

