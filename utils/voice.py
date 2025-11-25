# utils/voice.py
from streamlit.components.v1 import html

def voice_input_with_waveform():
    """
    Chrome-only Web Speech + Web Audio API.
    - Animated waveform
    - Synthetic F1 radio beeps
    - Injects text into the textarea whose placeholder includes 'Ask Gazoo AI'
    """
    js_code = """
    <script>
    function supportsSpeech() {
        return ("webkitSpeechRecognition" in window || "SpeechRecognition" in window);
    }

    let recognizing = false;
    let recognition = null;
    let audioContext = null;
    let analyser = null;
    let micSource = null;
    let animationId = null;
    let finalTranscript = "";

    function playRadioStart() {
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = "sine";
        osc.frequency.setValueAtTime(1200, ctx.currentTime);
        gain.gain.setValueAtTime(0, ctx.currentTime);
        gain.gain.linearRampToValueAtTime(0.4, ctx.currentTime + 0.01);
        gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.18);
        osc.connect(gain); gain.connect(ctx.destination);
        osc.start(); osc.stop(ctx.currentTime + 0.2);
    }

    function playRadioEnd() {
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = "sawtooth";
        osc.frequency.setValueAtTime(1200, ctx.currentTime);
        osc.frequency.linearRampToValueAtTime(400, ctx.currentTime + 0.25);
        gain.gain.setValueAtTime(0.4, ctx.currentTime);
        gain.gain.linearRampToValueAtTime(0.0, ctx.currentTime + 0.25);
        osc.connect(gain); gain.connect(ctx.destination);
        osc.start(); osc.stop(ctx.currentTime + 0.28);
    }

    function getTargetTextarea() {
        const all = [...window.parent.document.querySelectorAll("textarea")];
        return all.find(t => (t.placeholder || "").includes("Ask Gazoo AI"));
    }

    function setupWaveform() {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        analyser = audioContext.createAnalyser();
        analyser.fftSize = 64;

        navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
            micSource = audioContext.createMediaStreamSource(stream);
            micSource.connect(analyser);
            drawWaveform();
        });
    }

    function drawWaveform() {
        const canvas = document.getElementById("waveformCanvas");
        const ctx = canvas.getContext("2d");
        const bufferLength = analyser.frequencyBinCount;
        const data = new Uint8Array(bufferLength);

        function draw() {
            animationId = requestAnimationFrame(draw);
            analyser.getByteFrequencyData(data);

            ctx.fillStyle = "#000";
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            let barWidth = canvas.width / bufferLength;
            let x = 0;
            for (let i = 0; i < bufferLength; i++) {
                let h = data[i];
                ctx.fillStyle = `rgb(${h+50},40,40)`;
                ctx.fillRect(x, canvas.height - h/2, barWidth, h/2);
                x += barWidth + 1;
            }
        }
        draw();
    }

    function startVoice() {
        if (recognizing) return;
        const statusEl = document.getElementById("voice-status");

        if (!supportsSpeech()) {
            if (statusEl) statusEl.innerHTML = "Not supported. Use Chrome.";
            return;
        }

        playRadioStart();

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = "en-US";

        recognizing = true;
        if (statusEl) statusEl.innerHTML = "Listening…";

        setupWaveform();
        recognition.start();

        recognition.onresult = function(evt) {
            let interim = "";
            for (let i = evt.resultIndex; i < evt.results.length; ++i) {
                if (evt.results[i].isFinal) {
                    finalTranscript += evt.results[i][0].transcript + " ";
                } else {
                    interim += evt.results[i][0].transcript;
                }
            }
            const field = getTargetTextarea();
            if (field) {
                field.value = (finalTranscript + " " + interim).trim();
                field.dispatchEvent(new Event("input", { bubbles: true }));
            }
        };

        recognition.onerror = e => console.log("Speech error:", e);
        recognition.onend = () => stopVoice();
    }

    function stopVoice() {
        const statusEl = document.getElementById("voice-status");
        if (!recognizing) return;
        recognizing = false;

        playRadioEnd();
        if (recognition) recognition.stop();
        if (animationId) cancelAnimationFrame(animationId);
        if (statusEl) statusEl.innerHTML = "Stopped";
    }
    </script>

    <div>
      <button onclick="startVoice()" style="padding:8px 16px;border-radius:10px;background:#f44336;color:white;border:none;font-weight:700;cursor:pointer;">
        Start Voice
      </button>
      <button onclick="stopVoice()" style="padding:8px 16px;border-radius:10px;background:#444;color:white;border:none;font-weight:700;cursor:pointer;margin-left:10px;">
        Stop
      </button>

      <div id="voice-status" style="margin-top:8px;color:#f44336;font-weight:bold;">
        (idle)
      </div>

      <canvas id="waveformCanvas" width="500" height="80"
              style="margin-top:10px;background:#000;border-radius:8px;"></canvas>
    </div>
    """

    html(js_code, height=220)
