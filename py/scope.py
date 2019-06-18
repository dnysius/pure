# -*- coding: utf-8 -*-
##"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
## Copyright © 2015 Keysight Technologies Inc. All rights reserved.
##
## You have a royalty-free right to use, modify, reproduce and distribute this
## example file (and/or any modified version) in any way you find useful, provided
## that you agree that Keysight has no warranty, obligations or liability for any
## Sample Application Files.
##
##"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

import sys
import visa # PyVisa info @ http://PyVisa.readthedocs.io/en/stable/
import time
import numpy as np
from os import mkdir, listdir, makedirs
from os.path import isdir, isfile, join, dirname, exists
import re
from tqdm import tqdm # progress bar reporting
_nsre = re.compile('([0-9]+)')

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(_nsre, s)] 
## INSTRUCTIONS:
## Edit in the VISA address of the oscilloscope
## Edit in the file save locations ## IMPORTANT NOTE:  This script WILL overwrite previously saved files!
## Manually (or write more code) acquire data on the oscilloscope.  Ensure that it finished (Run/Stop button is red).
class Scope:
     
     def __init__(self, directory, filename="scope"):
          ## Number of Points to request
          self.USER_REQUESTED_POINTS = 8000000
              ## None of these scopes offer more than 8,000,000 points
              ## Setting this to 8000000 or more will ensure that the maximum number of available points is retrieved, though often less will come back.
              ## Average and High Resolution acquisition types have shallow memory depth, and thus acquiring waveforms in Normal acq. type and post processing for High Res. or repeated acqs. for Average is suggested if more points are desired.
              ## Asking for zero (0) points, a negative number of points, fewer than 100 points, or a non-integer number of points (100.1 -> error, but 100. or 100.0 is ok) will result in an error, specifically -222,"Data out of range"
          
          ## Initialization constants
          self.SCOPE_VISA_ADDRESS = 'USB0::0x0957::0x1799::MY52102738::INSTR' # Get this from Keysight IO Libraries Connection Expert
          self.GLOBAL_TOUT =  10000 # IO time out in milliseconds
          
          ## Save Locations
          self.BASE_FILE_NAME = filename + "_"  # want format to be NAME_[ROW]_[COLUMN].npy
          self.BASE_DIRECTORY = directory
          
          if not exists(self.BASE_DIRECTORY):
               mkdir(self.BASE_DIRECTORY)
          ############################################################################
          ## Optional automatic subfolder naming, replace BASE_DIRECTORY with SUBFOLDER
          ############################################################################
#          self.dnames = [d for d in listdir(self.BASE_DIRECTORY) if isdir(join(self.BASE_DIRECTORY, d))]
#          self.dnames.sort(key=natural_sort_key)
#          if len(self.dnames) > 0:
#               
#               try:
#                    i = int(self.dnames[-1][len(self.BASE_SUBDIR):]) + 1
#                    
#               except:
#                    i = 0
#                    raise TypeError
#          else:
#               i = 0
#                         
#          self.SUBFOLDER = self.BASE_DIRECTORY+self.BASE_SUBDIR+"{0}\\".format(i) 
#          if not isdir(self.SUBFOLDER):
#               mkdir(self.SUBFOLDER)
          self.fnames = [f for f in listdir(self.BASE_DIRECTORY) if isfile(join(self.BASE_DIRECTORY, f)) and f[-3:] == 'npy']
          self.fnames.sort(key=natural_sort_key)
          ##############################################################################################################################################################################
          ##############################################################################################################################################################################
          ## Main code
          ##############################################################################################################################################################################
          ##############################################################################################################################################################################       
