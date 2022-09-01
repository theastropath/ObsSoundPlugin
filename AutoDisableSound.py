import obspython as obs

from time import sleep
import os

sourcename = ""
audiofolder = ""
testfile = ""

wasplaying = False

# ------------------------------------------------------------

def script_description():
    return "Automatically disables a Media Source once it has finished playing a sound and clears the filename\n\nBy TheAstropath"


def play_task():
    global wasplaying
    
    if not is_source_playing():
        if wasplaying:
            hidesource()
            wasplaying = False

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

    sourcename     = obs.obs_data_get_string(settings, "sourcename")

    hidesource()
    unsetfilename()



def script_load(settings):
    obs.script_log(obs.LOG_DEBUG, "Loading script")
    hidesource()
    unsetfilename()
    obs.timer_add(play_task,100)

def script_unload():
    #obs.timer_remove(server_handle)
    hidesource()
    unsetfilename()
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


def script_defaults(settings):
    global sourcename
    
    sourcename= ""
    
def script_properties():
    props = obs.obs_properties_create()

    obs.obs_properties_add_text(props, "sourcename", "Media Source Name", obs.OBS_TEXT_DEFAULT)
    
    return props
