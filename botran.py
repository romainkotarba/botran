import collections
import os

from flask import Flask, request, jsonify

import ciscospark
import file_manager
import pprint

Data = collections.namedtuple('data', 'created id mentionedPeople personEmail personId roomId roomType')

app = Flask(__name__)
app.config.from_object('botran.default_settings')


def set_up_webhook(app_id, target_url):
    webhooks = ciscospark.get_webhooks()
    botran_webhooks = []
    if not webhooks.get('items'):
        ciscospark.register_webhook(app.config['BOTRAN_WEBHOOK_NAME'],
                                    app.config['BOTRAN_TARGET_URL'], 'messages', 'all')
        return True

    for botran_webhook in webhooks.get('items'):
        if botran_webhook.get('appId') == app_id and botran_webhook.get('targetUrl') == target_url:
            botran_webhooks.append(botran_webhook)

    if not botran_webhooks:
        ciscospark.register_webhook(app.config['BOTRAN_WEBHOOK_NAME'],
                                    app.config['BOTRAN_TARGET_URL'], 'messages', 'all')
        return True

    while len(botran_webhooks) > 1:
        ciscospark.delete_webhook(botran_webhooks[-1].get('id'))
        botran_webhooks.pop()

    return True


@app.route('/', methods=['POST'])
def hello_world():

    data_dict = request.json.get('data')
    data = Data(
        data_dict.get('created'),
        data_dict.get('id'),
        data_dict.get('mentionedPeople'),
        data_dict.get('personEmail'),
        data_dict.get('personId'),
        data_dict.get('roomId'),
        data_dict.get('roomType')
    )

    if app.config['BOTRAN_ID'] == data.personId:
        return '', 204

    if data.roomType == 'direct':
        disclaimer = ''
    else:
        disclaimer = "{} ".format(app.config['BOTRAN_NAME'])

    message = ciscospark.get_message(data.id)

    if message.get('text') == "{}help".format(disclaimer):
        message = "Hey, I'm Botran Octopus, aaaaand so far... I can:\n" \
                  "* @Botran **help**: Display this message again\n" \
                  "* @Botran **presentation**: Display info about myself\n" \
                  "* @Botran **info**: Display info about this room\n" \
                  "* @Botran **list**: List all attachments I've been mentioned\n" \
                  "* @Botran **zip**: Archive all the files I've been mentioned to in a Zip\n\n" \
                  "I'll keep an eye on all attachments you will mention me on. So don't hesitate to copy " \
                  "me next time you want to be sure to receive this file before leaving the space. \n\n" \
                  "Cheers"

    elif message.get('text') == "{}presentation".format(disclaimer):

        displayable_info = {'My Bot Name': 'BOTRAN_NAME',
                            'Webhook name': 'BOTRAN_WEBHOOK_NAME',
                            'My contact ;)': 'BOTRAN_CONTACT',
                            'Webhook target URL': 'BOTRAN_TARGET_URL',
                            'My secret key': 'BOTRAN_SECRET_',
                            'My Id': 'BOTRAN_ID',
                            'My App Id': 'BOTRAN_APP_ID'}

        message = "Here are some information about myself:\n"

        for info, key in displayable_info.items():

            message += "* **{}**: {}\n".format(info, app.config.get(key, "You're too young for that ;)"))

    elif message.get('text') == "{}info".format(disclaimer):
        room_info = ciscospark.get_room(data.roomId)
        print(room_info)
        message = "Here are some general information about this room:\n"
        for info in ['title', 'type', 'isLocked', 'sipAddress', 'created', 'lastActivity', 'id', 'creatorId']:
            message += "* **{}**: {}\n".format(info, room_info.get(info))

    elif message.get('text') == "{}list".format(disclaimer):
        message = "Hey, here is the list of attachments I've been assigned to:\n"
        for resource in file_manager.get_attachments(data.roomId):
            message += '* `{}`\n' \
                       '    * type: {}\n' \
                       '    * url: {}\n'.format(resource.name[0], resource.type, resource.link)

    elif message.get('text') == "{}zip".format(disclaimer):
        have_we_files = False
        room_info = ciscospark.get_room(data.roomId)
        message = "Here is the list of files contained in the archive: \n"
        for resource in file_manager.get_attachments(data.roomId):
            have_we_files = True
            file_manager.download_attachment(resource.link, data.roomId)
            message += "* **`{}`** from {}\n".format(resource.name[0], resource.personEmail)

        archive = file_manager.archive_directory(room_info.get('title', 'archive'), data.roomId)

        ciscospark.upload_file(archive, 'application/x-zip-compressed', data.roomId, 'archive.zip','there you go :)')
        if not have_we_files:
            message = "Nothing has been share with me yet :(\n"
            message += "To make myself useful, don't hesitate to copy me next time you attach some doc to the room!"

    else:
        message = "c'est toi !"

    ciscospark.post_message(data.roomId, markdown=message)
    return '', 204


if __name__ == '__main__':

    os.environ["SPARK_SECRET_KEY"] = app.config['BOTRAN_SECRET_KEY']
    set_up_webhook(app.config['BOTRAN_APP_ID'], app.config['BOTRAN_TARGET_URL'])

    app.run()
