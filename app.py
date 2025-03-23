import json
import os
import requests
import random

REFRESH_TOKEN = os.getenv('REFRESH_TOKEN')

def get_access_token():
    url = "https://securetoken.googleapis.com/v1/token?key=AIzaSyCYSrN4lGsh1sENLyvZAwnqaw7uoQ0-pVc"
    headers = {
        "user-agent": "okhttp/4.12.0"
    }
    data = {
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN
    }

    response = requests.post(url, headers=headers, json=data).json()
    return response["access_token"]

bearer = f"Bearer {get_access_token()}"

headers = {
    "content-type": "application/json",
    "authorization": bearer,
    "user-agent": "okhttp/4.12.0"
}


def do_quizzes():
    url = "https://damdoum.co/api/trpc/v2.quizzes.getQuizQuestions"
    correct_answers = []

    # Start with the first page
    page = 1
    while True:
        # Construct the URL with the current page
        params = {
            "batch": 1,
            "input": f'{{"0":{{"json":{{"timezone":"Africa/Tunis","page":{page}}}}}}}'
        }

        # Make the request
        with requests.Session() as s:
            response = s.get(url, params=params, headers=headers).json()


        # Check if the response contains data
        if not response[0]["result"]["data"]["json"]:
            break  # Exit the loop if no more data is returned

        # Extract correct answers from the current page
        correct_answers.extend(
            answer["id"]
            for question in response[0]["result"]["data"]["json"]
            for answer in question["answers"]
            if answer["isCorrect"]
        )

        if len(response[0]["result"]["data"]["meta"]["values"]) // 2 == page:
            break
        page += 1

    url = "https://damdoum.co/api/trpc/v2.quizzes.submitAnswers?batch=1"
    
    data = {
        "0": {
            "json": {
                "timezone": "Africa/Tunis",
                "answersIds": correct_answers
            }
        }
    }
    with requests.Session() as s:
        response = s.post(url, json=data, headers=headers).json()
    
    print(response)


def do_daily_polls():
    url = "https://damdoum.co/api/trpc/v2.dailyPolls.getDailyPoll"

    params = {
        "batch": 1,
        "input": '{"0":{"json":{"timezone":"Africa/Tunis"}}}'
    }
    with requests.Session() as s:
        response = s.get(url, params=params, headers=headers).json()
    
    vote_url = "https://damdoum.co/api/trpc/v2.dailyPolls.submitVote?batch=1"
    
    for question in response[0]["result"]["data"]["json"]["questions"]:
        most_voted = max(question["options"], key=lambda x: x["votes"])
        data = {
            "0": {
                "json": {
                    "timezone": "Africa/Tunis",
                    "questionId": question["id"],
                    "optionId": most_voted["id"]
                }
            }
        }
        with requests.Session() as s:
            response = s.post(vote_url, json=data, headers=headers).json()
        print(response)


