#setup 
import openai as openai #Extracting content metadata
import fitz #pdf reading library
import time #to ensure we don't call too often from openai
from bs4 import BeautifulSoup #to extract XML info -> will be eliminated eventually
import json
import asyncio
import asyncgpt
import tracemalloc


def pdfMetadata(filepath): 
    """
    This returns basic descriptive metadata for the PDF. 

    VARS: 
        Filepath: the path of the file you want to upload. 

    RETURNS: 
        metadata: This is the basic function of the Fitz library. 
        It scrapes the PDF for any embedded metadata. 
    """
    doc = fitz.open(filepath)
    metadata = doc.metadata
    return metadata 

def pdfTextExtraction(filepath): 
    """
    This returns text from the pdf by paragraph. 

    VARS: 
        Filename: the name of the file you want the function to write
        Filepath: the path of the pdf. 

    WRITES: 
        a .txt file 
    """
    doc = fitz.open(filepath + ".pdf")  # open document
    with open(filepath + ".txt", 'w') as out:
        for page in doc:  # iterate the document pages
            text = page.get_text().encode("utf8")  # get plain text (is in UTF-8)
            out.write(text.decode('utf-8'))  # write text of page
            out.write(bytes((12,)).decode('utf-8'))  # write page delimiter (form feed 0x0C) 
    return 

def summarize(prompt, thought): 
    final = "Summarize these responses into one sentence that tells me the paper's" + prompt + "\n" + thought
    response = openai.Completion.create(
                model="text-curie-001",
                prompt = final,
                max_tokens=400,
                temperature=0.7,
                top_p=1,
                frequency_penalty=0.5,
                presence_penalty=0.5
        )
    return response

  

def contentMetadataRecipe(openai, filepath, prompt): 
    """
    This recipe is for metadata extraction from paragraphs. Not basic metadata like authors etc. 

    VARS:

    RETURN: 

    """
    
    #initialization

    res = ""
    ans = []
    openai.Model.retrieve("text-curie-001")
    
    with open(filepath, 'r') as f: 
        #pull out the txt file into 
        paragraphs = f.readlines()
        print(len(paragraphs))

    
    #Set on
    base_prompt = "Does this paragraph describe the paper's " + prompt + "Answer with a Yes or No."
    
    for para in range(len(paragraphs)): 
        #for loop - for each paragraph, we ask if it describes the papers's "input prompt" then summarize that paragraph. 
        
        if len(paragraphs[para]) > 100 and len(paragraphs[para]) < 7601: 
            thought = paragraphs[para].strip()
            p = base_prompt + thought

        elif len(paragraphs[para]) > 7600:
            split1 = ""
            split2 = ""  
            modular = paragraphs[para].split('.')
            for i in range(len(modular)): 
                if i< len(modular)/2:
                    split1 += modular[i]
                else:
                    split2 += modular[i]
            
            paragraphs.insert(para+1, split1)
            paragraphs.insert(para+2, split2)

            continue

        else: 
            continue
        
        response = openai.Completion.create(
            model="text-curie-001",
            prompt = p,
            max_tokens=400,
            temperature=0.3,
            top_p=1,
            frequency_penalty=0.5,
            presence_penalty=0.5
        )

        answer = response["choices"][0]["text"]        
        
        if answer =="Yes": 
            question = "In one sentence, what does this paragraph say is the paper's" + prompt + "?" + thought
            response2 = openai.Completion.create(
                model="text-curie-001",
                prompt = question,
                max_tokens=400,
                temperature=0.7,
                top_p=1,
                frequency_penalty=0.5,
                presence_penalty=0.5
            )
            ans.append(response2["choices"][0]["text"]) 
        
        if para%30==0 and para!=0:
            print("\n\n\nI am so sleepy\n\n\n")
            time.sleep(60)
    count = 0
    while len(res) < 7400: 
        res += ans[count]
        count += 1
        if count == len(ans): 
            break

        
    final = summarize(prompt, res)
    return final

async def metadata(filename, filepath): 
    
    contentMetadata = {} #defining the dictionary

    pdfTextExtraction(filepath) #extract the text from the file
    
    filepathtxt = filepath + '.txt'

    #descriptiveMetadata = pdfMetadata(filepath + ".pdf")

    categories = ['Research Question', 'Alterative Approaches', 'Hypothesis', 'Methodology', 'Results', 'Inferences']

    bot = asyncgpt.GPT(apikey="YOUR API KEY")

    

    #for i in range(len(categories)):
        #contentMetadata = {categories[i]: contentMetadataRecipe(openai, filepathtxt, categories[i])}
    contentMetadata = AsyncRecipe(bot, filepath, categories[0])  
        
    metadata = [contentMetadata, descriptiveMetadata]

    return metadata

def categorize(bot, paragraphs, prompt):
    task = []
    test = 0
    base_prompt = "Does this paragraph describe the paper's " + prompt + "Answer with only a yes or no."

    print("len para =" + str(len(paragraphs)))
    for para in range(len(paragraphs)): 
        #for loop - for each paragraph, we ask if it describes the papers's "input prompt" then summarize that paragraph.
        if len(paragraphs[para]) > 100 and len(paragraphs[para]) < 7601: 
                    thought = paragraphs[para].strip()
                    p = base_prompt + thought
                    task.append(bot.complete(p))
                    test +=1
                    if test > 2: 
                         break

        elif len(paragraphs[para]) > 7600:
                    split1 = ""
                    split2 = ""  
                    modular = paragraphs[para].split('.')
                    for i in range(len(modular)): 
                        if i< len(modular)/2:
                            split1 += modular[i]
                        else:
                            split2 += modular[i]
                    
                    paragraphs.insert(para+1, split1)
                    paragraphs.insert(para+2, split2)

                    continue

        else: 
            continue
    print(len(task))
    return task

def AsyncRecipe(bot, filepath, prompt):

    with open(filepath, 'r') as f: 
        #pull out the txt file into 
        paragraphs = f.readlines()

    task = categorize(bot, paragraphs, prompt)

    return task



async def main():

    bot = asyncgpt.GPT(apikey="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")
    filepath = "/Users/desot1/Dev/desci/Papageorgiou et al_2017_Mechanical properties of graphene and graphene-based nanocomposites.txt"

    categorize = AsyncRecipe(bot, filepath, "method")
    
    completion = await asyncio.gather(*categorize)
    
    """"try:
        # get the return value from the wrapped coroutine
        value = completion.result()
    except Exception:
	    # task failed and there is no result
        print('failed')
    #print(type(completion[0]))"""
    #I think I need to build an exception here for when GPT goes pls fuck off. 
    print(completion[0])
    



if __name__ == "__main__":
    asyncio.run(main())
    # Hello there! How can I assist you today?


'''
def main(): 
    """
    testing the functions above
    """
    openai.api_key = "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"

    filename = 'Papageorgiou et al_2017_Mechanical properties of graphene and graphene-based nanocomposites'

    filepath = "/Users/desot1/Dev/desci/Papageorgiou et al_2017_Mechanical properties of graphene and graphene-based nanocomposites"
    
    metadata(filename, filepath)
    
    

    with open("metadata.json", "w") as write_file:
        json.dump(metadata, write_file, indent=4)  
    
    return 
'''
'''
if __name__ == "__main__": 
    main = main()  
    asyncio.run(main)  

'''