#          sys.stdout.write("Script is running.  This may take a while...")
          ##############################################################################################################################################################################
          ##############################################################################################################################################################################
          ## Connect and initialize scope
          ##############################################################################################################################################################################
          ##############################################################################################################################################################################
          
          ## Define VISA Resource Manager & Install directory
          self.rm = visa.ResourceManager('C:\\Windows\\System32\\visa32.dll') # this uses PyVisa
          ## Open Connection
          ## Define & open the scope by the VISA address ; # This uses PyVisa
          try:
              self.KsInfiniiVisionX = self.rm.open_resource(self.SCOPE_VISA_ADDRESS)
          except Exception:
              print("Unable to connect to oscilloscope at " + str(self.SCOPE_VISA_ADDRESS) + ". Aborting script.\n")
              sys.exit()
              
          
          ## Set Global Timeout
          ## This can be used wherever, but local timeouts are used for Arming, Triggering, and Finishing the acquisition... Thus it mostly handles IO timeouts
          self.KsInfiniiVisionX.timeout = self.GLOBAL_TOUT
          
          ## Clear the instrument bus
          self.KsInfiniiVisionX.clear()
          
          ## DO NOT RESET THE SCOPE! - since that would wipe out data...
          
          ## Data should already be acquired and scope should be STOPPED (Run/Stop button is red).

          ##########################################################
          ##########################################################
          ## Determine Which channels are on AND have acquired data - Scope should have already acquired data and be in a stopped state (Run/Stop button is red).
          
          #########################################
          ## Get Number of analog channels on scope
          self.IDN = str(self.KsInfiniiVisionX.query("*IDN?"))
          ## Parse IDN
          self.IDN = self.IDN.split(',') # IDN parts are separated by commas, so parse on the commas
          self.MODEL = self.IDN[1]
          if list(self.MODEL[1]) == "9": # This is the test for the PXIe scope, M942xA)
              self.NUMBER_ANALOG_CHS = 2
          else:
              self.NUMBER_ANALOG_CHS = int(self.MODEL[len(self.MODEL)-2])
          if self.NUMBER_ANALOG_CHS == 2:
              self.CHS_LIST = [0,0] # Create empty array to store channel states
          else:
              self.CHS_LIST = [0,0,0,0]
          self.NUMBER_CHANNELS_ON = 0
          ## After the CHS_LIST array is filled it could, for example look like: if chs 1,3 and 4 were on, CHS_LIST = [1,0,1,1]
          ###############################################
          ## Pre-allocate holders for the vertical Pre-ambles and Channel units
          
          self.ANALOGVERTPRES = np.zeros([12])
              ## For readability: ANALOGVERTPRES = (Y_INCrement_Ch1, Y_INCrement_Ch2, Y_INCrement_Ch3, Y_INCrement_Ch4, Y_ORIGin_Ch1, Y_ORIGin_Ch2, Y_ORIGin_Ch3, Y_ORIGin_Ch4, Y_REFerence_Ch1, Y_REFerence_Ch2, Y_REFerence_Ch3, Y_REFerence_Ch4)
          
          self.CH_UNITS = ["BLANK", "BLANK", "BLANK", "BLANK"]
          
          #########################################
          ## Actually find which channels are on, have acquired data, and get the pre-amble info if needed.
          ## The assumption here is that, if the channel is off, even if it has data behind it, data will not be retrieved from it.
          ## Note that this only has to be done once for repetitive acquisitions if the channel scales (and on/off) are not changed.
          
          self.KsInfiniiVisionX.write(":WAVeform:POINts:MODE MAX") # MAX mode works for all acquisition types, so this is done here to avoid Acq. Type vs points mode problems. Adjusted later for specific acquisition types.
          
          ch = 1 # Channel number
          for each_value in self.CHS_LIST:
              On_Off = int(self.KsInfiniiVisionX.query(":CHANnel" + str(ch) + ":DISPlay?")) # Is the channel displayed? If not, don't pull.
              if On_Off == 1: # Only ask if needed... but... the scope can acquire waveform data even if the channel is off (in some cases) - so modify as needed
                  Channel_Acquired = int(self.KsInfiniiVisionX.query(":WAVeform:SOURce CHANnel" + str(ch) + ";POINts?")) # If this returns a zero, then this channel did not capture data and thus there are no points
                  ## Note that setting the :WAV:SOUR to some channel has the effect of turning it on
              else:
                  Channel_Acquired = 0
              if Channel_Acquired == 0 or On_Off == 0: # Channel is off or no data acquired
                  self.KsInfiniiVisionX.write(":CHANnel" + str(ch) + ":DISPlay OFF") # Setting a channel to be a waveform source turns it on... so if here, turn it off.
                  self.CHS_LIST[ch-1] = 0 # Recall that python indices start at 0, so ch1 is index 0
              else: # Channel is on AND data acquired
                  self.CHS_LIST[ch-1] = 1 # After the CHS_LIST array is filled it could, for example look like: if chs 1,3 and 4 were on, CHS_LIST = [1,0,1,1]
                  self.NUMBER_CHANNELS_ON += 1
                  ## Might as well get the pre-amble info now
                  Pre = self.KsInfiniiVisionX.query(":WAVeform:PREamble?").split(',') # ## The programmer's guide has a very good description of this, under the info on :WAVeform:PREamble.
                      ## In above line, the waveform source is already set; no need to reset it.
                  self.ANALOGVERTPRES[ch-1]  = float(Pre[7]) # Y INCrement, Voltage difference between data points; Could also be found with :WAVeform:YINCrement? after setting :WAVeform:SOURce
                  self.ANALOGVERTPRES[ch+3]  = float(Pre[8]) # Y ORIGin, Voltage at center screen; Could also be found with :WAVeform:YORigin? after setting :WAVeform:SOURce
                  self.ANALOGVERTPRES[ch+7]  = float(Pre[9]) # Y REFerence, Specifies the data point where y-origin occurs, always zero; Could also be found with :WAVeform:YREFerence? after setting :WAVeform:SOURce
                  ## In most cases this will need to be done for each channel as the vertical scale and offset will differ. However,
                      ## if the vertical scales and offset are identical, the values for one channel can be used for the others.
                      ## For math waveforms, this should always be done.
                  self.CH_UNITS[ch-1] = str(self.KsInfiniiVisionX.query(":CHANnel" + str(ch) + ":UNITs?").strip('\n')) # This isn't really needed but is included for completeness
              ch += 1
          del ch, each_value, On_Off, Channel_Acquired
          
          ##########################
          if self.NUMBER_CHANNELS_ON == 0:
              self.KsInfiniiVisionX.clear()
              self.KsInfiniiVisionX.close()
              sys.exit("No data has been acquired. Properly closing scope and aborting script.")
          
          ############################################
          ## Find first channel on (as needed/desired)
          ch = 1
          for each_value in self.CHS_LIST:
              if each_value == 1:
                  self.FIRST_CHANNEL_ON = ch
                  break
              ch +=1
          del ch, each_value
          
          ############################################
          ## Find last channel on (as needed/desired)
          ch = 1
          for each_value in self.CHS_LIST:
              if each_value == 1:
                  self.LAST_CHANNEL_ON = ch
              ch +=1
          del ch, each_value
          
          ############################################
          ## Create list of Channel Numbers that are on
          self.CHS_ON = [] # Empty list
          ch = 1
          for each_value in self.CHS_LIST:
              if each_value == 1:
                  self.CHS_ON.append(int(ch)) # for example, if chs 1,3 and 4 were on, CHS_ON = [1,3,4]
              ch +=1
          del ch, each_value
          
          #####################################################
          
          ################################################################################################################
          ## Setup data export - For repetitive acquisitions, this only needs to be done once unless settings are changed
          
          self.KsInfiniiVisionX.write(":WAVeform:FORMat WORD") # 16 bit word format... or BYTE for 8 bit format - WORD recommended, see more comments below when the data is actually retrieved
          self.KsInfiniiVisionX.write(":WAVeform:BYTeorder LSBFirst") # Explicitly set this to avoid confusion - only applies to WORD FORMat
          self.KsInfiniiVisionX.write(":WAVeform:UNSigned 0") # Explicitly set this to avoid confusion
          
          #####################################################################################################################################
          #####################################################################################################################################
          ## Set and get points to be retrieved - For repetitive acquisitions, this only needs to be done once unless scope settings are changed
          ## This is non-trivial, but the below algorithm always works w/o throwing an error, as long as USER_REQUESTED_POINTS is a positive whole number (positive integer)
          
          #########################################################
          ## Determine Acquisition Type to set points mode properly
          
          self.ACQ_TYPE = str(self.KsInfiniiVisionX.query(":ACQuire:TYPE?")).strip("\n")
                  ## This can also be done when pulling pre-ambles (pre[1]) or may be known ahead of time, but since the script is supposed to find everything, it is done now.
          if self.ACQ_TYPE == "AVER" or self.ACQ_TYPE == "HRES": # Don't need to check for both types of mnemonics like this: if ACQ_TYPE == "AVER" or ACQ_TYPE == "AVERage": because the scope ALWAYS returns the short form
              self.POINTS_MODE = "NORMal" # Use for Average and High Resoultion acquisition Types.
          else:
              self.POINTS_MODE = "RAW" # Use for Acq. Type NORMal or PEAK

          ###########################################################################################################
          ## Find max points for scope as is, ask for desired points, find how many points will actually be returned
              ## KEY POINT: the data must be on screen to be retrieved.  If there is data off-screen, :WAVeform:POINts? will not "see it."
                  ## Addendum 1 shows how to properly get all data on screen, but this is never needed for Average and High Resolution Acquisition Types,
                  ## since they basically don't use off-screen data; what you see is what you get.
          
          ## First, set waveform source to any channel that is known to be on and have points, here the FIRST_CHANNEL_ON - if we don't do this, it could be set to a channel that was off or did not acquire data.
          self.KsInfiniiVisionX.write(":WAVeform:SOURce CHANnel" + str(self.FIRST_CHANNEL_ON))
          
          ## The next line is similar to, but distinct from, the previously sent command ":WAVeform:POINts:MODE MAX".  This next command is one of the most important parts of this script.
          self.KsInfiniiVisionX.write(":WAVeform:POINts MAX") # This command sets the points mode to MAX AND ensures that the maximum # of points to be transferred is set, though they must still be on screen
          
          ## Since the ":WAVeform:POINts MAX" command above also changes the :POINts:MODE to MAXimum, which may or may not be a good thing, so change it to what is needed next.
          self.KsInfiniiVisionX.write(":WAVeform:POINts:MODE " + str(self.POINTS_MODE))
          ## If measurements are also being made, they are made on the "measurement record."  This record can be accessed by using:
              ## :WAVeform:POINts:MODE NORMal instead of :WAVeform:POINts:MODE RAW
              ## Please refer to the progammer's guide for more details on :WAV:POIN:MODE RAW/NORMal/MAX
          
          ## Now find how many points are actually currently available for transfer in the given points mode (must still be on screen)
          self.MAX_CURRENTLY_AVAILABLE_POINTS = int(self.KsInfiniiVisionX.query(":WAVeform:POINts?")) # This is the max number of points currently available - this is for on screen data only - Will not change channel to channel.
          ## NOTES:
              ## For getting ALL of the data off of the scope, as opposed to just what is on screen, see Addendum 1
              ## For getting ONLY CERTAIN data points, see Addendum 2
              ## The methods shown in these addenda are combinable
              ## The number of points can change with the number of channels that have acquired data, the Acq. Mode, Acq Type, time scale (they must be on screen to be retrieved),
                  ## number of channels on, and the acquisition method (:RUNS/:STOP, :SINGle, :DIGitize), and :WAV:POINts:MODE
          
          ## The scope will return a -222,"Data out of range" error if fewer than 100 points are requested, even though it may actually return fewer than 100 points.
          if self.USER_REQUESTED_POINTS < 100:
              self.USER_REQUESTED_POINTS = 100
          ## One may also wish to do other tests, such as: is it a whole number (integer)?, is it real? and so forth...
          
          if self.MAX_CURRENTLY_AVAILABLE_POINTS < 100:
              self.MAX_CURRENTLY_AVAILABLE_POINTS = 100
          
          if self.USER_REQUESTED_POINTS > self.MAX_CURRENTLY_AVAILABLE_POINTS or self.ACQ_TYPE == "PEAK":
               self.USER_REQUESTED_POINTS = self.MAX_CURRENTLY_AVAILABLE_POINTS
               ## Note: for Peak Detect, it is always suggested to transfer the max number of points available so that narrow spikes are not missed.
               ## If the scope is asked for more points than :ACQuire:POINts? (see below) yields, though, not necessarily MAX_CURRENTLY_AVAILABLE_POINTS, it will throw an error, specifically -222,"Data out of range"
          
          ## If one wants some other number of points...
          ## Tell it how many points you want
          self.KsInfiniiVisionX.write(":WAVeform:POINts " + str(self.USER_REQUESTED_POINTS))
          
          ## Then ask how many points it will actually give you, as it may not give you exactly what you want.
          self.NUMBER_OF_POINTS_TO_ACTUALLY_RETRIEVE = int(self.KsInfiniiVisionX.query(":WAVeform:POINts?"))
          
          #####################################################################################################################################
          #####################################################################################################################################
          ## Get timing pre-amble data and create time axis
          ## One could just save off the preamble factors and #points and post process this later...
          
          Pre = self.KsInfiniiVisionX.query(":WAVeform:PREamble?").split(',') # This does need to be set to a channel that is on, but that is already done... e.g. Pre = self.KsInfiniiVisionX.query(":WAVeform:SOURce CHANnel" + str(FIRST_CHANNEL_ON) + ";PREamble?").split(',')
          ## While these values can always be used for all analog channels, they need to be retrieved and used separately for math/other waveforms as they will likely be different.
          #ACQ_TYPE    = float(Pre[1]) # Gives the scope Acquisition Type; this is already done above in this particular script
          self.X_INCrement = float(Pre[4]) # Time difference between data points; Could also be found with :WAVeform:XINCrement? after setting :WAVeform:SOURce
          self.X_ORIGin    = float(Pre[5]) # Always the first data point in memory; Could also be found with :WAVeform:XORigin? after setting :WAVeform:SOURce
          self.X_REFerence = float(Pre[6]) # Specifies the data point associated with x-origin; The x-reference point is the first point displayed and XREFerence is always 0.; Could also be found with :WAVeform:XREFerence? after setting :WAVeform:SOURce
          ## This could have been pulled earlier...
          del Pre
              ## The programmer's guide has a very good description of this, under the info on :WAVeform:PREamble.
              ## This could also be reasonably be done when pulling the vertical pre-ambles for any channel that is on and acquired data.
              ## This is the same for all channels.
              ## For repetitive acquisitions, it only needs to be done once unless settings change.
          
          self.DataTime = ((np.linspace(0,self.NUMBER_OF_POINTS_TO_ACTUALLY_RETRIEVE-1,self.NUMBER_OF_POINTS_TO_ACTUALLY_RETRIEVE)-self.X_REFerence)*self.X_INCrement)+self.X_ORIGin
          if self.ACQ_TYPE == "PEAK": # This means Peak Detect Acq. Type
              self.DataTime = np.repeat(self.DataTime,2)
              ##  The points come out as Low(time1),High(time1),Low(time2),High(time2)....
              ### SEE IMPORTANT NOTE ABOUT PEAK DETECT AT VERY END, specific to fast time scales
          
          #####################################################################################################################################
          #####################################################################################################################################
          ## Pre-allocate data array
              ## Obviously there are numerous ways to actually place data  into an array... this is just one
          
          if self.ACQ_TYPE == "PEAK": # This means peak detect mode ### SEE IMPORTANT NOTE ABOUT PEAK DETECT MODE AT VERY END, specific to fast time scales
              self.Wav_Data = np.zeros([2*self.NUMBER_OF_POINTS_TO_ACTUALLY_RETRIEVE,self.NUMBER_CHANNELS_ON])
              ## Peak detect mode returns twice as many points as the points query, one point each for LOW and HIGH values
          else: # For all other acquistion modes
              self.Wav_Data = np.zeros([self.NUMBER_OF_POINTS_TO_ACTUALLY_RETRIEVE,self.NUMBER_CHANNELS_ON])
          
          ###################################################################################################
          ###################################################################################################
          ## Determine number of bytes that will actually be transferred and set the "chunk size" accordingly.
          
              ## When using PyVisa, this is in fact completely unnecessary, but may be needed in other leagues, MATLAB, for example.
              ## However, the benefit in Python is that the transfers can take less time, particularly longer ones.
          
          ## Get the waveform format
          WFORM = str(self.KsInfiniiVisionX.query(":WAVeform:FORMat?"))
          if WFORM == "BYTE":
              FORMAT_MULTIPLIER = 1
          else: #WFORM == "WORD"
              FORMAT_MULTIPLIER = 2
          
          if self.ACQ_TYPE == "PEAK":
              POINTS_MULTIPLIER = 2 # Recall that Peak Acq. Type basically doubles the number of points.
          else:
              POINTS_MULTIPLIER = 1
          
          self.TOTAL_BYTES_TO_XFER = POINTS_MULTIPLIER * self.NUMBER_OF_POINTS_TO_ACTUALLY_RETRIEVE * FORMAT_MULTIPLIER + 11
              ## Why + 11?  The IEEE488.2 waveform header for definite length binary blocks (what this will use) consists of 10 bytes.  The default termination character, \n, takes up another byte.
                  ## If you are using mutliplr termination characters, adjust accordingly.
              ## Note that Python 2.7 uses ASCII, where all characters are 1 byte.  Python 3.5 uses Unicode, which does not have a set number of bytes per character.
          
          ## Set chunk size:
              ## More info @ http://pyvisa.readthedocs.io/en/stable/resources.html
          if self.TOTAL_BYTES_TO_XFER >= 400000:
              self.KsInfiniiVisionX.chunk_size = self.TOTAL_BYTES_TO_XFER
          
          
     def grab(self):
          #####################################################
          #####################################################
          ## Pull waveform data, scale it
          self.fnames = [f for f in listdir(self.BASE_DIRECTORY) if isfile(join(self.BASE_DIRECTORY, f)) and (f[-3:] == 'npy')]
          self.fnames.sort(key=natural_sort_key)
          now = time.clock() # Only to show how long it takes to transfer and scale the data.
          i  = 0 # index of Wav_data, recall that python indices start at 0, so ch1 is index 0
          for channel_number in self.CHS_ON:
                  ## Gets the waveform in 16 bit WORD format
              ## The below method uses an IEEE488.2 compliant definite length binary block transfer invoked by :WAVeform:DATA?.
                  ## ASCII transfers are also possible, but MUCH slower.
                  self.Wav_Data[:,i] = np.array(self.KsInfiniiVisionX.query_binary_values(':WAVeform:SOURce CHANnel' + str(channel_number) + ';DATA?', "h", False)) # See also: https://PyVisa.readthedocs.io/en/stable/rvalues.html#reading-binary-values
                  self.Wav_Data[:,i] = ((self.Wav_Data[:,i]-self.ANALOGVERTPRES[channel_number+7])*self.ANALOGVERTPRES[channel_number-1])+self.ANALOGVERTPRES[channel_number+3]
                      ## For clarity: Scaled_waveform_Data[*] = [(Unscaled_Waveform_Data[*] - Y_reference) * Y_increment] + Y_origin
          
                  i +=1
          
          ## Reset the chunk size back to default if needed.
          if self.TOTAL_BYTES_TO_XFER >= 400000:
              self.KsInfiniiVisionX.chunk_size = 20480
              ## If you don't do this, and now wanted to do something else... such as ask for a measurement result, and leave the chunk size set to something large,
                  ## it can really slow down the script, so set it back to default, which works well.
          
          del i, channel_number
