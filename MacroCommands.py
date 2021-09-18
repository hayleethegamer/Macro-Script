#Example of some Macros
def defComs(dev, parent):
	@parent.command("KEY_UP", pressType="hold")
	async def volumeUp(pressType):
		parent.keyPress("XF86AudioRaiseVolume")
	@parent.command("KEY_DOWN", pressType="hold")
	async def volumeUp(pressType):
		parent.keyPress("XF86AudioLowerVolume")
	@parent.command("KEY_M", pressType="hold")
	async def volumeUp(pressType):
		parent.keyPress("XF86AudioMute")
	@parent.command("KEY_C")
	async def calcuator(pressType):
		parent.exeCom("gnome-calculator")
	@parent.command("KEY_F")
	async def firefox(pressType):
		parent.exeCom("firefox")
	
