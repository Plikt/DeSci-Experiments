from youtube_transcript_api import YouTubeTranscriptApi
#import os
import openai
import math
import time
import soundfile as sf
import matplotlib.pyplot as plt

import whisper

from simple_diarizer.diarizer import Diarizer as diar
from simple_diarizer.utils import combined_waveplot



# This function takes an audio file and creates a transcript file from it. It functions as follows:
def GetTranscriptFromAudio(path, audiofilename):

    # Setup, define, and run Whisper
    options = whisper.DecodingOptions(language= 'en')
    model = whisper.load_model("base")
    result = model.transcribe("chris.wav")
   
    
    #for i in audiofilename.segments: 
        #result += model.transcribe(path+audiofilename[i]) + "\n\n"
   
    # write the content to a text file

    F = open('/Users/desot1/Documents/GitHub/DeSci-Experiments/'+ audiofilename + ".txt", "w")
    F.write(result["text"])
    F.close()
    
    # Return the transcript
    transcript_text= result["text"]
    return transcript_text


# This function takes the text input from the youtube video and uses GPT3 to turn it into a cohesive 
# series of thoughts. Those can later be turned into a twitter thread
#def CreateModularContent(openai, transcript_text, path):

    #META: Ways to do this
    #Break this into large chunks via the diarizer (comm calls) -> Summarize the one large chunk. 
    #Mechanically break into slightly more reasonable chunks by ending at end of sentence. 
    #  Separate into thoughts -> summarize each paragraph. + Summarize paragraphs. 
    #Manual
    #Other? The thoughts would be training. 
    

    

    

#this function would run each of the paragraphs from CreateModularContent and classify it using preset topics
#NOTE: I'm not sure how effective this would be -> do you have other thoughts on how we might create a
#rich set of methods for understanding how we might develop a method of creating /chunks of the text (Presumably besides you doing it)
#def Classify(topics, path, filename, openai):
    #this forloop runs through the topics and classifies each of the thoughts
    #for i in range(length(topics)): 
        #print("help")

#this returns a summary instead of a raw transcript. 
#path: the path where you want to store the output file + where you have the input file
#filename: Name of the input file
#openai: API and other info for GPT
#aggregate: How many "thoughts" do you want to put together per summary? 
#iterations: How many times do you want to make another summary?
def SummarizeThoughts(path, filename, openai, aggregate, iterations): 
    # Imports GPT3 model. Using Curie as it does a good job of summarizing text at a significantly cheaper
    # rate than DaVinci

    openai.Model.retrieve("text-davinci-002")
    cleaned_file = open(path + "CleanedSummary" + str(iterations) + ".txt", "w")
    raw_file = open(path+filename, "r")
    #raw_file = raw_file.strip()
    thought = raw_file.readline()
    for i in range(aggregate-1): 
        thought += raw_file.readline()
    counter = 0

    


    # structures the base prompt for the model
    base_prompt = "Paragraph:In particular the last five years has been full time at this organization called the GoFair Foundation. These slides are available. differences that are in here too. Okay, so what is this idea going fair and doing fair? So this presentation will be in two parts and the first part going fair is really about kind of the history of where this idea came from about fair and kind of how it's matured up until today and then in the next section on doing fair, just to kind of give you a snapshot of some state of the art developments right now on the implementation of the fair principles and kind of, you know, the doors that opens up to kind of a new way of looking at computing and a new way of doing information exchange and being able to access larger amounts of data for kind of, you know, distributed learning type analyses.\nSummary:What is going and doing fair? We’ll break this down into two parts - first we’ll explore the history of fair and how it has matured until today, then we’ll explore the implementation of the Fair principles as a novel method of computing, information exchange, and distributed learning analysis.\nParagraph:Okay, so I'm going to start here with a picture from, that I took in 2019 in the gentleman at the podium, his name is George Straun and in 1995, he was the director of something called the NSF Net, the National Science Foundation Network and would George is saying at this, in this presentation here is that in 2019, the internet was now 50 years old. So in particular, what he's really referring to is that this key technology of the modern internet, TCP IP was invented in 1969 and underwent a lot of research and development for 20 years. Then there was another 10 years where TCP IP was used to implement the NSF Net and the goal of the project was to connect, I think, 100 American universities to the national supercomputing centers that had grown up in the United States. And it's kind of strange to think about it now, but just the idea that there were local computing networks and if you wanted to interconnect them, that that was a real engineering problem. It was interoperability of the networks. And so this TCP IP was helping to create what they call the internet, the interoperable network. But it was, you know, at that time, a real engineering problem, right?\nSummary:In 1995, George Straun was the director of the National Science Foundation Network (NSF Net). And the goal of the NSF at that time was to connect 100 American Universities to the national supercomputing centers. Now, while this seems simple now the key technology of the internet, TCP IP, was invented just 26 years earlier in 1969, and finding a way to connect many local networks running on this invention was a huge engineering challenge. They were asking the question, how do we make a global internet? An interoperable network.\nParagraph:"

    while thought:
        
        # Clean off white space for OpenAI
        thought=thought.strip()

        # Prepare full prompt
        p = base_prompt + thought + "\nSummary:"

        # Model parameters were determined through sandbox testing. Temp is fairly high to allow the model
        response = openai.Completion.create(
            model="text-davinci-002",
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

        for i in range(aggregate-1): 
            thought += raw_file.readline()
        #thought = raw_file.readline() + raw_file.readline() + raw_file.readline()
        #for i in range(aggregate-1): 
            #thought += raw_file.readline()
    if iterations > 0: 
        SummarizeThoughts(path, "CleanedSummary" + str(iterations) + ".txt", openai, 3, iterations-1)


#Base variables
#openai.organization = "org-6VHyHADPuVpvaocpiGuAUaPb"
openai.api_key = "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"
path = '/Users/desot1/Documents/GitHub/DeSci-Experiments/'

SummarizeThoughts(path, "TranscriptSegmentedIntoThoughts.txt", openai, 1, 2)

