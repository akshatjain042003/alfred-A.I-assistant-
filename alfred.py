

import streamlit as st
import pyttsx3
import speech_recognition as sr
import datetime
import AppOpener as ao
import psutil
import webbrowser
import random
import os
import time
# import spotify_func
from pywinauto import Application
import mvoies_folder as mf
import openai  # Import the OpenAI library
from google import genai
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import re
from dotenv import load_dotenv
load_dotenv()


def speak(txt):
    '''
    This is the speak function which speaks the "txt" provided by anyone.
    '''
    sp = pyttsx3.init()
    sp.setProperty('rate', 150)
    sp.say(txt)
    sp.runAndWait()

def recognize():
    '''
    This is the recognizer function, and it will recognize the text spoken by the user.
    This recognizer uses recognize_google.
    '''
    while True:
        try:
            rec = sr.Recognizer()
            with sr.Microphone() as mic:
                print("Listening...")
                aud = rec.listen(mic)
            
            try:
                text = rec.recognize_google(aud)
                print(text)
                return text
            except sr.UnknownValueError:
                speak("Sorry, I could not understand!")
            except sr.RequestError:
                speak("Sorry, I could not recognize. Maybe there is a weak network connection.")
        except Exception as e:
            speak("An error occurred. Please try again.")
            print(f"Error: {e}")

# Spotify API credentials
SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = 'http://localhost:8502'  # No /callback route needed

# Initialize Spotify OAuth
sp_oauth = SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope="user-library-read,user-modify-playback-state"  # Add required scopes
)

# Function to handle Spotify authentication
def authenticate_spotify():
    auth_url = sp_oauth.get_authorize_url()
    st.write(f"Please authorize the app by visiting this URL: [Authorize Spotify]({auth_url})")
    st.write("After authorizing, you will be redirected to a URL. Paste the **full URL** from your browser's address bar below.")

    # Get the redirected URL from the user
    redirected_url = st.text_input("Enter the full URL you were redirected to:")
    if redirected_url:
        # Extract the authorization code from the URL fragment
        if "#" in redirected_url:
            fragment = redirected_url.split("#")[1]
            params = dict(pair.split("=") for pair in fragment.split("&"))
            if "access_token" in params:
                st.success("Successfully authenticated with Spotify!")
                return params  # Return the token info
            else:
                st.error("Failed to retrieve access token.")
        else:
            st.error("Invalid URL. Please try again.")
    return None

# Function to play music on Spotify
def play_spotify_song(song_name, token_info):
    sp = spotipy.Spotify(auth=token_info['access_token'])
    results = sp.search(q=song_name, limit=1, type='track')
    if results['tracks']['items']:
        track_uri = results['tracks']['items'][0]['uri']
        sp.start_playback(uris=[track_uri])
        st.write(f"Now playing: {results['tracks']['items'][0]['name']}")
    else:
        st.error("Song not found.")

def wish():
    hr = int(datetime.datetime.now().hour)
    if hr>=00 and hr<12:
        speak("Good morning")
    elif hr>=12 and hr<16:
        speak("Good afternoon")
    else:
        speak("Good evening")

def frame(ans):
    '''
    Return the predefined answer corresponding to the most similar question.
    '''
    an = random.choice(ans)
    predefined_answers = an
    return predefined_answers

def rettime(respo):
    '''
    Perform operations related to time and date.
    '''
    if respo == "time":
        curtime = datetime.datetime.now().strftime("%H:%M")
        ans = [f"It's {curtime}",
               f"The current time is {curtime}",
               f"It's {curtime}",
               f"Yes, I have the time. It's {curtime}"]
    elif respo == "date":
        date = datetime.date.today()
        ans = [f"It's {date}",
               f"The current date is {date}",
               f"It's {date}",
               f"Yes, I have the date. It's {date}"]
    return frame(ans)

def apps_links(response):
    '''
    This speaks a command to open any app you pass in response.
    '''
    ans = ["Here you go!",
           f"Opening {response}",
           f"Yes, sure. Opening {response}"]
    return frame(ans)

def close_app_open(appname, name):
    '''
    This function closes the app which is running on the PC.
    The app that you pass will be closed using AppOpener.
    '''
    for proc in psutil.process_iter(['pid', 'name']):
        if appname.lower() in proc.info['name'].lower():
            speak(f"Closing {name}")
            ao.close(name)
            return
    speak(f"{name} is not running.")

def check_link_open(link, name):
    '''
    This function checks if a specific link is open in Chrome.
    '''
    try:
        app = Application(backend='uia')
        app.connect(title_re=".*Chrome.*")
        element_name = "Address and search bar"
        dlg = app.top_window()
        url = dlg.child_window(title=element_name, control_type="Edit").get_value()
        if url == link:
            speak(f"Closing {name}")
    except Exception as e:
        speak(f"Could not check the link. Error: {e}")

