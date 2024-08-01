import pyttsx3 as p
import speech_recognition as sr
import webbrowser
import requests
from datetime import datetime
import openai
import os
import time

# Initialize OpenAI API key securely
openai.api_key = os.getenv('OPENAI_API_KEY', 'your_ApI_key')

# Initialize the text-to-speech engine
engine = p.init()
engine.setProperty('rate', 130)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

# Function to speak text
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to write text to a file
def write_to_file(text):
    with open('transcription.txt', 'a') as file:
        file.write(text + '\n')

# Function to listen and recognize speech
def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)
    try:
        text = r.recognize_google(audio).lower()
        write_to_file(text)  # Write the recognized text to a file
        print(f"Recognized: {text}")  # Print recognized text to the console
        return text
    except sr.UnknownValueError:
        speak("Sorry, I did not understand that.")
        return ""
    except sr.RequestError:
        speak("Sorry, my speech service is down.")
        return ""

# Function to interact with OpenAI API for Q&A
def ask_chatgpt(question):
    try:
        response = openai.Completion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": question}
            ],
            temperature=0.5,
            max_tokens=150
        )
        answer = response.choices[0].message['content'].strip()
        return answer
    except Exception as e:
        print(f"An error occurred: {e}")
        return "Sorry, there was an error processing your request."

# Function to search Google
def search_google(query):
    speak(f"Searching for {query} on Google")
    webbrowser.open(f"https://www.google.com/search?q={query}")

# Function to search Wikipedia
def search_wikipedia(query):
    speak(f"Searching for {query} on Wikipedia")
    webbrowser.open(f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}")

# Function to play a YouTube video
def play_youtube_video(query):
    speak(f"Playing {query} on YouTube")
    webbrowser.open(f"https://www.youtube.com/results?search_query={query}")

# Function to get weather information
def get_weather(location):
    api_key = os.getenv('OPENWEATHERMAP_API_KEY', 'your_openweathermap_api_key_here')
    base_url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}"
    response = requests.get(base_url)
    if response.status_code == 200:
        data = response.json()
        temp = data['main']['temp'] - 273.15  # Convert from Kelvin to Celsius
        description = data['weather'][0]['description']
        speak(f"The current temperature in {location} is {temp:.1f} degrees Celsius with {description}.")
    else:
        speak(f"Sorry, I couldn't retrieve the weather for {location}.")

# Function to set a reminder
def set_reminder(reminder_text, time_in_minutes):
    speak(f"Setting a reminder for {reminder_text} in {time_in_minutes} minutes.")
    time.sleep(time_in_minutes * 60)
    speak(f"Reminder: {reminder_text}")

# Function to tell the current time
def tell_time():
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    speak(f"The current time is {current_time}.")

# Main function for the assistant
def main():
    speak("Hello, I'm DD's Voice Assistant. How can I help you today?")

    while True:
        text = listen()

        if "how are you" in text:
            speak("I'm just a computer program, but I'm functioning as expected. How can I assist you?")

        elif "play" in text:
            if "youtube" in text:
                speak("What would you like to watch?")
                query = listen()
                if query:
                    play_youtube_video(query)
            else:
                speak("What song would you like to play?")
                query = listen()
                if query:
                    play_youtube_video(query)

        elif "weather" in text:
            speak("Please specify the location.")
            location = listen()
            if location:
                get_weather(location)

        elif "reminder" in text:
            speak("What would you like to be reminded about?")
            reminder_text = listen()
            speak("In how many minutes?")
            try:
                time_in_minutes = int(listen())
                set_reminder(reminder_text, time_in_minutes)
            except ValueError:
                speak("Sorry, I didn't get the time. Please try again.")

        elif "time" in text:
            tell_time()

        elif "search" in text:
            if "wikipedia" in text:
                speak("What do you want to search for on Wikipedia?")
                query = listen()
                if query:
                    search_wikipedia(query)
            else:
                speak("What do you want to search for on Google?")
                query = listen()
                if query:
                    search_google(query)

        elif any(keyword in text for keyword in ["who", "what", "when", "where", "why", "how"]):
            speak("Searching for the answer.")
            answer = ask_chatgpt(text)
            speak(answer)
            write_to_file(f"Question: {text}")
            write_to_file(f"Answer: {answer}")

        elif "exit" in text or "quit" in text:
            speak("Goodbye!")
            break

        else:
            speak("Sorry, I didn't catch that. Can you please repeat?")

if __name__ == "__main__":
    main()
