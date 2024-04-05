# A streamlit demo that has an input bar for a user to enter a claim (text) query and top_k=5 research articles to query and a button to submit. When the button is clicked, call the "_run" function already written below with the claim text entered by the user. "_run" is an async function and on the first time it is run it returns a task_id that you must record and afterwards make sure you call "_run" with that task_id to get back the response. 
# When the output is not ready then you will see the text in the response "There are no results yet. please tell the user and wait ..." or you will see "The estimated time for this operation is...". Please display that progress in a progress bar based on this estimated time until the output is received in the background which you can keep checking using the task_id. 
# The demo should display the response json in a very nice, human-readable format (preferably using markdown).

# The structure/ shape of the json response is:
# { 
#   "claim": "..."  , 
#   " short summary": "..."  ,
#   " detailed report": {
#                  "strong supporting evidence": [ ... evidence, context, metadata ... ]
#                  "strong refuting evidence":   [ ... evidence, context, metadata ... ]
#                  "partial supporting evidence":[ ... evidence, context, metadata ... ]
#              }
# }
#
# Here is a complete example of the json response:
# "task_result":{
# "short_summary":"The claim is strongly supported by the evidence. Word embeddings, a popular machine-learnt semantic space, have been shown to retain gender bias present in corpora used to train them. This results in gender-stereotypical vector analogies and such bias has been shown to materialise in a variety of downstream tasks."
# "report":{
# "claim":"word embeddings preserve gender biases"
# "short summary":"The claim is strongly supported by the evidence. Word embeddings, a popular machine-learnt semantic space, have been shown to retain gender bias present in corpora used to train them. This results in gender-stereotypical vector analogies and such bias has been shown to materialise in a variety of downstream tasks."
# "detailed report":{
# "strong evidence in support of the claim":[
# 0:{
# "evidence":"However, contextualized word embeddings preserve and even amplify gender bias when taking into account other aspects."
# "context and assumptions around the evidence if any":"The study was conducted in 2019 and it was observed that contextualized word embeddings can amplify gender bias."
# "metadata":{
# "paper_id":"121125604"
# "section":"Conclusions and further work"
# "year":2019
# "venue":"ACL"
# }
# }
# 1:{
# "evidence":"We show that the biases in the word embedding are in fact closely aligned with social conception of gender stereotype, as evaluated by U.S.-based crowd workers on Amazon's Mechanical Turk."
# "context and assumptions around the evidence if any":"The study was conducted in 2016 and it was observed that the biases in the word embedding are closely aligned with social conception of gender stereotype."
# "metadata":{
# "paper_id":"1704893"
# "section":"Introduction"
# "year":2016
# "venue":"ACL"
# }
# }
# 2:{
# "evidence":"Word embeddings, a popular machine-learnt semantic space, have been shown to retain gender bias present in corpora used to train them."
# "context and assumptions around the evidence if any":"The study was conducted in 2019 and it was observed that word embeddings, a popular machine-learnt semantic space, retain gender bias present in corpora used to train them."
# "metadata":{
# "paper_id":"202541569"
# "section":"Introduction"
# "year":2019
# "venue":"ACL"
# }
# }
# 3:{
# "evidence":"Bolukbasi et al. (2016) demonstrated that word embeddings, which serve as the foundation for language models, can reflect gender biases present in the training data."
# "context and assumptions around the evidence if any":"The study was conducted in 2023 and it was observed that word embeddings, which serve as the foundation for language models, can reflect gender biases present in the training data."
# "metadata":{
# "paper_id":"259950823"
# "section":"II. LITERATURE REVIEW"
# "year":2023
# "venue":"ACL"
# }
# }
# ]
# "strong evidence refuting the claim":[]
# }
# }
# }
# }

import json
import time
from typing import Dict, Optional
import requests
import streamlit as st
import os

# read environment variable or secret from streamlit secrets
bearer_token: str = st.secrets["BEARER_TOKEN"]  # os.getenv("BEARER_TOKEN") or st.secrets["BEARER_TOKEN"]  
headers_ = { "Authorization": f"Bearer {bearer_token}", "content-type": "application/json" }