def searching_things(search_text):
    '''
    This function searches for the video asked by the user on YouTube.
    '''
    if not search_text.strip():
        speak("Please provide a valid search term.")
        return
    format_search = search_text.replace(" ", "+")
    url = f"https://www.youtube.com/results?search_query={format_search}"
    webbrowser.open(url)

def clean_response(response):
    # Remove Markdown formatting
    response = re.sub(r'\*\*(.*?)\*\*', r'\1', response)  # Remove bold
    response = re.sub(r'_(.*?)_', r'\1', response)        # Remove italics
    response = response.replace("*", "")                  # Remove asterisks
    return response

def ask_chatgpt(question):
    '''
    This function sends the user's question to ChatGPT and returns the response.
    '''
    try:
        client = genai.Client(api_key=os.getenv("GENAI_API_KEY"))
        response = client.models.generate_content(
            model="gemini-2.0-flash", contents=f"Provide a concise and short answer to the following question: {question}"
        )
        # Extract the assistant's reply from the response
        
        assistant_reply = clean_response(response.text)
        print(assistant_reply)
        return assistant_reply
    except Exception as e:
        return f"Sorry, I couldn't process your request. Error: {e}"

def handle_time_questions(q):
    '''
    Handle time and date-related questions.
    '''
    if "time" in q.lower():
        speak(rettime("time"))
        return True
    elif "date" in q.lower():
        speak(rettime("date"))
        return True
    else:
        return False

def handle_app_questions(q):
    '''
    Handle app-related questions (e.g., opening/closing apps).
    '''
    if "open" in q.lower() and "whatsapp" in q.lower():
        if "close" in q.lower():
            close_app_open("WhatsApp.exe", "whatsapp")
        else:
            speak(apps_links("WhatsApp"))
            ao.open("whatsapp")
        return True
    elif "open" in q.lower() and "chrome" in q.lower():
        if "close" in q.lower():
            close_app_open("chrome.exe", "chrome")
        else:
            speak(apps_links("chrome"))
            ao.open("google chrome")
        return True
    elif "open" in q.lower() and "spotify" in q.lower() or "music" in q.lower() or "song" in q.lower():
        if "close" in q.lower():
            close_app_open("Spotify.exe", "spotify")
        else:
            speak("Tell me the name of the song you want to listen to on Spotify.")
            song = recognize()
            speak(apps_links("Spotify"))
            # spotify_func.music(song)
        return True
    elif "open" in q.lower() and "movie" in q.lower():
        speak("Which movie do you want to watch?")
        mov = recognize()
        mf.movie_player(mov)
        return True
    else:
        return False
    

def handle_general_questions(q):
    '''
    Handle general questions (e.g., who are you, who made you).
    '''
    if "who are you" in q.lower() or "your name" in q.lower():
        speak("I'm Alfred, your assistant.")
        return True
    elif "who made you" in q.lower() or "created you" in q.lower():
        speak("Akshat Jain created me.")
        return True
    else:
        return False
    

def questions(q):
    '''
    Main function to handle all types of questions.
    '''
    if handle_time_questions(q) or handle_app_questions(q) or handle_general_questions(q):
        print ("not asking gemini")
    
    elif "open" in q.lower() and "youtube" in q.lower():
        speak("Can I search for the video you are looking for?")
        c = recognize()
        if "no" in c.lower() or "not" in c.lower():
            speak("Okay, you want to search yourself.")
            speak("Opening YouTube.")
            webbrowser.open("https://www.youtube.com/")
        else:
            if "yes" in c.lower() or "sure" in c.lower():
                speak("Okay, name the video.")
                b = recognize()
                searching_things(b.lower())
            else:
                searching_things(c.lower())
    else:
        speak("Let me think about that...")
        response = ask_chatgpt(q)
        speak(response)

# Streamlit App
def main():
    st.title("Alfred - Your Voice Assistant")
    st.write("Welcome to Alfred! Speak or type your command below.")

    # Input for user command
    user_input = st.text_input("Enter your command:")

    if st.button("Submit"):
        if user_input:
            st.write(f"You said: {user_input}")
            questions(user_input)
        else:
            st.warning("Please enter a command.")

    if st.button("Speak Command"):
        st.write("Listening...")
        command = recognize()
        st.write(f"You said: {command}")
        questions(command)

    if st.button("Exit"):
        st.write("Goodbye!")
        speak("Goodbye!")
        st.stop()

if __name__ == "__main__":
    main()