#          print("\n\nIt took " + str(time.clock() - now) + " seconds to transfer and scale " + str(self.NUMBER_CHANNELS_ON) + " channel(s). Each channel had " + str(self.NUMBER_OF_POINTS_TO_ACTUALLY_RETRIEVE) + " points.\n")
          del now         
          ################################################################################################
          ################################################################################################
          ## Save waveform data -  really, there are MANY ways to do this, of course
          ################################################################################################
          ################################################################################################
          
          ## If saving repetitive acquisitions, it may be better to just save off a single time axis file, and not just replicate it w/ every save

          ########################################################
          ## As a NUMPY BINARY file - fast and small, but really only good for python - can't use header
          ########################################################
          now = time.clock() # Only to show how long it takes to save
          if len(self.fnames) >= 1:
               recent = self.fnames[-1]
               pre = len(self.BASE_FILE_NAME)
               suf = -4
               try:
                    i = int(recent[pre:suf]) + 1
               except:
                    raise TypeError
          else:
               i = 0
          
          
          filename = join(self.BASE_DIRECTORY, self.BASE_FILE_NAME +"{0}".format(i)+ ".npy")
               
          with open(filename, 'wb') as filehandle: # wb means open for writing in binary; can overwrite
              np.save(filehandle, np.insert(self.Wav_Data,0,self.DataTime,axis=1))
#          print("It took " + str(time.clock() - now) + " seconds to save " + str(self.NUMBER_CHANNELS_ON) + " channels and the time axis in binary format. Each channel had " + str(self.NUMBER_OF_POINTS_TO_ACTUALLY_RETRIEVE) + " points.\n")
          del now
          
          ## Read the NUMPY BINARY data back into python with:
#          with open(filename, 'rb') as filehandle: # rb means open for reading binary
#              recalled_NPY_data = np.load(filehandle)
              
          del filename, filehandle, i


     def close(self):
          ###################################################################
          ###################################################################
          ## Done with scope operations - Close Connection to scope properly
          
          self.KsInfiniiVisionX.clear()
          self.KsInfiniiVisionX.close()
          del self.KsInfiniiVisionX
          
if __name__=='__main__':
     scope = Scope("C:\\Users\\dionysius\\Desktop\\PURE\\pure\\data\\30deg\\3FOC5in")
#     pbar = tqdm(range(20))
#     for i in pbar:
#     oscilloscope.grab()
#          pbar.set_description("Processing {0}".format(i))
     done = False
     while not done:
          cmd = input('//\t')
          if cmd =='':
               scope.grab()
          elif cmd == 'x':
               done = True
          