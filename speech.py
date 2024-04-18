import speech_recognition as sr
import pymysql
import pyttsx3
import tkinter as tk
import spacy
from dateutil import parser
import datetime


# Load English tokenizer, tagger, parser and NER
nlp = spacy.load("en_core_web_sm")
# database connection
connection = pymysql.connect(host="localhost", port=3306, user="root", passwd="", database="speech")

# Create a cursor object
cursor = connection.cursor()
engine = pyttsx3.init()
engine.setProperty("rate", 150)



def add_todatabase():
    recognizer = sr.Recognizer()

    print("hi,in add_todatabse")
    # Use the microphone as the audio source
    task = "Your task value"
    date_task = "2023-02-19"
    time_task = "6pm"
    with sr.Microphone() as source:
        engine.say("Please tell me the event")
        engine.runAndWait()
        audio_data = recognizer.listen(source)
        engine.say("yes Processing...")

    try:
        task = recognizer.recognize_google(audio_data)
        print(task)
        if("tomorrow" in task):
            current_date=datetime.date.today()
            date_task= current_date + datetime.timedelta(days=1)
        else:
            date_time = parser.parse(task, fuzzy=True)
            date_only = date_time.date()
            print(date_only)
            date_task=str(date_only)
        # Define the SQL INSERT statement
        # insert_sql = "insert into task_data values(text,2023-02-19,6pm)"
        insert_sql = "INSERT INTO task_data values('{}','{}','{}')".format(task, date_task, time_task)

        # Execute the SQL statement
        cursor.execute(insert_sql)
        engine.say("its set")
        engine.runAndWait()

        # Commit the changes to the database
        connection.commit()
    # Close the cursor and the database connection
    except Exception as e:
        print(f"Error: {e}")
        connection.rollback()
        raise  # Re-raise the excepti
    
        # cursor.close()
        # connection.close()


def show(date_only):
    engine.say("here's your list")
    engine.runAndWait()
    if(date_only ==""):
        insert_sql = "select * from task_data"
        cursor.execute(insert_sql)
    else:
        insert_sql = "SELECT task FROM task_data WHERE date_task = %s"
        # Execute the query with the parameter
        cursor.execute(insert_sql, (date_only,))
    result = cursor.fetchall()
    for data in result :
        print(data)
        engine.say(data)
        engine.runAndWait()

    #engine.say("sorry not there")
   
    #engine.runAndWait()


def transcribe_audio():
    # engine.say("Hello There !")
    engine.runAndWait()
    recognizer = sr.Recognizer()

    # Use the microphone as the audio source
    with sr.Microphone() as source:
        engine.say("Hello there , what can i do for u")
        engine.runAndWait()
        audio_data = recognizer.listen(source)
        print("Processing...")

    try:
        text = recognizer.recognize_google(audio_data)
        doc=nlp(text)
        # Extracting only the date
        #date_only = date_time.date()
        print("Transcript: " + text)
        # Analyze syntax
        # Analyze syntax
        noun=[chunk.text for chunk in doc.noun_chunks]
        verb= [token.lemma_ for token in doc if token.pos_ == "VERB"]
        
        print(noun,verb)
        if ("task" in text and "set" in verb  ):
            # print("yes , pls tell the event ")
            add_todatabase()

        elif ("show" in text):
             
            if("tomorrow" in text):
                current_date=datetime.date.today()
                date_task= current_date + datetime.timedelta(days=1)
                show(str(date_task))
            

            else:
                date_time = parser.parse(text, fuzzy=True)
                date_only = date_time.date()
                show(str(date_only))
        elif ("remove" in verb or "delete" in verb or "drop" in verb or "cancel" in verb):
                print("in delete")
                delete_task(text)  
            
        else:
            engine.say("Sorry i couldnt understand")
            engine.runAndWait()
    except sr.UnknownValueError:
        engine.say("sorry i couldnt understand")
    except sr.RequestError as e:
        engine.say("Could not request results from Google Speech Recognition service; pls check your internet")

def delete_task(text):
    text=text.lower()
    s=text.split()
    print(s)
    s.remove(s[0])
    s.remove(s[0])
    s = ' '.join(s)
    print(s)
    remove="DELETE FROM task_data WHERE task=%s"
    try:
        cursor.execute(remove,(s,))
        connection.commit()
        engine.say("its deleted ")
    except:
        engine.say("an error occured ")
        

# Function to start voice recognition
#def start_voice_recognition():
    #main()

# Tkinter GUI
#class TaskManagementApp(tk.Tk):
    #def __init__(self):
        #tk.Tk.__init__(self)
        #self.title("Task Management App")

        # Add a button to start voice recognition
        #self.start_button = tk.Button(self, text="Start Voice Recognition", command=start_voice_recognition)
        #self.start_button.pack(pady=20)

# Create an instance of the Tkinter app
#app = TaskManagementApp()

# Start the Tkinter main loop
#app.mainloop()


#transcribe_audio()

