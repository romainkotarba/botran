import os
import requests
from requests_toolbelt import MultipartEncoder

SPARK_API_URL = "https://api.ciscospark.com/v1/"


def set_spark_header(spark_secret_key=None, content_type='application/json; charset=utf-8'):
    """
    Set header for Cisco Spark API requests
    :return: JSON header for HTTP requests
    """

    if not spark_secret_key:
        spark_secret_key = os.environ.get("SPARK_SECRET_KEY")

    token = "Bearer {}".format(spark_secret_key)
    spark_header = {'Authorization': token, 'Content-Type': content_type}
    return spark_header


def list_members(room_id):

    api_node = "{}memberships".format(SPARK_API_URL)
    headers = set_spark_header()
    payload = {
        'roomId': room_id
    }
    resp = requests.get(api_node, params=payload, headers=headers)

    if resp.status_code != 200:
        print("Error querying API: {} {}".format(resp.status_code, resp.text))
        print()
        return

    return resp.json()


def list_rooms():
    """
    Lists all cisco spark rooms a user belongs to.
    :return: JSON list of all rooms
    """

    headers = set_spark_header()
    api_node = "{}rooms".format(SPARK_API_URL)
    resp = requests.get(api_node, headers=headers)

    if resp.status_code != 200:
        print("Error querying API: {} {}".format(resp.status_code, resp.text))
        return

    return resp.json()


def get_room(room_id):
    """
    Given a room id, return JSON describing the room
    :param room_id: the id of the room.
    :return: JSON list of the room
    """

    headers = set_spark_header()
    api_node = "{}rooms/{}".format(SPARK_API_URL, room_id)
    resp = requests.get(api_node, headers=headers)

    if resp.status_code != 200:
        print("Error querying API: {} {}".format(resp.status_code, resp.text))
        return

    return resp.json()


def get_message(message_id):
    """
    Shows details for a message, by message ID.
    :param message_id: Specify the message ID in the messageId parameter in the URI.
    :return: message details formatted in JSON 
    """

    api_node = "{}messages/{}".format(SPARK_API_URL, message_id)
    headers = set_spark_header()

    resp = requests.get(api_node, headers=headers)

    if resp.status_code != 200:
        print("Error querying API: {} {}".format(resp.status_code, resp.text))
        print()

    return resp.json()


def post_message(room_id, text=None, markdown=None):
    """
    Post a message to a room
    
    :param room_id: The ID of the room to post in
    :param text: the message to post
    :return: nada
    """

    api_node = "{}messages".format(SPARK_API_URL)
    headers = set_spark_header()
    payload = {
        'roomId': room_id,
        'text': text,
        'markdown': markdown
    }
    resp = requests.post(api_node, json=payload, headers=headers)

    if resp.status_code != 200:
        print("Error querying API: {} {}".format(resp.status_code, resp.text))
        print()

    return True


def invite_user(attendee, room_id):
    """
    Add user to a Cisco Spark room
    :param attendee: email or id of person to add
    :param room_id: room id for membership
    :return: 
    """

    print('* invite {}: {} ({})'.format(attendee.type, attendee.fullname, attendee.email))

    api_node = "{}memberships".format(SPARK_API_URL)
    headers = set_spark_header()
    payload = {
        'roomId': room_id,
        'personEmail': attendee.email
    }
    resp = requests.post(api_node, json=payload, headers=headers)

    if resp.status_code != 200:
        print("Error querying API: {} {}".format(resp.status_code, resp.text))
        print()
        return

    print("User added successfully :)")
    print()
    return resp.json()



def remove_user(attendee, room_id):
    """
    Remove a user from a Cisco Spark room
    :param attendee: email or id of person to add
    :param room_id: room id for membership
    :return: 
    """

    print('* Remove user {}: {} ({})'.format(attendee.type, attendee.fullname, attendee.email))

    members = list_members(room_id)

    membership = [m['id'] for m in members['items'] if attendee.email == 'personEmail']
    if not membership:
        return

    api_node = "{}memberships".format(SPARK_API_URL)
    headers = set_spark_header()

    for m in membership:
        payload = {
            'roomId': room_id,
            'personEmail': m
        }

        # resp = requests.delete(api_node, json=payload, headers=headers)
        #
        # if resp.status_code != 200:
        #     print("Error querying API: {} {}".format(resp.status_code, resp.text))
        #     print()
        #     return
        #
        # print("User removed successfully :)")
        # print()
    return