def do_gamified_ads_quiz():
    url = "https://damdoum.co/api/trpc/v2.gamifiedAds.getActive"
    
    compaign_url = "https://damdoum.co/api/trpc/v2.gamifiedAds.quiz.getCampaign"
    
    unlock_url = "https://damdoum.co/api/trpc/v2.gamifiedAds.quiz.unlockPastDay?batch=1"
    
    questions_url = "https://damdoum.co/api/trpc/v2.gamifiedAds.quiz.getQuestions"
    
    submit_url = "https://damdoum.co/api/trpc/v2.gamifiedAds.quiz.submitAnswers?batch=1"
    
    params = {
        "batch": 1,
        "input": '{"0":{"json":null,"meta":{"values":["undefined"]}}}'
    }
    
    with requests.Session() as s:
        response = s.get(url, params=params, headers=headers).json()
    campaign_ids = []
    
    campaign_ids.extend(
    campaign["id"]
    for campaign in response[0]["result"]["data"]["json"]
    )

    
    for campaign_id in campaign_ids:
        params = {
            "batch": 1,
            "input": f'{{"0":{{"json":{{"id":"{campaign_id}","timezone":"Africa/Tunis"}}}}}}'
        }
        with requests.Session() as s:
            response = s.get(compaign_url, params=params, headers=headers).json()
        if not response[0]["result"]["data"]["json"]:
            break
        if not response[0]["result"]["data"]["json"]["isClosed"]:
            for day in response[0]["result"]["data"]["json"]["days"]:
                if not day["isPlayed"]:
                    if not day["isUnlocked"]:
                        data = {
                            "0": {
                                "json": {
                                    "campaignId": campaign_id,
                                    "dayId": day["id"],
                                    "timezone": "Africa/Tunis"
                                }
                            }
                        }
                        with requests.Session() as s:
                            s.post(unlock_url, json=data, headers=headers).json()
                            print(f"Unlocked day {day['id']} in campaign {campaign_id}")
                    quest_params = {
                        "batch": 1,
                        "input": json.dumps({"0": {"json": {"dayId": day["id"], "campaignId": campaign_id, "timezone": "Africa/Tunis"}}})
                    }
                    with requests.Session() as s:
                        questions_r = s.get(questions_url, params=quest_params, headers=headers).json()
                    
                    if "error" in questions_r[0]:
                        print(questions_r[0]["error"]["json"]["message"])
                        break
                    if not questions_r[0]["result"]["data"]["json"]:
                        break
                    correct_answers = []
                    correct_answers.extend(
                        answer["id"]
                        for question in questions_r[0]["result"]["data"]["json"]["questions"]
                        for answer in question["answers"]
                        if answer["isCorrect"]
                    )
                    
                    data = {
                        "0": {
                            "json": {
                                "dayId": day["id"],
                                "campaignId": campaign_id,
                                "answerIds": correct_answers,
                                "completionTime": random.randint(0, 50),
                                "timezone": "Africa/Tunis"
                            }
                        }
                    }
                    with requests.Session() as s:
                        submit_r = s.post(submit_url, json=data, headers=headers).json()
                    print(submit_r)


def do_memory_game():
    times = random.randint(10, 15)
    url = "https://damdoum.co/api/trpc/v2.memoryGame.submitSolvedGame?batch=1"
    data = {
        "0": {
            "json": {
                "timezone": "Africa/Tunis"
            }
        }
    }
    
    for _ in range(times):
        with requests.Session() as s:
            response = s.post(url, json=data, headers=headers).json()
        print(response)
        
def do_sliding_puzzles():
    times = random.randint(10, 15)
    for _ in range(times):
        url = "https://damdoum.co/api/trpc/v2.slidingPuzzles.getPuzzle?batch=1&input=%7B%220%22%3A%7B%22json%22%3A%7B%22timezone%22%3A%22Africa%2FTunis%22%7D%7D%7D"
        with requests.Session() as s:
            response = s.get(url, headers=headers).json()
        
        url = "https://damdoum.co/api/trpc/v2.slidingPuzzles.submitSolvedSlidingPuzzle?batch=1"
        data = {
            "0": {
                "json": {
                    "puzzleId": response[0]["result"]["data"]["json"]["id"],
                    "timezone": "Africa/Tunis",
                    "remainingSeconds": random.randint(0, 90)
                }
            }
        }
    
    
        with requests.Session() as s:
            response = s.post(url, json=data, headers=headers).json()
        print(response)

def do_wordle():
    times = random.randint(10, 15)
    url = "https://damdoum.co/api/trpc/v2.wordle.submitSolvedWordle?batch=1"
    data = {
        "0": {
            "json": {
                "timezone": "Africa/Tunis"
            }
        }
    }
    
    for _ in range(times):
        with requests.Session() as s:
            response = s.post(url, json=data, headers=headers).json()
        print(response)



def do_wyr():
    url = "https://damdoum.co/api/trpc/v2.wyr.getQuestions"

    params = {
        "batch": 1,
        "input": '{"0":{"json":{"timezone":"Africa/Tunis"}}}'
    }
    with requests.Session() as s:
        response = s.get(url, params=params, headers=headers).json()
    
    vote_url = "https://damdoum.co/api/trpc/v2.wyr.submitVote?batch=1"
    
    for question in response[0]["result"]["data"]["json"]:
        if question["firstOption"]["votes"] > question["secondOption"]["votes"]:
            most_voted = question["firstOption"]
        else:
            most_voted = question["secondOption"]
        data = {
            "0": {
                "json": {
                    "timezone": "Africa/Tunis",
                    "questionId": question["id"],
                    "optionId": most_voted["id"]
                }
            }
        }
        with requests.Session() as s:
            response = s.post(vote_url, json=data, headers=headers).json()
        print(response)


do_wyr()
do_wordle()
do_sliding_puzzles()
do_memory_game()
do_gamified_ads_quiz()
do_daily_polls()
do_quizzes()