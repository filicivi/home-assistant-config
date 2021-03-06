################################################################################
# Battery Checker
#
# Most of this is straight from the AppDaemon examples, with the exception
# of the notification method, that has been changed to the generic notify
# service.
# 
# Eventually,I would like to update this to where the threshold setting is
# set by an input_number and controlled through the UI.
################################################################################

import appdaemon.plugins.hass.hassapi as hass
import datetime
import globals

#
# App to send email report for devices running low on battery
#
# Args:
#
# threshold = value below which battery levels are reported and email is sent
# always_send = set to 1 to override threshold and force send
#
# None
#
# Release Notes
#
# Version 1.0:
#   Initial Version

class Battery(hass.Hass):

  def initialize(self):
    #self.check_batteries({"force": 1})
    time = datetime.time(6, 0, 0)
    self.run_daily(self.check_batteries, time)
    
  def check_batteries(self, kwargs):
    devices = self.get_state()
    values = {}
    low = []
    for device in devices:
      battery = None
      if "attributes" in devices[device]:
          if "battery" in devices[device]["attributes"]:
            battery = devices[device]["attributes"]["battery"]
          if "battery_level" in devices[device]["attributes"]:
            battery = devices[device]["attributes"]["battery_level"]
          if battery != None:
            if battery < int(self.args["threshold"]):
              low.append(device)
            values[device] = battery
    message = "Bettery Level Report\n\n"
    if low:
      message += "The following devices are low: (< {}) ".format(self.args["threshold"])
      for device in low:
        message = message + device + " "
      message += "\n\n"
    
    message += "Battery Levels:\n\n"
    for device in sorted(values):
      message += "{}: {}\n".format(device, values[device])
      
    if low or ("always_send" in self.args and self.args["always_send"] == "1") or ("force" in kwargs and kwargs["force"] == 1):
      self.notify(message, title="Home Assistant Battery Report")