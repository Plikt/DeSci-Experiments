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
    options = whisper.DecodingOptions(language= 'en')
    model = whisper.load_model("base")
    result = model.transcribe("chris.wav")
    result
    
    #for i in audiofilename.segments: 
        #result += model.transcribe(path+audiofilename[i]) + "\n\n"
   
    # write the content to a text file
    #F = open(path + audiofilename + ".txt", "w")
    #F.write(result["text"])
    #F.close()
    
    # Return the transcript
    transcript_text= result["text"]
    return transcript_text


# This function takes the text input from the youtube video and uses GPT3 to turn it into a cohesive 
# series of thoughts. Those can later be turned into a twitter thread
def CreateModularContent(openai, transcript_text, path):

    #META: Ways to do this
    #Break this into large chunks via the diarizer (comm calls) -> Summarize the one large chunk. 
    #Mechanically break into slightly more reasonable chunks by ending at end of sentence. 
    #  Separate into thoughts -> summarize each paragraph. + Summarize paragraphs. 
    #Manual
    #Other? The thoughts would be training. 

    
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

    base_prompt = "Text: So this presentation will be in two parts and the first part going fair is really about kind of the history of where this idea came from about fair and kind of how it's matured up until today and then in the next section on doing fair, just to kind of give you a snapshot of some state of the art developments right now on the implementation of the fair principles and kind of, you know, the doors that opens up to kind of a new way of looking at computing and a new way of doing information exchange and being able to access larger amounts of data for kind of, you know, distributed learning type analyses.\nShortened text:This presentation will be in two parts. The first part 'going fair' is the history of where this idea came from and how it's matured until today. In the next section on 'doing fair', I'll give you a snapshot of state of the art developments on fair principle implementations and the doors that open up to a new way of looking at computing, of doing information exchange, and being able to access larger amounts of data for distributed learning analyses.\nText:"
    #"Text: what this allows to do is it creates a a tremendous abilities for applications to compete for features and not for data right so you're unbundling the data layer from the application layer and that changes the incentives it's no longer about hey creating Network effects like in web 2 when you're essentially building you know hoarding data and creating Network effects out of this horde of data that you're building out over time but rather because you've unbundled the data layer from the application layer it's all about how you're going to serve your users the best with the best set of features.\nCleaned text: What this allows applications to do is compete on features, not data. By unbundling the data layer from the application layer, the incentives change. It's no longer about creating network effects by hoarding data. Instead, it's all about how you can serve your users the best with the best set of features.\nText: "

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

def DiarizeContent(
                    audiofilename,
                    embed_model='xvec', # 'xvec' and 'ecapa' supported
                    cluster_method='sc' # 'ahc' and 'sc' supported
                    ): 
    
    segments = diar.diarize(audiofilename)
    

#this function would run each of the paragraphs from CreateModularContent and classify it using preset topics
#NOTE: I'm not sure how effective this would be -> do you have other thoughts on how we might create a
#rich set of methods for understanding how we might develop a method of creating /chunks of the text (Presumably besides you doing it)
#def Classify(topics, path, filename, openai):
    #this forloop runs through the topics and classifies each of the thoughts
    #for i in range(length(topics)): 
        #print("help")

