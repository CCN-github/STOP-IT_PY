"""
      _                    _ _   
  ___| |_ ___  _ __       (_) |_ 
 / __| __/ _ \| '_ \ _____| | __|
 \__ \ || (_) | |_) |_____| | |_ 
 |___/\__\___/| .__/      |_|\__|
              |_|                
  AUTHOR: Frederick Verbruggen 
  Description: This is a basic version of the stop-signal task. 
"""
#####################################################################
### Start with importing some modules 
#####################################################################
from psychopy import gui, data, visual, event, core
import os
import numpy as np

#####################################################################
### Define variables etc. 
#####################################################################
# number of experimental blocks
NexpBL = 3 

# time variables
ITI = 0.500 # fixed intertrial interval
MAXRT = 1.25 # fixed maximum reaction time
SSD = 0.200 # start value; will be updated throughout the experiment
SSDstep = 0.050 # step size of the tracking procedure; this is also the lowest possible SSD
iFBT = 0.500 # immediate feedback interval
bFBT = 15. # break interval between blocks 

# parameters of the visual stimuli
size = 50 # size of the stimuli (in pixels)
XY = [[-size/2,0],[0,size/2],[0,size/4],[size/2,size/4],[size/2,-size/4],[0,-size/4],[0,-size/2]] # basic coordinates of a leftwards-pointing arrow
CLRS = ['green', 'red'] # colors of the go and stop arrows, respectively

# define response keys (in this case: the arrow keys and esc key)
keys = ('left', 'right', 'escape')

### DO NOT CHANGE THE DESIGN (UNLESS YOU REALLY KNOW WHAT YOU ARE DOING)
# Specify the design (2 by 4 in this instance) 
go = [0,1] # left (0) vs. right (1) arrows
signal = [0,0,0,1] # 1/4 of the trials are signal (1) trials
design = data.createFactorialTrialList({"goStim": go, "signal": signal})

#####################################################################
### Initialise experiment
#####################################################################
# By default, Psychopy changes the working directory based on the 
# location of the .py file. The output folder will be located here.
# The output folder will be created if it does not exist yet. 
wd = os.getcwd()
data_path = wd + "/output" 
if not os.path.isdir('output'): 
        os.mkdir('output')

# Get some user info and use this to determine the file name
info = {"Participant": "", "Session": "", "X extra: Gender": "", "X extra: Age": ""}
already_exists = True
while already_exists:
    myDlg = gui.DlgFromDict(dictionary = info, title = "Stop-signal Task")
    if myDlg.OK:
        file_name = data_path + "/stopIT_Subject_" + str(info["Participant"]) + "_Session_" + str(info["Session"]) 
        if not os.path.isfile(file_name + ".csv"):
            already_exists = False
        else:
            myDlg2 = gui.Dlg(title = "Error")
            myDlg2.addText("File already exists. Try another subject or session number")
            myDlg2.show()
    else: 
        print("*** EXPERIMENT ABORTED BY USER ***")
        core.quit()

#create an experiment handler (will be used to write the data to a file)
thisExp = data.ExperimentHandler(dataFileName=file_name, extraInfo = info)

# initialise screen & timer
win = visual.Window(fullscr=True, units = 'pix')
win.mouseVisible = False
exp_timer = core.Clock()

#####################################################################
### Functions required to run the experiment
#####################################################################
# function to present the instructions
def presentInstructions():
    file = open('STOPIT_instructions.txt', 'r')
    i = file.read()
    block_text = (  "\n\n"+
                    "The experimental phase consists of {0} eperimental blocks.\n\n"+
                    "Press the space bar to start").format(NexpBL)
    instruct = visual.TextStim(win, text=i+block_text)
    instruct.draw()
    win.flip()
    event.waitKeys(keyList="space") # wait for the space bar

# function to inform subjects that trials will start
def getReady():
    ready_stim = visual.TextStim(win,text='Get ready...')
    ready_stim.draw()
    win.flip()
    core.wait(2)

