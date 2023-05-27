import speech_recognition as sr


if __name__ == "__main__":

    # obtain audio from the microphone
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say something!")
        audio = r.listen(source)

    # recognize speech using whisper
    try:
        response = r.recognize_whisper(audio, language="english", show_dict=True)
        print("Whisper thinks you said: ", response)
    except sr.UnknownValueError:
        print("Whisper could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Whisper")