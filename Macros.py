#!/usr/bin/python3
#This Code is Executed as root!!!!!
def set_procname(newname):
	newname = newname.encode("utf-8")
	from ctypes import cdll, byref, create_string_buffer
	libc = cdll.LoadLibrary('libc.so.6')    #Loading a 3rd party library C
	buff = create_string_buffer(len(newname)+1) #Note: One larger than the name (man prctl says that)
	buff.value = newname                 #Null terminated string as it should be
	libc.prctl(15, byref(buff), 0, 0, 0) #Refer to "#define" of "/usr/include/linux/prctl.h" for the misterious value 16 & arg[3..5] are zero as the man page says.
set_procname("MacroManger.py")

import tkinter as tk
import os
import sys


class Error(tk.Frame):
	def __init__(self, errorMess, master=None):
		if os.getuid() == 0:
			os.setuid(parsed.id)
		super().__init__(master)
		self.window()
		self.text(errorMess)
		self.create()
		self.master = master
		self.pack()
		self.mainloop()
	def window(self):
		self.master.geometry("300x50") #WxH
		self.master.title("Error Message")
	def create(self):
		self.button = tk.Button(self)
		self.button["text"] = "OK"
		self.button["command"] = self.master.destroy
		self.button.pack(side="bottom")
	def text(self, errorMess):
		tk.Label(self.master, text=errorMess).pack()

try:
	from evdev import InputDevice, categorize, ecodes
except ImportError:
	errorMessage = "Error: evdev not found, please install python-evdev or python3-evdev"
	ErrorDialog = Error(errorMessage, tk.Tk())
	sys.exit()

try:
	dev = InputDevice("/dev/input/by-id/IDForInputDevice")
except FileNotFoundError:
	errorMessage = "Error, device not present, exiting..."
	ErrorDialog = Error(errorMessage, tk.Tk())
	sys.exit()
except PermissionError:
	errorMessage = "Error, Permission Denied. Exiting..."
	ErrorDialog = Error(errorMessage, tk.Tk())
	sys.exit()
dev.grab()
userID = int(os.environ["SUDO_UID"])
if userID == 0:
	errorMessage = "Error, Script not allowed to run as root the entire time."
	ErrorDialog = Error(errorMessage, tk.Tk())
	sys.exit()
else:
	os.setuid(userID) #gets ID From user name

#Code from here on rus as user
import asyncio
import signal

import MacroCommands

class Manager():
	def __init__(self):
		self.loop = asyncio.get_event_loop()
		#self.loop.add_signal_handler(signal.SIGINT, lambda: self.signalHandler())
		self.errorCount = 0
		self.waiting = False
		self.comList = {}
		MacroCommands.defComs(dev, self)
		self.run()
	
	def _stop(self):
		print("Stopping!!")
		pending = asyncio.all_tasks()
		gathered = asyncio.gather(*pending)
		try:
			gathered.cancel()
			self.loop.run_until_complete(gathered)
			gathered.exception()
		except:
			pass
		self.loop.stop()
		dev.close()
		sys.exit()
	def signalHandler(self):
		self._stop()
	
	def run(self):
		try:
			self.loop.run_until_complete(self.start())
		except (KeyboardInterrupt):
			self._stop()
	
	async def start(self):
		for event in dev.read_loop():
			if not self.waiting:
				self.loop.call_later(60, self.decreaseErrorCount, self)
				self.waiting == True
			if event.type == ecodes.EV_KEY:
				key = categorize(event)
				if key.keycode == "KEY_ESC":
					self._stop()
				if key.keystate == key.key_down:
					await self.dispatch("keyPress", key.keycode)
				if key.keystate == key.key_hold:
					await self.dispatch("keyHold", key.keycode)
	
	#Event Handling
	async def runEvent(self, event, *args, **kwargs):  
		try:
			await getattr(self,event)(*args, **kwargs)
		except asyncio.CancelledError:
			pass
		except Exception:
			try:
				await self.errorHandleing()
			except asyncio.CancelledError:
				pass
	async def dispatch(self, event, *args, **kwargs):
		method = "on_" + event
		if hasattr(self, method):
			#asyncio.ensure_future(self.runEvent(method, *args, **kwargs), loop=self.loop)
			#asyncio.create_task(self.runEvent(method, *args, **kwargs))
			#self.loop.create_task(self.runEvent(method, *args, **kwargs))
			await self.runEvent(method, *args, **kwargs)
	
	#Events
	async def on_keyPress(self, key):
		pressType = "press"
		try:
			await self.comList[key].run(pressType)
		except KeyError:
			pass
	async def on_keyHold(self, key):
		pressType = "hold"
		try:
			await self.comList[key].run(pressType)
		except KeyError:
			pass
	async def on_error(self, error):
		await self.errorHandleing(error)
		
	#Commands
	def command(self, *arg, **kwargs):
		return Command(self, *arg, **kwargs)
	
	
	
	#Helpers
	def exeCom(self, command, GUI=True):
		if GUI:
			command = command + " </dev/null &>/dev/null &"
		os.system(command)
	def keyWrite(self, message):
		self.exeCom("xdotool type \"{}\"".format(message), GUI=False)
	def keyPress(self, keyID):
		self.exeCom("xdotool key {}".format(keyID), GUI=False)
	
	#Error Handling
	def decreaseErrorCount(self):
		self.errorCount -= 1
		self.waiting = False
	async def errorHandleing(self, errorMessage=None):
		self.errorCount += 1
		if errorMessage == None:
			errorMessage = "There was an unknown Error."
		ErrorDialog = Error(errorMessage, tk.Tk())
		if self.errorCount >= 20:
			sys.exit()

class Command:
	def __init__(self, parent, macro, pressType="press"):
		self.macro = macro
		self.parent = parent
		self.pressType=pressType
		self.parent.comList[macro] = self
	
	def __call__(self, func):
		""" Make it able to be a decorator """
		self.func = func
		return self
	async def run(self, keyPress):
		if keyPress == "hold" and self.pressType != "hold":
			return
		await self.func(keyPress)


Manager()
