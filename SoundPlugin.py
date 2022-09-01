import obspython as obs

from time import sleep
from threading import Thread
from socketserver import ThreadingMixIn
from http.server import HTTPServer,BaseHTTPRequestHandler
import os

sourcename = ""
audiofolder = ""
testfile = ""
portnum = 8888
oldportnum=0

serverthread = None
stopserver = False
httpd = None

wasplaying = False

playlist = []


# ------------------------------------------------------------

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        global playlist
        obs.script_log(obs.LOG_DEBUG,"Got GET!")

        opts = dict()
        
        command = self.path[1:]
        if "?" in command:
            split = command.split("?")
            filename = split[0]
            options = split[1].split("&")

            for option in options:
                splitopt = option.split("=")
                opts[splitopt[0]]=splitopt[1]

            obs.script_log(obs.LOG_DEBUG,str(opts))
            
        else:
            filename = command

        #obs.script_log(obs.LOG_DEBUG,str(self.path))
        if check_for_file(filename):
            #playsound(filename)
            playlist.append((filename,opts))
            resp = "Played "+filename
        else:
            obs.script_log(obs.LOG_DEBUG,filename+" is not present")
            resp = "Could not find "+filename
        self.send_response_only(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        resp = resp.encode()
        self.wfile.write(resp)        

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

# ------------------------------------------------------------

def check_for_file(filename):
    return os.path.isfile(audiofolder+filename)

def script_description():
    return "Accepts audio file play requests via HTTP request\n\nBy TheAstropath"

def server_handle():
    global httpd
    #obs.script_log(obs.LOG_DEBUG,"Handling")
    
    if httpd:
        #Timeout must be very small, otherwise it impacts the
        #framerate of the stream
        httpd.timeout=0.001
        httpd.handle_request()
        

def server_task():
    global httpd
    global stopserver
    obs.script_log(obs.LOG_DEBUG, "Server task started")

    while not stopserver:
        httpd.timeout=0.001
        httpd.handle_request()
        sleep(1)
        
    obs.script_log(obs.LOG_DEBUG, "Server task stopped")


    stopserver = False

def stop_server():
    global httpd
    global serverthread
    global stopserver
    obs.script_log(obs.LOG_DEBUG, "Server stopped")

    if serverthread!=None:
        stopserver = True
        serverthread = None

    if httpd:
        httpd.server_close()
        
    httpd = None

def start_server():
    global httpd
    global serverthread

    obs.script_log(obs.LOG_DEBUG, "Server started")
    
    server_address = ('',portnum)
    httpd = ThreadingHTTPServer(server_address,Handler)

    if serverthread==None:
        serverthread = Thread(target = server_task)
        serverthread.start()
    
    #httpd = HTTPServer(server_address,Handler)
    
def manage_server():
    stop_server()
    start_server()

def play_task():
    global wasplaying
    global playlist
    
    if not is_source_playing():
        if wasplaying:
            hidesource()
            wasplaying = False

        #Check to see if there is anything new to play
        if len(playlist)>0:
            sound = playlist.pop(0)
            filename = sound[0]
            opts = sound[1]
            volume = 1.0
            speed = 1.0

            if "vol" in opts:
                volume = float(opts["vol"])

            if "speed" in opts:
                speed = float(opts["speed"])
            
            playsound(filename,volume,speed)
    else:
        wasplaying = True

def is_source_playing():
    source = obs.obs_get_source_by_name(sourcename)
    mediastate = obs.obs_source_media_get_state(source)
    #obs.script_log(obs.LOG_DEBUG, "Media state: "+str(mediastate))
    obs.obs_source_release(source)

    return mediastate == 1  #PLAYING is 1
    

def script_update(settings):
    global sourcename
    global portnum
    global audiofolder
    global testfile
    global oldportnum

    sourcename     = obs.obs_data_get_string(settings, "sourcename")
    audiofolder    = obs.obs_data_get_string(settings, "audiofolder")
    testfile       = obs.obs_data_get_string(settings, "testfile")
    portnum        = obs.obs_data_get_int(settings, "portnum")

    hidesource()
    unsetfilename()

    if oldportnum!=portnum:
        manage_server()
        oldportnum = portnum



def script_load(settings):
    obs.script_log(obs.LOG_DEBUG, "Loading script")
    hidesource()
    unsetfilename()
    #obs.timer_add(server_handle,100)
    start_server()
    obs.timer_add(play_task,100)

def script_unload():
    #obs.timer_remove(server_handle)
    hidesource()
    unsetfilename()
    stop_server()
    obs.script_log(obs.LOG_DEBUG, "Unloading script")

def hidesource():
    #obs.script_log(obs.LOG_DEBUG,"Trying to hide source "+sourcename)

    frontendscenes = obs.obs_frontend_get_scenes()
    #obs.script_log(obs.LOG_DEBUG,str(frontendscenes))
    
    for scenesource in frontendscenes:
        #obs.script_log(obs.LOG_DEBUG,str(scenesource))

    #scenesource = obs.obs_frontend_get_current_scene()
        scene = obs.obs_scene_from_source(scenesource)
        #obs.script_log(obs.LOG_DEBUG,"Scene "+str(scene))

        sceneitem = obs.obs_scene_find_source(scene,sourcename)
        if sceneitem:
            #obs.script_log(obs.LOG_DEBUG,"Scene item "+str(sceneitem))

            obs.obs_sceneitem_set_visible(sceneitem,False)
    
        #obs.obs_source_release(scenesource)
    obs.source_list_release(frontendscenes)

def unsetfilename():
    source = obs.obs_get_source_by_name(sourcename)
    #obs.script_log(obs.LOG_DEBUG,"Source "+str(source))

    settings = obs.obs_source_get_settings(source)
    #obs.script_log(obs.LOG_DEBUG,str(obs.obs_data_get_json(settings)))
    obs.obs_data_set_string(settings,"local_file","")
    #obs.script_log(obs.LOG_DEBUG,str(obs.obs_data_get_json(settings)))

    obs.obs_source_update(source,settings)
    
    obs.obs_data_release(settings)
    obs.obs_source_release(source)

def set_source_speed(source,speed):
    settings = obs.obs_source_get_settings(source)
    speedpct = int(speed*100)
    obs.obs_data_set_int(settings,"speed_percent",speedpct)
    obs.obs_source_update(source,settings)
    obs.obs_data_release(settings)

def playsound(filename,volume,speed):
    obs.script_log(obs.LOG_DEBUG,"Trying to play "+filename+" to source "+sourcename)

    scenesource = obs.obs_frontend_get_current_scene()
    scene = obs.obs_scene_from_source(scenesource)
    #obs.script_log(obs.LOG_DEBUG,"Scene "+str(scene))

    sceneitem = obs.obs_scene_find_source(scene,sourcename)
    #obs.script_log(obs.LOG_DEBUG,"Scene item "+str(sceneitem))

    source = obs.obs_sceneitem_get_source(sceneitem)

    obs.obs_source_set_volume(source,volume)
    set_source_speed(source,speed)
    
    obs.obs_sceneitem_set_visible(sceneitem,False)

    settings = obs.obs_source_get_settings(source)
    #obs.script_log(obs.LOG_DEBUG,str(obs.obs_data_get_json(settings)))
    obs.obs_data_set_string(settings,"local_file",audiofolder+filename)
    #obs.script_log(obs.LOG_DEBUG,str(obs.obs_data_get_json(settings)))

    obs.obs_source_update(source,settings)
    
    obs.obs_sceneitem_set_visible(sceneitem,True)
    
    obs.obs_data_release(settings)
    obs.obs_source_release(scenesource)

    #obs.script_log(obs.LOG_DEBUG,"Should be visible now...")

def testplay(props,prop):
    obs.script_log(obs.LOG_DEBUG, "Hit the test play button")
    playsound(testfile,100);

def script_defaults(settings):
    global sourcename
    global audiofolder
    global testfile
    global portnum
    
    sourcename= ""
    audiofolder = ""
    testfile = ""
    portnum = 8888
    
def script_properties():
    props = obs.obs_properties_create()

    obs.obs_properties_add_text(props, "sourcename", "Media Source Name", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(props, "audiofolder", "Audio Folder", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(props, "testfile", "Test File", obs.OBS_TEXT_DEFAULT)

    obs.obs_properties_add_button(props, "testbutton", "Test Playback", testplay)

    obs.obs_properties_add_int(props,"portnum","Port Number",1000,10000,1)
    
    return props
