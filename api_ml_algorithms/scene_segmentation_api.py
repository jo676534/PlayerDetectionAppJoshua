import requests

#need to 
scene_segmentation_endpoint = 'http://127.0.0.1:5000/get' # this is a flask environment running on my local computer for testing

#need to pass in the video name and video key so scene segmentatio knows what video to use
def begin_scene_segmentation(video_name,video_key):

    #the request will be a get request
    #the scene segmentation algorithm will return a dict
    #of scenes to trim
    try:
        
        video_data_location = {'video_name':video_name, 'video_key':video_key}

        result = requests.get(url=scene_segmentation_endpoint,data=video_data_location)
        
        data_json = result.json()

        #do some work to return item a certain way?
        #the algorithm will also save these trim queues but not in the front end do it in the flask app
       
        #send to front-end
        return data_json

    except requests.exceptions.RequestException as error:
        print(str(error))
        return error






#algorithm will return a huge json have it here for testing purposes, this is already hosted on heroku
def test_api():

    try:
         response1 = requests.get("https://exercisedatabase.herokuapp.com/exercises")
         print(response1.json())

    except requests.exceptions.RequestException as error:
        print(str(error))
        return error