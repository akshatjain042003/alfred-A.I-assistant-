import os
import pyttsx3
import speech_recognition as sr
import inflect

def speak(txt):
    '''
    this is the speak function which speaks to the "txt" provided by anyone
    '''
    sp = pyttsx3.init()
    sp.setProperty('rate',150)
    sp.say(txt)
    sp.runAndWait()

def recognize():
    '''
    this is recognizer and it will recognize the text by the user 

    this recognizer uses recognize_google
    '''
    while True:
        try:
            rec = sr.Recognizer()
            with sr.Microphone() as mic:
                print("Listening...")
                aud = rec.listen(mic)
            
            try:
                text = rec.recognize_houndify(aud,client_id="HJ2VRUq9tX7gTtiljAf76w==",client_key="tgde_7GtntDiLJvZeJIf5IqP3C85PFEoloKdxaz6aOd2D0JGjFMMvPQOcqprhaGBDmHE9o6v4CymtaeySrmmRA==")
                print (text)
            except sr.UnknownValueError:
                speak("Sorry i could not uncderstand!")
            except sr.RequestError:
                speak("Sorry i could not recognize maybe there is a weak network connection")
            return text
        except UnboundLocalError:
            speak("please repeate")
def movie_player(name,file_path="D:\movies"):
    
    os.chdir(file_path)
    movie_name = name.split()
    lst = os.listdir(file_path)
    matching_movie = None
    for movie in lst:
        if all(word in movie.lower() for word in movie_name):
            matching_movie = movie

    if matching_movie:
        if os.path.isfile(matching_movie):
            os.startfile(matching_movie)
        else:
            while True:
                try:
                    episode = {}
                    speak("which episode or part do you want to watch:\t")
                    reco = recognize()
                    num = inflect.engine()
                    for i in range(1, 30):

                        episode[f"episode{i}"]= f"e{i:02d}"
                        episode[f"{i}"]= f"e{i:02d}"
                        p = i
                        wordsofnum = num.number_to_words(p)
                        episode[f"episode{wordsofnum}"] =f"e{i:02d}"
                    final_inp = reco.replace(" ","")
                    inp1 = final_inp.split()
                    ans = [episode[word] for word in inp1]
                    res = "".join(ans)
                    print (res)
                    item_path = os.path.join(file_path,matching_movie)
                    movie_player(res,file_path=item_path)   
                    break 
                except KeyError:
                    speak("Please name correct episode")
    else:
        speak("not found, do you want to enter the name?")
        reco = recognize()
        if "yes"in reco.lower() or "sure" in reco.lower():
            speak("enter the name:")
            inp = input("enter the name:\t ")
            movie_player(inp)



