import argparse

from shikoni.ShikoniClasses import ShikoniClasses
from shikoni.tools.ShikoniInfo import start_shikoni_api
from shikoni.base_messages.ShikoniMessageConnectorSocket import ShikoniMessageConnectorSocket
from shikoni.base_messages.ShikoniMessageRun import ShikoniMessageRun


from shikoni.message_types.ShikoniMessageString import ShikoniMessageString

import speech_recognition as sr


def on_message(msg, shikoni: ShikoniClasses):
    group_name = msg["group_name"]
    messages = msg["messages"]
    do_run = 0
    for key, message in messages.items():
        if isinstance(message, ShikoniMessageRun):
            do_run += 1
    if do_run < len(messages):
        return

    tts_json = get_tts_json(language="english")
    text = tts_json["text"]
    shikoni.send_to_all_clients(message=ShikoniMessageString(text), group_name=group_name)


def get_tts_json(language="english"):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say something!")
        audio = r.listen(source)

    # recognize speech using whisper
    try:
        return r.recognize_whisper(audio, language=language, show_dict=True)
    except sr.UnknownValueError:
        print("Whisper could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Whisper")
    return {}


def start_server(server_port: int, api_server_port: int, on_message_call):
    shikoni = ShikoniClasses(message_type_decode_file="data/massage_type_classes.json",
                             default_server_call_function=on_message_call)

    # to search for free ports as client
    api_server = start_shikoni_api(api_server_port)

    # start the websocket server
    # if start_loop is false, no messages will be handled
    shikoni.start_base_server_connection(
        connection_data=ShikoniMessageConnectorSocket().set_variables(url="0.0.0.0",
                                                                      port=server_port,
                                                                      is_server=True,
                                                                      connection_name="001"),
        start_loop=True)

    # close
    shikoni.close_base_server()
    api_server.terminate()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Skikoni Server")
    parser.add_argument("-p", "--port", dest="port", type=int, help="server port ()")
    parser.add_argument("--api", dest="api_port", type=int, help="api server port (PORT + 1)")

    args = parser.parse_args()
    server_port = 19998
    if args.port:
        server_port = args.port
    api_server_port = server_port + 1
    if args.api_port:
        api_server_port = args.api_port

    start_server(server_port=server_port, api_server_port=api_server_port, on_message_call=on_message)
