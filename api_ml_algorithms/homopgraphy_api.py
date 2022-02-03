import requests

homography_endpoint = 'http://127.0.0.1:5000/get' # this is a flask environment running on my local computer for testing



def begin_homography(video_name,video_key):

        try:
        
            video_data_location = {'video_name':video_name, 'video_key':video_key}

            result = requests.get(url=homography_endpoint,data=video_data_location)
        
            data_json = result.json()

            #do some work to return item a certain way?
            #the algorithm will also save these trim queues but not in the front end do it in the flask app
       
            #send to front-end
            return data_json

        except requests.exceptions.RequestException as error:
            print(str(error))
            return error
