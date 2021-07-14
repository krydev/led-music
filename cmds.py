ON_SWITCH = "7e0404f00001ff00ef"
OFF_SWITCH = "7e0404000000ff00ef"

def set_brightness(val):
	return f"7e0001{val:02x}00000000ef"

def set_rgb_color(r, g, b):
	return f"7e000503{r:02x}{g:02x}{b:02x}00ef"