def _run(input_claim: str, 
         top_k: int=5, 
         tool_url: str = "https://nora-claims.apps.allenai.org/use-tool", 
         task_id: Optional[str] = None) -> Dict:
        if tool_url is None:
            raise ValueError("tool_url must be set")

        res = {}

        if task_id:
            # st.write(f"(if condition) task_id: {task_id}")
            res = requests.post(
                url=tool_url,
                data=json.dumps({"task_id": task_id}),
                headers=headers_,
            ).json()
            current_response = {
                "paper_finder_agent_response": f"There are no results yet. please tell the user and wait for them to ask again before checking the status."
            }
            task_result = res.get("task_result")
            if task_result:
                current_response = {
                    "paper_finder_agent_response": task_result.get(
                        "response_text",
                        f"There are no results yet. please tell the user and wait for them to ask again before checking the status.",
                    ),
                    "corpus_ids": task_result.get("corpus_ids", []),
                }
        else:
            # st.write(f"(else condition) Task id is: {task_id}")
            # "input_claim": "highly educated people are polarized", "top_k": 2
            data_ = json.dumps({"input_claim": input_claim, "top_k": top_k})  
            
            res_str_json = requests.post(
                tool_url,
                data=data_,
                headers=headers_,
            )
            # st.write(f"res_str_json: {res_str_json.text} and as json: {res_str_json.json()}")

            res = res_str_json.json()
            current_response = {
                "paper_finder_agent_response": f'The estimated time for this operation is: {res["estimated_time"]}, and the task_id is {res["task_id"]}. Please tell the user and wait for them to ask again before checking the status.'
            }
        
        # st.write(f"Current response: {current_response['paper_finder_agent_response']}")
        return res, current_response




def main():
    st.title("CS Claim verifier")
    sample_cs_claims = [
        "type your own claim here...",
        "work autonomy can increase motivation",
        "weight decay helps generalization",
        "word embeddings preserve gender biases",
        "the less human features a robot has, the more appealing it is",
        "the performance of metrics varies widely across datasets",
        "individuals express their true selves more easily online",
        "interactive books help students with knowledge absorbing",
        "downvotes worsen the quality of discourse on social media",
        "unaccompanied migrant youth show signs of sleep disorders",
        "delivering feedback too early could derail visitor engagement",
        "less than 5% provided any kind of publicly available source code",
        "time constraints limit what patients disclose to clinicians",
        "children struggled to formulate queries to a voice interface",
        "the brain is able to accept virtual limbs as part of the own body",
        "workers exposed to examples generated higher quality responses",
        "highly educated individuals can be more polarized in their beliefs",
        "BERT representations are correlated with human scores of polysemy",
        "front vowels in brand names seem more feminine than back vowels",
        "user clicks as a relevance proxy often suffer from ranking bias",
        "neural networks models do not produce competitive results for smaller data",
        "older adults made more insertion errors with the smaller device"
    ]

    # Select a claim input from the dropdown or write one
    claim = st.selectbox("Select a claim or type", sample_cs_claims)
    if claim == "type your own claim here...":
        claim = st.text_area("Type your claim here")
    top_k = st.number_input("Number of papers to summarize over", value=5)
    answer = None
    wait_printed = False
    task_id_ = ""
    time_remaining_in_minutes = 0
    wait_started_at = 0
    progress_bar = st.progress(0, text="Progress bar")

    if st.button("Submit"):
        while answer is None :

            response, str_msg = _run(input_claim=claim, top_k=top_k, task_id=task_id_)

            # Check if the response is not ready yet then extract the time remaining and task_id from the response and show the message below
            if "estimated_time" in response:
                # Show the message below
                task_id_ = response['task_id']
                if not wait_printed:
                    time_remaining_in_minutes = float(response['estimated_time'].split(" ")[0])
                    # st.write(f"The estimated time for this operation is: {time_remaining_in_minutes: 0.2} minutes.")
                    # st.write(f"The task id assigned is {response['task_id']}")
                    wait_printed = True # Set this flag to True so that the message is not printed again
                    wait_started_at = time.time()
                    # Show the progress bar based on the estimated time
                    progress_bar.progress(0)
                else:
                    # estimated time remaining
                    percentage_done = int((time.time() - wait_started_at) / (time_remaining_in_minutes * 60) * 100)
                    percentage_done = 95 if percentage_done >= 95 else percentage_done
                    progress_bar.progress(percentage_done)

            else:
                # If the response is ready then show the response
                # Check if the response has the key "paper_finder_agent_response" and if it has then show the response
                progress_bar.progress(100)
                answer = response["task_result"]
                short_summary = answer["short_summary"]
                report = answer["report"]

                # Make a collapsible section in streamlit to show complete response
                # st.write("Response")
                # write summary in bold text
                st.markdown(f"**Short Summary:** {short_summary}")

                # Expand the collapsible section to show the complete response
                st.write("\n\n")
                with st.expander("Detailed Report"):
                    st.json(response)
                
                

if __name__ == "__main__":
    main()
    