# function to present stimuli within a trial and register responses
def stimPresent(SSD): 
    # clear event buffer, screen and start ITI
    event.clearEvents(eventType="keyboard")
    win.flip()
    core.wait(ITI)
    
    # prepare the stimuli
    orient = [0,180] # left: orient[0] = 0; right: orient[1] = 180
    arrow_go = visual.ShapeStim(win, vertices=XY, fillColor=CLRS[0], lineWidth=0, pos=(0,0), ori = orient[trial["goStim"]])
    arrow_stop = visual.ShapeStim(win, vertices=XY, fillColor=CLRS[1], lineWidth=0, pos=(0,0), ori = orient[trial["goStim"]])

    # present the go stimulus
    arrow_go.draw()
    win.flip()
    
    # reset timer and variables
    exp_timer.reset()
    signalPresent = False
    signalTime = 0
    
    # start timer loop
    trial_continue = True
    while trial_continue:
        lapse = exp_timer.getTime() # elapsed time
        response=event.getKeys(keyList = keys) # check responses; only allow keys listed above 
        
        # abort experiment when escape key is pressed
        if response and response[0] == "escape":
            print("*** EXPERIMENT ABORTED BY USER ***")
            core.quit()

        # stop trial if MAXRT has elapsed or when a response is executed
        if lapse > MAXRT or response:
            trial_continue = False

        # check if we have to present a stop signal (take some drawing time into consideration)
        if lapse > (SSD - .010) and trial["signal"] == 1 and signalPresent == False:
            arrow_stop.draw()
            win.flip()
            signalTime = exp_timer.getTime()
            signalPresent = True
    
    # return some stuff 
    return (response, lapse, signalTime) 

# function to process the output of a trial and perform staircase tracking
# note: latencies are converted to ms at this stage
def output(b, SSD, response, lapse, signalTime):
    # add block number to the data file
    trials.addData("block", b) 

    # add the response and RT to the data file
    if response: 
        trials.addData("response", response[0])
        trials.addData("RT",np.round(1000*lapse, 0))
    else:
        trials.addData("response", 0)
        trials.addData("RT", 0)

    # determine if trial is correct or not
    # for signal trials, we immediately update the SSD value as well
    if trial["signal"] == 0:
        trials.addData("ssdReq", 0)
        trials.addData("ssdTrue", 0)
        if response and response[0] == keys[trial["goStim"]]: 
            trials.addData("acc", 1)
            fb_text = "correct response"
        else:
            trials.addData("acc", 0)
            if response: fb_text = "incorrect response"
            else: fb_text = "too slow"
    else: 
        trials.addData("ssdReq", np.round(1000*SSD,0))
        trials.addData("ssdTrue", np.round(1000*signalTime,0))
        if response:
            SSD -= SSDstep
            trials.addData("acc", 0)
            fb_text = "remember: try to stop"
        else:
            SSD += SSDstep
            trials.addData("acc", 1)
            fb_text = "correct stop"
        
        if SSD < SSDstep: SSD = SSDstep # SSD can never be lower than the step size (i.e. the stop signal will always follow the go stimulus)      
        if SSD >= MAXRT: SSD = MAXRT - SSDstep # SSD can never be equal or higher than MAXRT (i.e. the stop signal will always appear before the go stimulus is removed)
        
    # return updated SSD value and feedback text
    return (SSD, fb_text)

# function to present immediate feedback after a trial
def immediateFeedback(fb_text):
    fb_stim = visual.TextStim(win,text=fb_text)
    fb_stim.draw()
    win.flip()
    core.wait(iFBT)

