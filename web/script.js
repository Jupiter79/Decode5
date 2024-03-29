// SETTINGS
const TOLERANCE_DIGITS = 20;
const TOLERANCE_SIGNALS = 50;
const SIGNAL_TONE_REQUIRED_SECONDS = 2;

const TONES = {
    1: 1060,
    2: 1160,
    3: 1270,
    4: 1400,
    5: 1530,
    6: 1670,
    7: 1830,
    8: 2000,
    9: 2200,
    0: 2400,
    'R': 2600
}

const SIGNALS = {
    "Feueralarm": [1240, 0, "red"],
    "Probealarm": [1860, 0, "cyan"],
    "Zivilschutzalarm": [825, 0, "magenta"],
    "Zivilschutzwarnung": [2280, 0, "yellow"],
    "Zivilschutzentwarnung": [1010, 0, "lime"],
    "Stiller Alarm": [2600, 0, "orange"]
}

$(document).ready(() => addDisplayingElements());

let frames = 2048;

// Request access to the microphone
let lastTone, cycleDuration;
let tone_List = [];
let detectSignal = false;
let lastToneDetected;

let count = 0;
navigator.mediaDevices.getUserMedia({ audio: true })
    .then(function (stream) {
        // Create an audio context
        var audioContext = new (window.AudioContext || window.webkitAudioContext)();

        cycleDuration = 1 / audioContext.sampleRate * frames;

        // Create an audio source from the microphone stream
        var source = audioContext.createMediaStreamSource(stream);

        // Create an analyser node
        var analyser = audioContext.createAnalyser();
        analyser.fftSize = frames;

        // Connect the source to the analyser
        source.connect(analyser);

        // Get the frequency data
        var frequencyData = new Uint8Array(analyser.frequencyBinCount);

        // Function to update the frequency display
        function updateFrequency() {
            analyser.getByteFrequencyData(frequencyData);

            // Calculate the dominant frequency
            var maxIndex = 0;
            for (var i = 0; i < frequencyData.length; i++) {
                if (frequencyData[i] > frequencyData[maxIndex]) {
                    maxIndex = i;
                }
            }

            // Convert index to frequency
            var frequency = maxIndex * (audioContext.sampleRate / analyser.fftSize);

            // Display the frequency
            document.getElementById('frequencyDisplay').innerText = 'Frequenz: ' + frequency.toFixed(2) + ' Hz';


            Object.entries(SIGNALS).forEach(x => {
                let signalFrequency = SIGNALS[x[0]][0];

                if (frequency - TOLERANCE_SIGNALS <= signalFrequency && frequency + TOLERANCE_SIGNALS >= signalFrequency) {
                    if (detectSignal) SIGNALS[x[0]][1]++;

                    colorType(x[0], false);
                }

                if (detectSignal && SIGNALS[x[0]][1] >= SIGNAL_TONE_REQUIRED_SECONDS * 2 / cycleDuration) {
                    console.log(`SIGNAL: ${x[0]}`);

                    count++;

                    $("#alarmList #list").append(`
                    <tr>
                    <th scope="row">${count}</th>
                    <td>${lastToneDetected}</td>
                    <td>${x[0]}</td>
                    </tr>`)

                    resetSignalDetection();
                }
            })



            Object.entries(TONES).forEach(x => {
                if (frequency - TOLERANCE_DIGITS <= x[1] && frequency + TOLERANCE_DIGITS >= x[1]) {
                    if (x[0] != lastTone) {
                        tone_List.push(x[0] != "R" ? x[0] : tone_List[tone_List.length - 1]);

                        if (tone_List.length == 5) {
                            alarm();
                            colorType(x[0], true);

                            tone_List = [];

                            return;
                        }

                        colorType(x[0], true);

                        let oldLength = tone_List.length;
                        setTimeout(() => {
                            if (tone_List.length == oldLength) {
                                tone_List = [];
                            }
                        }, 70 * 2)

                        lastTone = x[0];
                    }
                }
            })


            // Call the updateFrequency function recursively
            requestAnimationFrame(updateFrequency);
        }

        // Start updating the frequency display
        updateFrequency();
    })
    .catch(function (err) {
        console.error('Error accessing microphone: ', err);
    });

function alarm() {
    console.log(`ALARM: ${tone_List.join("")}`);
    lastToneDetected = tone_List.join("");

    detectSignal = true;

    colorType(null, null, true);

    setTimeout(() => resetSignalDetection(), 5000);
}

function resetSignalDetection() {
    detectSignal = false;

    Object.entries(SIGNALS).forEach(x => {
        SIGNALS[x[0]][1] = 0;
    })
}

function addDisplayingElements() {
    Object.entries(TONES).forEach(x => {
        $("#tones>.digits").append(`<div class="col" data-type="${x[0]}">${x[0]}</div>`);
    });

    Object.entries(SIGNALS).forEach(x => {
        $("#tones>.signals").append(`<div class="col" data-type="${x[0]}">${x[0]}</div>`);
    });
}

alreadyAppended = false
function colorType(type, isDigit, alert = false) {
    if (alert) {
        Object.entries(TONES).forEach(x => {
            $(`#tones [data-type="${x[0]}"]`).addClass("active");
            $("#tones .digits").hide();
        });

        if (!alreadyAppended) {
            tone_List.forEach(x => {
                $("#tones>.digits_result").append(`<div class="col active">${x}</div>`);
            })

            alreadyAppended = true;
        }

        setTimeout(() => {
            Object.entries(TONES).forEach(x => {
                $(`#tones [data-type="${x[0]}"]`).removeClass("active");
            });

            $("#tones .digits").show();
            $("#tones>.digits_result").empty();

            alreadyAppended = false;
        }, 1000 * 5)

        return;
    }
    9
    let element = $(`#tones [data-type="${type}"]`);

    if (!detectSignal || (detectSignal && !isDigit)) {
        if (isDigit) element.addClass("active");
        else element.css("background-color", SIGNALS[type][2]);

        setTimeout(() => {
            if (!detectSignal || !isDigit) {
                if (isDigit) element.removeClass("active");
                else element.css("background-color", "unset");
            }
        }, isDigit ? 60 : 1);
    }
}