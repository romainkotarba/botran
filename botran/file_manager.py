import collections
import os
import re

import shutil

import ciscospark
import utils
from requests_toolbelt import MultipartEncoder

Attachment = collections.namedtuple('attachment', 'id personId personEmail text type created link name')
SPARK_API_URL = "https://api.ciscospark.com/v1/"


def main():
    BOTRAN_SECRET_KEY = 'MDczMDJlN2YtN2EwYy00NGQwLWI1ZTAtNjE3NGJmN2EzYTNlZTM0OGZhMzEtYTIx'
    try:
        os.environ['SPARK_SECRET_KEY'] = BOTRAN_SECRET_KEY
    except KeyError as e:
        print("No secret key found for Spark. Access to API will be restricted...")
        return

    # Serverless
    test_room = 'Y2lzY29zcGFyazovL3VzL1JPT00vNjVkNTE0ZjAtYzA2Ni0xMWU3LWE3ZWMtNWQxZjZkYzk1ODE4'
    # Les Miserables
    test_room = 'Y2lzY29zcGFyazovL3VzL1JPT00vOTJmNjc0YjAtYjJhNi0xMWU3LTkzOWItNTdmNzU0NjY4NGY1'
    # Avec les bots on est mieux
    # test_room = 'Y2lzY29zcGFyazovL3VzL1JPT00vMDA4MTI5OTAtYmFmOC0xMWU3LTkyNDctZmI4OGIzZDhiMTJi'

    # pp = pprint.PrettyPrinter(indent=4)
    # room_info = ciscospark.get_room(test_room)
    # ciscospark.register_webhook('Botran-{}-{}'.format(room_info.get('title'), test_room), 'https://2271b9be.ngrok.io',
    #                             'messages', 'all', 'roomId={}'.format(test_room))

    # ciscospark.upload_file('archive/Les Misérables.zip', test_room, 'there you go :)')
    ciscospark.upload_file('data/Y2lzY29zcGFyazovL3VzL1JPT00vOTJmNjc0YjAtYjJhNi0xMWU3LTkzOWItNTdmNzU0NjY4NGY1/Airbus DS LCS Conciergerie.PNG', test_room, 'there you go :)')

    # ciscospark.delete_webhooks("roomId=Y2lzY29zcGFyazovL3VzL1JPT00vMmNmNTdlYTAtMzVkMi0xMWU3LTg4N2UtNDE0ZTk2M2Q0ZTcz")

    # print("report on shared docs so far in this room:")
    # for resource in get_attachments(test_room):
    #     print("* Type: {}, name: {}, link: {}".format(resource.type, resource.type, resource.link))
    # for resource in resources:
    #     if resource.type == 'file':


def archive_directory(output, directory):
    output_name = os.path.join('archive', output)
    try:
        shutil.make_archive(output_name, 'zip', os.path.join('data', directory))
    except FileNotFoundError:
        return False
    return "{}.zip".format(output_name)


def download_attachment(url, location=None):
    resp = ciscospark.get_resource(url)
    content = resp.headers.get('content-disposition')

    file_name = re.findall('filename="(.+)"', content)
    if file_name:
        if not os.path.exists(os.path.join('data', location)):
            os.makedirs(os.path.join('data', location))
        with open(os.path.join('data', location, file_name[0]), 'wb') as f:
            resp.raw.decode_content = True
            shutil.copyfileobj(resp.raw, f)

        return file_name[0]
    else:
        return


def get_attachments(room_id):

    resources = []
    # This function returns a generator
    for m in ciscospark.list_messages(room_id, mention=True):
        urls = utils.find_url_in_string(m.get('text'))
        if urls:
            for url in urls:
                yield Attachment(m['id'], m['personId'], m['personEmail'], m.get('text'), url, m['created'], 'link')

        if m.get('files'):
            for file in m.get('files'):
                resp = ciscospark.get_resource(file)
                content = resp.headers.get('content-disposition')
                type_file = resp.headers.get('Content-Type')
                file_name = re.findall('filename="(.+)"', content)

                yield Attachment(m['id'], m['personId'], m['personEmail'], m.get('text'), type_file, m['created'], file, file_name)


if __name__ == '__main__':
    main()
#         download_attachment(resource.type)