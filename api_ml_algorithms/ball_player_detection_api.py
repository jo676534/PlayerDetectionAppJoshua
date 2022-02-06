import requests

ball_and_player_detection_endpoint = "http://127.0.0.1:5000/get"  # this is a flask environment running on my local computer for testing


def begin_ball_player_detection(video_name, video_key):

    # the request will be a get request
    # the ball and player detection algorithm will

    try:
        video_data_location = {"video_name": video_name, "video_key": video_key}

        result = requests.get(
            url=ball_and_player_detection_endpoint, data=video_data_location
        )

        data = result.json

        return data

    except requests.exceptions.RequestException as error:
        print(str(error))
        return error
