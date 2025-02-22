import speech_recognition as sr
import subprocess
def process_command(command):
    if "hey alfred" in command.lower() or "knock knock" in  command.lower() or "wakeup alfred" in command.lower() or "alfred" in command.lower():
        subprocess.run(['python', 'alfred.py'])

def listen_for_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)

    try:
        print("Recognizing...")
        command = r.recognize_google(audio)
        print("Command:", command)
        process_command(command)
    except sr.UnknownValueError:
        print("Could not understand audio")
    except sr.RequestError as e:
        print("Could not request results; {0}".format(e))

while True:
    listen_for_command()