def list_messages(room_id, mention=None):
    if mention:
        api_node = "{}messages?mentionedPeople=me".format(SPARK_API_URL)
    else:
        api_node = "{}messages".format(SPARK_API_URL)
    headers = set_spark_header()
    payload = {
        'roomId': room_id
    }

    resp = requests.get(api_node, params=payload, headers=headers)

    if resp.status_code != 200:
        print("Error querying API: {} {}".format(resp.status_code, resp.text))
        return

    while True:
        if resp.status_code == 200:
            for m in resp.json().get('items'):
                yield m

        # Grab next pages if result has too much items
        # https://developer.ciscospark.com/pagination.html
        if resp.links.get('next'):
            url = resp.links.get('next').get('url')
            resp = requests.get(url, headers=headers)
        else:
            break


def find_attachment(message):
    if message.get('files'):
        headers = set_spark_header()
        for file_link in message.get('files'):
            resp = requests.get(file_link, headers=headers, stream=True)
            # print(resp.headers)


def get_resource(url):
    headers = set_spark_header()
    resp = requests.get(url, headers=headers, stream=True)
    if resp.status_code == 200:
        return resp
    else:
        return


def get_webhooks(max_response_items=None):
    if max_response_items:
        api_node = "{}webhooks?max={}".format(SPARK_API_URL, max_response_items)
    else:
        api_node = "{}webhooks".format(SPARK_API_URL)
    headers = set_spark_header()

    resp = requests.get(api_node, headers=headers)
    # requests.exceptions.ConnectionError
    if resp.status_code != 200:
        print("Error querying API: {} {}".format(resp.status_code, resp.text))
        print()
        return

    return resp.json()


def delete_webhooks(to_filter):
    print('* delete webhooks matching: {}'.format(to_filter))
    headers = set_spark_header()

    webhooks_list = get_webhooks()
    for webhook in webhooks_list.get('items'):

        webhook_filter = webhook.get('filter')

        if webhook_filter == to_filter:
            api_node = "{}webhooks/{}".format(SPARK_API_URL, webhook.get('id'))
            resp = requests.delete(api_node, headers=headers)
            if resp.status_code == 204:
                print("Deleted Webhook: {}".format(webhook.get('name')))

    return


def delete_webhook(webhook_id):
    print('* delete webhook: {}'.format(webhook_id))

    api_node = "{}webhooks/{}".format(SPARK_API_URL, webhook_id)
    headers = set_spark_header()

    resp = requests.delete(api_node, headers=headers)

    if resp.status_code != 204:
        print("Error querying API: {} {}".format(resp.status_code, resp.text))
        print()
        return

    print("Webhook successfully deleted :)")
    print()
    return resp.json()


def register_webhook(name, target_url, resource, event, filter=None):
    """
    Add a webhook to a Cisco resource
    for official documentation about API endpoint:
    https://developer.ciscospark.com/endpoint-webhooks-post.html
    
    :param name: A user-friendly name for this webhook.
    :param target_url: The URL that receives POST requests for each event.
    :param resource: The resource type for the webhook. Creating a webhook requires 'read' 
    scope on the resource the webhook is for.
    :param event: The event type for the webhook.
    :param filter: The filter that defines the webhook scope.
    :return: JSON object returned by API
    """

    print('* instantiate new webhook {}: {} {} {} {}'.format(name, target_url, resource, event, filter))

    api_node = "{}webhooks".format(SPARK_API_URL)
    headers = set_spark_header()
    payload = {
        'name': name,
        'targetUrl': target_url,
        'resource': resource,
        'event': event,
        'filter': filter
    }
    resp = requests.post(api_node, json=payload, headers=headers)

    if resp.status_code != 200:
        print("Error querying API: {} {}".format(resp.status_code, resp.text))
        print()
        return

    print("Webhook successfully created :)")
    print()
    return resp.json()


def upload_file(file_path, mime_type, room_id, post_file_name, message):
    print('* upload new file {}: to {}'.format(file_path, room_id))

    api_node = "{}messages".format(SPARK_API_URL)

    payload = {
        'roomId': room_id,
        'text': message,
        'files': (post_file_name, open(file_path, 'rb'), mime_type)
    }

    m = MultipartEncoder(fields=payload)
    headers = set_spark_header(content_type=m.content_type)
    resp = requests.post(api_node, data=m, headers=headers)

    if resp.status_code != 200:
        print("Error querying API: {} {}".format(resp.status_code, resp.text))
        print()
        return

    print("Webhook successfully created :)")
    print()
    return resp.json()

