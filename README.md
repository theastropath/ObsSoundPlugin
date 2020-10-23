# ObsSoundPlugin
A Python script for OBS Studio that allows audio playback based on incoming HTTP messages

Configuration:

To set this up, you need to first create a "Media Source" in OBS which will be used for playback.  Next, add the script to OBS under Tools>Scripts.  Configure the "Media Source Name" to match the name of the Media Source you created earlier.  The "Audio Folder" should be the path to the folder containing your audio clips (This should end with a backslash for now).  The "Test File" lets you specify a filename of an audio clip in the audio folder that you can test with the "Test Playback" button.  The "Port Number" allows you to choose what port you want to listen for the HTTP requests on.


Sending playback requests:

Sending playback requests is very simple.  In the examples below, replace "yourpc" with the IP or hostname of the PC you are running OBS Studio on.  Change 8888 to whatever port you chose to listen on when you configured the script

For extremely basic playback, you can send a request to:

http://yourpc:8888/testsound.mp3

Which will play the clip at 100% volume.

You can also adjust the volume by adding a "vol" parameter afterwards, for example:

http://yourpc:8888/testsound.mp3?vol=0.5

1.0 is 100% volume and can be adjusted down to 0% or up to 200% (2.0)

If you want to change the speed of playback, there is a "speed" parameter also:

http://yourpc:8888/testsound.mp3?speed=0.5

Like with volume, this can be adjusted from 0% speed up to 200% (2.0)

The volume and speed parameters can also be combined:

http://yourpc:8888/testsound.mp3?vol=0.5&speed=0.5