# function to present the feedback at the end of a block 
def blockFeedback():
    # getting the relevant data from the TrialHandler is tricky;  
    # luckily we can use 'saveAsWideText' to turn 'trials' into a dataframe. 
    df = trials.saveAsWideText('temp.txt') 
    os.remove('temp.txt') # immediately delete the temp file to avoid clutter

    # separate stop-signal and no-signal trials
    ns = df.loc[(df.signal == 0), :]
    ss = df.loc[(df.signal == 1), :]
        
    # calculate mean RT, and probability of correct/incorrect/missed responses for nosignal trials  
    nsExe = ns.loc[(df.response > 0), 'RT'] # select all nosignal trials with a response
    nsCorrect = ns.loc[(df.acc > 0), 'RT'] # select all nosignal trials with a correct response
    nsMissed = ns.loc[(df.response == 0), :] # select all nosignal trials without a response
    
    avg_nsRT = np.mean(nsExe) # calculate mean RT (only excluding missed responses)
    prop_ns_Correct = float(len(nsCorrect)) /len(ns) # proportion of correct no-signal trials
    prop_ns_Missed = float(len(nsMissed)) /len(ns) # proportion of missed trials
    prop_ns_Incorrect = 1 - (prop_ns_Correct + prop_ns_Missed) # for completeness, also proportion of incorrect no-signal trials

    # calculate probability of a correct stop for stop-signal trials  
    ssCorrect = ss.loc[(df.acc > 0), :] # select all correct stop-signal trials
    prop_ss_Correct = float(len(ssCorrect))/len(ss) # proportion of correct stop-signal trials

    # put all the information in a string (including time counter) and present it on the screen 
    bF_timer = core.CountdownTimer(bFBT)
    while bF_timer.getTime() > 0:
        feedbackString =   ("NO-SIGNAL TRIALS: \n" + 
               "Average response time = {0:.0f} milliseconds\n" +
               "Proportion correct = {1:.3f} (should be close to 1)\n" + 
               "Proportion incorrect = {2:.3f}\n" + 
               "Proportion missed = {3:.3f}\n\n" + 
               "STOP-SIGNAL TRIALS: \n" + 
               "Proportion correct = {4:.3f} (should be close to 0.5)\n\n\n" + 
               "Seconds left to wait: {5:.0f}\n\n" + 
                "").format(avg_nsRT,prop_ns_Correct, prop_ns_Incorrect, prop_ns_Missed, prop_ss_Correct, np.ceil(bF_timer.getTime()))
        feedbackText = visual.TextStim(win, text=feedbackString)
        feedbackText.draw()
        win.flip()
    
    # they can now press the space bar to restart
    feedbackString2 = visual.TextStim(win, text="press the space bar to continue")
    feedbackString2.draw()
    win.flip()
    event.waitKeys(keyList="space") # wait for the space bar

# function to wrap up the experiment 
def goodbye():
    goodbye_text = ("This is the end of the experiment.\n\n"+
                   "Please inform the experimenter that you have finished.\n\n"+
                   "Thank you for your participation!")
    goodbye_stim = visual.TextStim(win,text=goodbye_text)
    goodbye_stim.draw()
    win.flip()
    event.waitKeys(keyList="space") # wait for the space bar

#####################################################################
### Run the actual experiment 
#####################################################################
# present the instructions 
presentInstructions()

# present the blocks. 
# the first block is a short practice block with immediate feedback. 
for b in range(1+NexpBL):
    # prepare the block
    if b == 0: nREP = 4 # how often should the main design (see above) be repeated in practice blocks? 
    else: nREP = 12 # how often should the main design (see above) be repeated in experimental blocks?
    
    trials = data.TrialHandler(design, nReps=nREP, method="fullRandom") # randomise trial list
    thisExp.addLoop(trials) # pass this to the experiment handler (to ensure proper storage)
    getReady(); # warn subjects that block will start
    
    # start the trial loop
    for trial in trials: 
        (response, lapse, signalTime) = stimPresent(SSD) # present the go and stop signals and check for responses
        (SSD,fb_text) = output(b, SSD, response, lapse, signalTime) # process the output of the trial
        if b == 0: immediateFeedback(fb_text) # present immediate feeback in the practice block
        thisExp.nextEntry() # inform ExperimentHandler that the current trial has ended
    
    # present block feedback between blocks (but not at the end of the experiment
    if b < NexpBL: blockFeedback() 

# wrap up  
goodbye() # present goodby message
thisExp.saveAsWideText(file_name, delim=',', appendFile=False) # in theory, this is done automatically when we abort the program. just to be safe...
thisExp.abort() # inform the ExperimentHandler that the run is now aborted. 
win.close() # close the Psychopy window
core.quit() # quit PsychoPy 




