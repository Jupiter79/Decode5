import pyaudio
import numpy
import sys
import sounddevice as sd
import threading
from colorama import Fore, Back, Style, init

# Einstellungen
TOLERANCE = 20
# Toleranz in Hertz (+-)

INPUT_DEVICE = 1
# Mikrofon ID

NOISE_THRESHOLD = 0.05
# Geräuschschwelle für den Noise Filter

# Einstellungen
if len(sys.argv) > 1 and sys.argv[1] == "--devices":
    print(sd.query_devices())
    sys.exit()

pi = pyaudio.PyAudio()

COOLDOWN = 2

# Automatische Erkennung der Sample Rate vom Gerät
SAMPLE_RATE = int(sd.query_devices(device=INPUT_DEVICE)['default_samplerate'])

frames = 2048
channels = 1
sw = pi.get_sample_size(pyaudio.paInt16)

checkingSignal = False
detectionCooldown = False

streaminput = pi.open(
    format=pyaudio.paInt16,
    rate=SAMPLE_RATE,
    channels=channels,
    input=True,
    frames_per_buffer=frames,
    input_device_index=INPUT_DEVICE
)

init(autoreset=True)

print(Fore.RED + "Alarmerkennung" + Fore.GREEN + " aktiviert...\n" + Fore.WHITE + "Toleranz: " + Fore.YELLOW + str(TOLERANCE) + "hz\n" + Fore.WHITE +
      "Aufnahmegerät: " + Fore.YELLOW + sd.query_devices(device=INPUT_DEVICE)["name"] + "\n")


window = numpy.blackman(frames)
train = []
tonenone = 0

reffreq = {
    '1': 1060,
    '2': 1160,
    '3': 1270,
    '4': 1400,
    '5': 1530,
    '6': 1670,
    '7': 1830,
    '8': 2000,
    '9': 2200,
    '0': 2400,
    'R': 2600
}

def numdec(x):
    return int('{0:g}'.format(x))

def checkfreq(freq, reffreq):
    global TOLERANCE
    for rtone, rfreq in list(reffreq.items()):
        if abs(rfreq - freq) <= TOLERANCE:
            return rtone

def cleantrain(train):
    lasttone = None
    newtrain = []

    for tone in train:
        if tone != lasttone:
            newtrain.append(tone if tone != "R" else lasttone)
        lasttone = tone

    if len(newtrain) == 5:
        printtrain(newtrain)

alarmTone = None
lastTone = None
toneConfirmed = False

def changeCheckingSignal(value):
    global checkingSignal

    if value is True:
        checkingSignal = True
    else:
        checkingSignal = False
        for property in signale:
            signale[property][0] = 0

def handleAlarm(tone, typ):
    print("\033[1A" + Fore.GREEN + tone + Fore.WHITE + " -> " + signale[typ][1] + typ)


def cooldown(value):
    global COOLDOWN
    global detectionCooldown

    detectionCooldown = value

    if value is True:
        threading.Timer(COOLDOWN, cooldown, args=(False,)).start()

def printtrain(newtrain):
    global lastTone
    global toneCount
    global clearAlarmT
    global checkingSignal
    global alarmTone
    global toneConfirmed

    if newtrain[0] is not None:
        tone = "".join(newtrain)

    if newtrain[0] is not None:
        if not toneConfirmed:
            print(Fore.GREEN + tone + Fore.WHITE + "?")
            toneConfirmed = True
        else:
            print("\033[1A" + Fore.GREEN + tone + Fore.RED + "!")
            toneConfirmed = False

    if newtrain[0] is not None and detectionCooldown is False:
        cooldown(True)
        alarmTone = tone
        threading.Timer(0.6, changeCheckingSignal, args=(True,)).start()
        lastTone = None

signale = {
    "Feueralarm": [0, Fore.RED],
    "Stiller Alarm": [0, Fore.WHITE],
    "Probealarm": [0, Fore.BLUE],
    "Zivilschutzalarm": [0, Fore.MAGENTA],
    "Zivilschutzwarnung": [0, Fore.YELLOW],
    "Zivilschutzentwarnung": [0, Fore.GREEN]
}

def detectSignal(frequency):
    global signale
    global alarmTone

    timespersecond = SAMPLE_RATE / frames * 2

    if abs(1240 - frequency) <= TOLERANCE:
        signale["Feueralarm"][0] += 1
    if abs(2600 - frequency) <= TOLERANCE:
        signale["Stiller Alarm"][0] += 1
    if abs(1860 - frequency) <= TOLERANCE:
        signale["Probealarm"][0] += 1
    if abs(825 - frequency) <= TOLERANCE:
        signale["Zivilschutzalarm"][0] += 1
    if abs(2280 - frequency) <= TOLERANCE:
        signale["Zivilschutzwarnung"][0] += 1
    if abs(1010 - frequency) <= TOLERANCE:
        signale["Zivilschutzentwarnung"][0] += 1

    for property in signale:
        value = signale[property][0]
        if value > timespersecond * 1.2:
            changeCheckingSignal(False)
            handleAlarm(alarmTone, property)

def applyNoiseFilter(indata):
    global NOISE_THRESHOLD

    rms = numpy.sqrt(numpy.mean(numpy.maximum(indata ** 2, 0)))
    if rms < NOISE_THRESHOLD:
        indata = numpy.zeros_like(indata)

    return indata

data = streaminput.read(frames)

while len(data) == frames * sw:
    indata = numpy.frombuffer(data, dtype=numpy.int16)
    indata = applyNoiseFilter(indata)

    fftData = abs(numpy.fft.rfft(indata)) ** 5
    which = fftData[1:].argmax() + 1

    freq = which * SAMPLE_RATE / frames

    if not numpy.isnan(freq):
        freq = round(freq)

        if checkingSignal:
            detectSignal(freq)

        gain = max(indata) / 32767.0
        fftData *= gain

        tone = checkfreq(freq, reffreq)
        if tone:
            train.append(tone)
            tone = None
        elif train and tone is None and tonenone == 1:
            cleantrain(train)
            train = []
            tonenone = 0
        elif train and tone is None and tonenone == 0:
            tonenone = 1
        elif train and tone is None and tonenone == 1:
            tonenone = 2
        elif train and tone is None and tonenone == 2:
            tonenone = 3
        elif train and tone is None and tonenone == 3:
            tonenone = 4
        elif train and tone is None and tonenone == 4:
            tonenone = 5
        elif train and tone is None and tonenone == 5:
            tonenone = 6

    data = streaminput.read(frames)

if train:
    cleantrain(train)
