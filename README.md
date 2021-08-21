# Player Detection and Tracking
This Dash application is for the Player Detection and Tracking from SportsScience AI.

## Installation and Running
Can be ran with Docker with the included Dockerfile or traditionally, below:

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the required libraries used in the application.
```bash
pip install -r requirements.txt
```

In the 'application.py' file the choice of running with the debug tool or in a production setting is possible at the end of the file. Choose one and comment the other to work
```python
app.run_server(debug=True, port=8080) # Have this line active to debug
application.run(debug=True, host='0.0.0.0', port=8080) # Have this line active to run actual application
```

When ready to run:
```bash
python application.py
```
## Senior Design Past Group Resources
[Homography](https://drive.google.com/file/d/1gRlwyqVVX9RW0beowKVINEigz9lavhnp/view?usp=sharing)
[DeepSort_YOLOv4](https://drive.google.com/file/d/1xi6UmQBrwhmRHK1YJzIjqg8rSe0YuJT0/view?usp=sharing)

## Stages of an entry.
0: PAGE - Initial Review (Game freshly uploaded)
1: PROCESS - Converted to 15 fps
2: PAGE - Video Editor (Being edited)
3: PROCESS - Video being recompiled with removed frames (Then usually goes back to stage 2 unless no more editing needs to be done)
4: PROCESS - Detection algorithm being run    
5: PAGE - Dashboard (Track matching + Manual annotation + Add track)
6: PROCESS - Homography being run
7: PAGE - Final review page

### Stage 0 - Initial Review [Page]
Immediately after uploading, the entry enters Stage 0 aka Initial Review. Upon user selection from the home page, the video will be pulled from its corresponding AWS S3 bucket into the video player on the page. Here the user is able to play and go through the video and ultimately be able to deny or accept the video into the system.

#### Why?
We chose to create an Initial Review page to be be able to gatekeep invalid videos from being further processed.

#### Incomplete Implementation
- Upon user selection, pulling from database and displaying the corresponding video from AWS S3.
- If denied, purging entry from database and AWS S3.
- If accepted, incrementing stage in database.

### Stage 1 - Convert Video to 15 Frames per Second [Process]
#### Why?
After approval, we would ideally like the video to be more manageable to both the algorithms (Stages 3, 4, and 6) and for our frame player (Stages 2 and 5). Having  the video at 15FPS gives us more efficiency by providing less frames to be processed while still giving the feeling of movement from  frame-to-frame. For example, a 90 minute video at 50FPS gives us 270,000 frames; while the same 90 minute video at 15FPS gives us 81,000 frames.

#### Extra Notes
- AWS MediaConvert or AWS Elastic Transcoder
- Was able to manually do this with python library moviepy.

#### Incomplete Implementation
- When 15FPS version is uploaded back to S3, increment stage in database.

### Stage 2 - Video Editor [Page]
In the Video Editor Page, where we are introduced to the frame player, we are able to select a range of frames to 'blacklist.' Blacklisting a frame will just mark a frame to avoid when recompilation is processing. Adding multiple ranges will create a list of ranges to blacklist. 
#### Why?
There are unusable footage in games such as closeups, fans, commercials, when we strictly want footage of gameplay. We want to be able to identify them to crop out the video.

#### Extra Notes
Optimal Implementation to avoid having to go to Stage 3 multiple times.
- If incomplete("Save and Quit"), save blacklist [to Database? to S3?].
- When entering an entry in Stage 2, try to pull blacklist first, if nothing there, start fresh.

#### Incomplete Implementation
- Upon user selection, pulling(downloading?) from database and displaying the corresponding video from AWS S3; 15 FPS, unedited video.
- When 'Save and Continue' is selected, increment stage in database.

### Stage 3 - Video Recompilation and Compression [Process]
#### Why?
Stages 2 and 3 work conjointly together. Using the blacklist provided in Stage 2, that will allow us to know which frames to avoid in remaking the video. If using the frames to recreate the video, the actual video file can be large and uncompressed.

#### Extra Notes
Gonna need two parts to this process:
- Recompiling 
- (depending on recompiling) Compression
    Currently needs to compress.

- AWS MediaConvert or AWS Elastic Transcoder

#### Incomplete Implementation
- Currently recompilation is working inside the 'video_edit.py' file, but compression not implemented.

### Stage 4 - Detection Algorithm [Process]

#### Why?

#### Incomplete Implementation


### Stage 5 - Dashboard [Page]

#### Why?

#### Incomplete Implementation

### Stage 6 - Homography [Process]

#### Why?

#### Incomplete Implementation

### Stage 7 - Final Review [Page]

#### Why?

#### Incomplete Implementation