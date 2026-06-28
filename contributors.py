from flask import Blueprint,jsonify
from dotenv import load_dotenv
import os
import requests
load_dotenv()
GITHUB_TOKEN=os.getenv("GITHUB_TOKEN")

avatar_sync= Blueprint("avatar_sync",__name__)
@avatar_sync.route("/avatar_sync",methods=['GET'])

def response():
    headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

    owner = "AdityaSharma2457"
    repo = "rag_cpu"

    url = f"https://api.github.com/repos/{owner}/{repo}/contributors"

    response = requests.get(url, headers=headers)
    return  jsonify(response.json())