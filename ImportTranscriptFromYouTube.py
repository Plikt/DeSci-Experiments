from youtube_transcript_api import YouTubeTranscriptApi
#import os
#import openai
import math
import time
import whisper


# This function pulls the transcript of YouTube videos, then writes the individual 
# lines coming from youtube into an individual text file
def FormatYouTubeTranscript(video_id,path):
    
    # Pulls transcript from youtube
    transcript = YouTubeTranscriptApi.get_transcript(video_id)

    # Preliminary code needed to initialize text cleaning
    filename = path + "transcript_" + video_id + ".txt"
    F = open(filename, "w")
    transcript_text = ""

    # Appends each line from youtube into a text file and a transcript string
    for index in range(len(transcript)):
        line = transcript[index]['text'] + " "
        F.write(line)
        transcript_text+=line

    F.close()
    return transcript_text


# This function takes an audio file and creates a transcript file from it. It functions as follows:
def GetTranscriptFromAudio(path, audiofilename):

    # Setup, define, and run Whisper
    options = whisper.DecodingOptions(language= 'en', fp16=False)
    model = whisper.load_model("base")
    result = model.transcribe(path+audiofilename)
   
    # write the content to a text file
    F = open(path+"CallTranscriptFull.txt", "w")
    F.write(result["text"])
    F.close()
    
    # Return the transcript
    transcript_text= result["text"]
    return transcript_text


# This function takes the text input from the youtube video and uses GPT3 to turn it into a cohesive 
# series of thoughts. Those can later be turned into a twitter thread
def CreateModularContent(openai, transcript_text, path):
    
    # Imports GPT3 model. Using Curie as it does a good job of summarizing text at a significantly cheaper
    # rate than DaVinci
    openai.Model.retrieve("text-curie-001")   

    # The text is summarized in 1000 word chunks. GPT3 limits text size on inputs. 1000 word segments 
    # are large enough to yeild complete and relevant thoughts. 
    countOfWords = len(transcript_text.split())
    n = 300
    
    # Preliminary code needed to initialize text cleaning
    filename = path + "summaryCleanedText" + ".txt"
    F = open(filename, "w")

    # structures the base prompt for the model
    base_prompt = "Text: what this allows to do is it creates a a tremendous abilities for applications to compete for features and not for data right so you're unbundling the data layer from the application layer and that changes the incentives it's no longer about hey creating Network effects like in web 2 when you're essentially building you know hoarding data and creating Network effects out of this horde of data that you're building out over time but rather because you've unbundled the data layer from the application layer it's all about how you're going to serve your users the best with the best set of features.\n\nCleaned text: What this allows applications to do is compete on features, not data. By unbundling the data layer from the application layer, the incentives change. It's no longer about creating network effects by hoarding data. Instead, it's all about how you can serve your users the best with the best set of features.\n\nText: "

    counter = 0
    totalIterations = math.ceil(countOfWords/n)

    # for loop that analyzes community call text using GPT3
    for t in range(totalIterations):

        # text start and end counters
        if t==0:
            start=0
        else:
            start = t * n
        end = (t+1) * n
        
        print(str(start) + " - " + str(end) + " of " + str(countOfWords))

        # extract and clean the text
        text = ' '.join(transcript_text.split()[start:end])
        text.strip()

        # A sleep counter because microsoft keeps limiting me
        if counter%30==0 and counter!=0:
            print("\nI am so sleepy\n")
            time.sleep(60)

        # Model parameters were determined through sandbox testing. Temp is fairly high to allow the model
        response = openai.Completion.create(
            model="text-curie-001",
            # prompt = "Create a list of the main points in this text." + "\n\n" + text + "\n\n",
            prompt = base_prompt + "\n\n" + text + "\n\nCleaned text:" ,
            max_tokens=400,
            temperature=0.7,
            frequency_penalty=0.5,
            presence_penalty=0.5
        ) 

        # printing in terminal because I'm impatient
        counter+=1
        print(str(counter) + " of " + str(totalIterations))
       
        # .txt formatting
        F.write(response["choices"][0]["text"])
        F.write("\n\n")

        
# This 
def CleanThoughts(path, filename, openai):

    # Imports GPT3 model. Using Curie as it does a good job of summarizing text at a significantly cheaper
    # rate than DaVinci
    openai.Model.retrieve("text-curie-001")   
    
    cleaned_file = open(path + "CleanedSumamry.txt", "w")
    raw_file = open(path+filename, "r")
    thought = raw_file.readline()
    counter = 0

    # structures the base prompt for the model
    base_prompt = "Text: what this allows to do is it creates a a tremendous abilities for applications to compete for features and not for data right so you're unbundling the data layer from the application layer and that changes the incentives it's no longer about hey creating Network effects like in web 2 when you're essentially building you know hoarding data and creating Network effects out of this horde of data that you're building out over time but rather because you've unbundled the data layer from the application layer it's all about how you're going to serve your users the best with the best set of features.\n\nCleaned text: What this allows applications to do is compete on features, not data. By unbundling the data layer from the application layer, the incentives change. It's no longer about creating network effects by hoarding data. Instead, it's all about how you can serve your users the best with the best set of features.\n\nText: "
    
    while thought:
        
        # Clean off white space for OpenAI
        thought=thought.strip()

        # Prepare full prompt
        p = base_prompt+thought+"\n\nCleaned text:"

        # Model parameters were determined through sandbox testing. Temp is fairly high to allow the model
        response = openai.Completion.create(
            model="text-curie-001",
            prompt = p,
            max_tokens=400,
            temperature=0.7,
            top_p=1,
            frequency_penalty=0.5,
            presence_penalty=0.5
        ) 

        # answer logging and .txt formatting
        cleaned_file.write(response["choices"][0]["text"])
        cleaned_file.write("\n")
        
        counter+=1
        print(counter)
        # A sleep counter because microsoft keeps limiting my creativity
        if counter%30==0 and counter!=0:
            print("\n\n\nI am so sleepy\n\n\n")
            time.sleep(60)

        thought = raw_file.readline()






#Base variables
#openai.organization = "org-6VHyHADPuVpvaocpiGuAUaPb"
#openai.api_key = "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"
path = '/Users/erikvanwinkle/Documents/Coding Projects/GPT3CommunityCall/FOSS_11-14/'

audiofilename = 'future-of-science-se_untitled-recording_erik-7c7d35045_2022-nov-14-1559pm-utc-riverside.wav'
transcript_text = GetTranscriptFromAudio(path, audiofilename)
#CleanThoughts(path, "CallTranscriptFull.txt", openai)


#filename = "CallTranscriptFull.txt"
#video_id = 'vWvYTTA_8EA'
#transcript_text = FormatYouTubeTranscript(video_id,path)
#CreateModularContent(openai, filename, path)