def CleanThoughts(path, filename, openai):
    #WAYS> 
    #Change content goals -> just use Whisper -> diarize -> Summarize. 
    #continue trying to make a clearer transcript. 

    # Imports GPT3 model. Using Curie as it does a good job of summarizing text at a significantly cheaper
    # rate than DaVinci
    openai.Model.retrieve("text-curie-001")   
    
    cleaned_file = open(path + "CleanedSumamry.txt", "w")
    raw_file = open(path+filename, "r")
    thought = raw_file.readline()
    counter = 0

    # structures the base prompt for the model
    #base_prompt = "Text: In particular the last five years has been full time at this organization called the GoFair Foundation. These slides are available. differences that are in here too. Okay, so what is this idea going fair and doing fair? So this presentation will be in two parts and the first part going fair is really about kind of the history of where this idea came from about fair and kind of how it's matured up until today and then in the next section on doing fair, just to kind of give you a snapshot of some state of the art developments right now on the implementation of the fair principles and kind of, you know, the doors that opens up to kind of a new way of looking at computing and a new way of doing information exchange and being able to access larger amounts of data for kind of, you know, distributed learning type analyses. Cleaned: What is going fair and doing fair? This presentation will be in two parts. The first part, going fair, is the history of where this idea came from and how it has matured up until today. In the next section on doing fair, I’ll give you a snapshot of state of the art developments on the fair principles implementation and how that opens up a new way of looking at computing, of doing information exchange and being able to access larger amounts of data for kind of, you know, distributed learning type analyses.\n\nText:"
    #base_prompt = "Text: In particular the last five years has been full time at this organization called the GoFair Foundation. These slides are available. differences that are in here too. Okay, so what is this idea going fair and doing fair? So this presentation will be in two parts and the first part going fair is really about kind of the history of where this idea came from about fair and kind of how it's matured up until today and then in the next section on doing fair, just to kind of give you a snapshot of some state of the art developments right now on the implementation of the fair principles and kind of, you know, the doors that opens up to kind of a new way of looking at computing and a new way of doing information exchange and being able to access larger amounts of data for kind of, you know, distributed learning type analyses. \n\nCleaned: What is going fair and doing fair? This presentation will be in two parts. The first part, going fair, is the history of where this idea came from and how it has matured up until today. In the next section on doing fair, I’ll give you a snapshot of state of the art developments on the fair principles implementation and how that opens up a new way of looking at computing, of doing information exchange and being able to access larger amounts of data for kind of, you know, distributed learning type analyses. \n\nText:" 
    #base_prompt = "Text: what this allows to do is it creates a a tremendous abilities for applications to compete for features and not for data right so you're unbundling the data layer from the application layer and that changes the incentives it's no longer about hey creating Network effects like in web 2 when you're essentially building you know hoarding data and creating Network effects out of this horde of data that you're building out over time but rather because you've unbundled the data layer from the application layer it's all about how you're going to serve your users the best with the best set of features.\n\nCleaned text: What this allows applications to do is compete on features, not data. By unbundling the data layer from the application layer, the incentives change. It's no longer about creating network effects by hoarding data. Instead, it's all about how you can serve your users the best with the best set of features.\n\nText: "
    #base_prompt = "Text: Okay, so I'm going to start here with a picture from, that I took in 2019 in the gentleman at the podium, his name is George Straun and in 1995, he was the director of something called the NSF Net, the National Science Foundation Network and would George is saying at this, in this presentation here is that in 2019, the internet was now 50 years old. So in particular, what he's really referring to is that this key technology of the modern internet, TCP IP was invented in 1969 and underwent a lot of research and development for 20 years. Then there was another 10 years where TCP IP was used to implement the NSF Net and the goal of the project was to connect, I think, 100 American universities to the national supercomputing centers that had grown up in the United States. And it's kind of strange to think about it now, but just the idea that there were local computing networks and if you wanted to interconnect them, that that was a real engineering problem. It was interoperability of the networks. And so this TCP IP was helping to create what they call the internet, the interoperable network. But it was, you know, at that time, a real engineering problem, right?’ And then around 1995, it had become recognized that the NSF Net had become dominated by the private sector that already companies were finding this government network so useful that they became the majority users. And then it was at that time that George Straun said, well, this government network is, you know, the life is probably, the lifetime is probably over for it. And what we'd like to do is then hand it over to the private sector. And that's what gave birth into the modern internet that we know.\n\nCleaned text: I'm going to start with a picture that I took in 2019. The gentleman at the podium is George Straun and in 1995, he was the director of the NSF Net, the National Science Foundation Network. At his talk, he was referring to the modern internet technology, TCP IP. TCP IP was invented in 1969, underwent a lot of research and development for 20 years, then implemented the NSF Net for 10 years. The project’s goal was to connect 100 American universities to the United States national supercomputing centers. Overall, There were local computing networks and you wanted to interconnect them, that that was a real engineering problem. TCP IP was helping to create the internet, the interoperable network. By 1995, the NSF Net was dominated by the private sector. At that time George Straun said, the government network is over and we should hand it over to the private sector. That's what gave birth into the modern internet that we know.\n\nText: "
    #base_prompt = "Text:Yeah, in particular the last five years has been full time at this organization called the GoFair Foundation. These slides are available. differences that are in here too. Okay, so what is like, oh, this idea going fair and doing fair? So this presentation will be in two parts and the first part going fair is really about kind of the history of where this idea came from about fair and kind of how it's matured up until today and then just in the next section on doing fair, just to kind of give you a snapshot of some when we might be like, hey, these are state of the art developments right now on the implementation of the fair principles and kind of, you know, the doors that opens up to be able to find a new way of looking at computing and a new way of doing information exchange and being able to access larger amounts of data for kind of, you know, distributed learning type analyses. For example, if we wanted to see what good data was, we might look at what the fair principles say. \n\nShortened text:What is going fair and doing fair? This presentation will be in two parts. The first part, going fair, is the history of where this idea came from and how it has matured up until today. In the next section on doing fair, I’ll give you a snapshot of state of the art developments on the fair principles implementation and how that opens up a new way of looking at computing, of doing information exchange, and accessing larger amounts of data for distributed learning analyses.\n\nText:"
    #base_prompt = "Text:Yeah, in particular the last five years has been full time at this organization called the GoFair Foundation. These slides are available. differences that are in here too. Okay, so what is like, oh, this idea going fair and doing fair? So this presentation will be in two parts and the first part going fair is really about kind of the history of where this idea came from about fair and kind of how it's matured up until today and then just in the next section on doing fair, just to kind of give you a snapshot of some when we might be like, hey, these are state of the art developments right now on the implementation of the fair principles and kind of, you know, the doors that opens up to be able to find a new way of looking at computing and a new way of doing information exchange and being able to access larger amounts of data for kind of, you know, distributed learning type analyses. For example, if we wanted to see what good data was, we might look at what the fair principles say.\n\nShortened text: What is going fair and doing fair? This presentation will be in two parts. The first part, going fair, is the history of where this idea came from and how it has matured up until today. In the next section on doing fair, I’ll give you a snapshot of state of the art developments on the fair principles implementation and how that opens up a new way of looking at computing, of doing information exchange, and accessing larger amounts of data for distributed learning analyses.\n\nText:"
    base_prompt = "Text:Yeah, in particular the last five years has been full time at this organization called the GoFair Foundation. I think these slides are available. differences that are in here too. Okay, so what is like, oh, this idea going fair and doing fair? So this presentation will be in two parts and the first part going fair is really about kind of the history of where this idea came from about fair and kind of how it's matured up until today and then just in the next section on doing fair, just to kind of give you a snapshot of some when we might be like, hey, these are state of the art developments right now on the implementation of the fair principles and kind of, you know, the doors that I think it opens up to be able to find a new way of looking at computing and a new way of doing information exchange and being able to access larger amounts of data for kind of, you know, distributed learning type analyses. For example, if we wanted to see what good data was, we might look at what the fair principles say.\n\nShortened text:What is going fair and doing fair? This presentation will be in two parts. The first part, going fair, is the history of where this idea came from and how it has matured up until today. In the next section on doing fair, I’ll give you a snapshot of state of the art developments on the fair principles implementation and how that opens up a new way of looking at computing, of doing information exchange, and accessing larger amounts of data for distributed learning analyses.\n\nText:"
    while thought:
        
        # Clean off white space for OpenAI
        thought=thought.strip()

        # Prepare full prompt
        p = base_prompt+thought+"\n\nShortened text:"

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

#audiofilename = 'future-of-science-se_untitled-recording_erik-7c7d35045_2022-nov-14-1559pm-utc-riverside.wav'
#transcript_text = GetTranscriptFromAudio(path, audiofilename)
#CleanThoughts(path, "CallTranscriptFull.txt", openai)
SummarizeThoughts(path, "TranscriptSegmentedIntoThoughts.txt", openai, 1, 2)
#SummarizeThoughts(path, "CleanedSummary.txt", openai, 5)
#GetTranscriptFromAudio(path, "philipp.wav")
#GetTranscriptFromAudio(path, "philipp.wav")
#GetTranscriptFromAudio(path, "carla.wav")






#filename = "CallTranscriptFull.txt"
#video_id = 'vWvYTTA_8EA'
#transcript_text = FormatYouTubeTranscript(video_id,path)
#CreateModularContent(openai, filename, path)
