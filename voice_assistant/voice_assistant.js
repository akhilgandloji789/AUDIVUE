/**
 * AUDIVUE Voice Assistant Module
 * Real-time Speech-to-Text (STT) & Text-to-Speech (TTS) Engine
 * Designed for visually impaired assistance with top-rated female voice selection,
 * priority queueing, safety interrupts, and hands-free voice command recognition.
 */

class AudivueVoiceAssistant {
    constructor(options = {}) {
        // Configuration settings
        this.speechRate = options.rate || 1.05;   // Slightly crisp reading speed
        this.speechPitch = options.pitch || 1.0;  // Natural warm pitch
        this.speechVolume = options.volume || 1.0;
        this.activeMode = options.defaultMode || 'obstacle'; // 'obstacle' or 'currency'
        
        // State management
        this.isMuted = false;
        this.isListening = false;
        this.lastSpokenText = '';
        this.selectedVoice = null;
        this.availableVoices = [];
        this.speechQueue = [];
        this.isSpeaking = false;
        
        // Callback handlers
        this.onCommandRecognized = options.onCommandRecognized || null;
        this.onModeChange = options.onModeChange || null;
        this.onStatusUpdate = options.onStatusUpdate || null;
        this.onSpeechStart = options.onSpeechStart || null;
        this.onSpeechEnd = options.onSpeechEnd || null;

        // Initialize Speech Synthesis (TTS)
        this.initTTS();

        // Initialize Speech Recognition (STT)
        this.initSTT();
    }

    /**
     * ==========================================
     * 1. TEXT-TO-SPEECH (TTS) ENGINE & VOICE PICKER
     * ==========================================
     */
    initTTS() {
        if (!('speechSynthesis' in window)) {
            console.warn('AUDIVUE Voice Assistant: Web Speech Synthesis API is not supported in this browser.');
            return;
        }

        this.synth = window.speechSynthesis;

        // Populate voices (handles async loading in Chrome/Edge)
        this.loadVoices();
        if (this.synth.onvoiceschanged !== undefined) {
            this.synth.onvoiceschanged = () => this.loadVoices();
        }
    }

    /**
     * Loads available browser voices and selects the top-rated natural female English voice
     */
    loadVoices() {
        if (!this.synth) return;
        this.availableVoices = this.synth.getVoices();

        if (this.availableVoices.length === 0) return;

        // Preferred female voice keywords ordered by popularity and quality
        const femaleVoicePriorities = [
            'Google US English',          // Top rated Google Female Voice
            'Google UK English Female',   // Google UK Female
            'Google India English',       // Google India Female
            'Microsoft Jenny Online (Natural)', // MS Natural Jenny
            'Microsoft Aria Online (Natural)',  // MS Natural Aria
            'Microsoft Zira',             // Standard MS Female Voice
            'Samantha',                   // Top rated Apple iOS/macOS Female Voice
            'Karen',                      // Apple Australian Female
            'Victoria',                   // Apple Female
            'Fiona',                      // Apple Scottish Female
            'Zira',
            'Jenny',
            'Aria',
            'Emma'
        ];

        // 1. Search by explicit priority list
        for (const preferredName of femaleVoicePriorities) {
            const foundVoice = this.availableVoices.find(v => 
                v.name.toLowerCase().includes(preferredName.toLowerCase()) && 
                v.lang.startsWith('en')
            );
            if (foundVoice) {
                this.selectedVoice = foundVoice;
                break;
            }
        }

        // 2. Heuristic search for female english voices
        if (!this.selectedVoice) {
            this.selectedVoice = this.availableVoices.find(v => 
                v.lang.startsWith('en') && 
                (v.name.toLowerCase().includes('female') || v.name.toLowerCase().includes('woman'))
            );
        }

        // 3. Fallback to any English voice
        if (!this.selectedVoice) {
            this.selectedVoice = this.availableVoices.find(v => v.lang.startsWith('en')) || this.availableVoices[0];
        }

        this.notifyStatus(`Voice loaded: ${this.selectedVoice.name} (${this.selectedVoice.lang})`);
    }

    /**
     * Sets a specific voice by name
     */
    setVoiceByName(voiceName) {
        const found = this.availableVoices.find(v => v.name === voiceName);
        if (found) {
            this.selectedVoice = found;
            this.notifyStatus(`Voice changed to: ${found.name}`);
            return true;
        }
        return false;
    }

    /**
     * Speaks text using Web Speech Synthesis
     * Supports priority levels: 'normal', 'high', 'interrupt'
     */
    speak(text, priority = 'normal') {
        if (!this.synth || this.isMuted || !text) return;

        // If priority is 'interrupt' or 'high', stop current speech immediately
        if (priority === 'interrupt' || priority === 'high') {
            this.synth.cancel(); // Stop active speech immediately
            this.speechQueue = [];
        }

        this.lastSpokenText = text;
        const utterance = new SpeechSynthesisUtterance(text);

        if (this.selectedVoice) {
            utterance.voice = this.selectedVoice;
        }

        utterance.rate = this.speechRate;
        utterance.pitch = this.speechPitch;
        utterance.volume = this.speechVolume;

        utterance.onstart = () => {
            this.isSpeaking = true;
            if (this.recognition && this.isListening) {
                try { this.recognition.stop(); } catch(e){}
            }
            if (this.onSpeechStart) this.onSpeechStart(text);
        };

        utterance.onend = () => {
            this.isSpeaking = false;
            if (this.onSpeechEnd) this.onSpeechEnd(text);
            if (this.shouldListen && this.recognition) {
                setTimeout(() => {
                    try { this.recognition.start(); } catch(e){}
                }, 400);
            }
            this.processQueue();
        };

        utterance.onerror = (err) => {
            console.error('AUDIVUE TTS Error:', err);
            this.isSpeaking = false;
            if (this.shouldListen && this.recognition) {
                setTimeout(() => {
                    try { this.recognition.start(); } catch(e){}
                }, 400);
            }
            this.processQueue();
        };

        if (priority === 'interrupt' || priority === 'high') {
            this.synth.speak(utterance);
        } else {
            this.speechQueue.push(utterance);
            if (!this.isSpeaking) {
                this.processQueue();
            }
        }
    }

    processQueue() {
        if (this.speechQueue.length > 0 && !this.synth.speaking) {
            const nextUtterance = this.speechQueue.shift();
            this.synth.speak(nextUtterance);
        }
    }

    /**
     * Instantly stops any active speech
     */
    stopSpeech() {
        if (this.synth) {
            this.synth.cancel();
            this.speechQueue = [];
            this.isSpeaking = false;
            this.notifyStatus('Speech muted/stopped.');
        }
    }

    /**
     * Mutes or unmutes speech output
     */
    toggleMute() {
        this.isMuted = !this.isMuted;
        if (this.isMuted) {
            this.stopSpeech();
            this.notifyStatus('Voice Assistant Muted');
        } else {
            this.notifyStatus('Voice Assistant Unmuted');
            this.speak('Voice output enabled.', 'high');
        }
        return this.isMuted;
    }

    /**
     * Repeats the last spoken alert
     */
    repeatLast() {
        if (this.lastSpokenText) {
            this.speak(this.lastSpokenText, 'high');
        } else {
            this.speak('No previous alert to repeat.', 'normal');
        }
    }

    /**
     * Formats and speaks an Obstacle Detection Alert
     */
    speakObstacleAlert(objectName, position = 'center', distance = 'medium', isCritical = false) {
        const text = isCritical 
            ? `Warning! ${objectName} directly ahead, ${distance}!`
            : `${objectName} detected, ${position}, ${distance}.`;
            
        const priority = isCritical ? 'interrupt' : 'normal';
        this.speak(text, priority);
    }

    /**
     * Formats and speaks a Currency Detection & Summation Alert
     */
    speakCurrencyAlert(notesArray = [], totalSum = 0) {
        if (!notesArray || notesArray.length === 0) {
            this.speak('No currency notes detected in frame.', 'high');
            return;
        }

        const noteCounts = {};
        notesArray.forEach(note => {
            noteCounts[note] = (noteCounts[note] || 0) + 1;
        });

        const breakdownParts = Object.entries(noteCounts).map(([denom, count]) => {
            return count > 1 ? `${count} notes of ${denom} rupees` : `one ${denom} rupees note`;
        });

        const breakdownText = breakdownParts.join(', ');
        const text = `Currency detected: ${breakdownText}. Total sum is ${totalSum} rupees.`;
        
        this.speak(text, 'high');
    }


    /**
     * ==========================================
     * 2. SPEECH RECOGNITION (STT) VOICE COMMANDS
     * ==========================================
     */
    initSTT() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

        if (!SpeechRecognition) {
            console.warn('AUDIVUE Voice Assistant: Web Speech Recognition API is not supported in this browser.');
            return;
        }

        this.recognition = new SpeechRecognition();
        this.recognition.continuous = true;
        this.recognition.interimResults = false;
        this.recognition.lang = 'en-US';

        this.recognition.onstart = () => {
            this.isListening = true;
            this.notifyStatus('Listening for voice commands...');
        };

        this.recognition.onresult = (event) => {
            const lastResultIndex = event.results.length - 1;
            const transcript = event.results[lastResultIndex][0].transcript.trim().toLowerCase();
            this.handleVoiceCommand(transcript);
        };

        this.recognition.onerror = (event) => {
            console.warn('AUDIVUE STT Error:', event.error);
            if (event.error === 'not-allowed') {
                this.notifyStatus('Microphone permission denied.');
            }
        };

        this.recognition.onend = () => {
            this.isListening = false;
            // Auto-restart recognition if it stopped unexpectedly
            if (this.shouldListen) {
                try {
                    this.recognition.start();
                } catch (e) {
                    // Ignore restart collision
                }
            }
        };
    }

    /**
     * Starts listening for voice commands
     */
    startListening() {
        if (!this.recognition) {
            this.speak('Speech recognition is not supported in this browser.', 'high');
            return;
        }

        this.shouldListen = true;
        try {
            this.recognition.start();
            this.speak('Voice commands activated. Say obstacle mode or currency mode.', 'high');
        } catch (e) {
            console.log('STT already running');
        }
    }

    /**
     * Stops listening for voice commands
     */
    stopListening() {
        this.shouldListen = false;
        if (this.recognition) {
            this.recognition.stop();
            this.isListening = false;
            this.notifyStatus('Voice recognition stopped.');
        }
    }

    /**
     * Parses and executes recognized voice commands
     */
    handleVoiceCommand(commandText) {
        console.log('Recognized Voice Command:', commandText);

        const now = Date.now();
        if (this.lastCommandText === commandText && (now - (this.lastCommandTime || 0)) < 4000) {
            return;
        }
        this.lastCommandText = commandText;
        this.lastCommandTime = now;

        if (this.onCommandRecognized) {
            this.onCommandRecognized(commandText);
        }

        // 1. Obstacle Mode Command
        if (commandText.includes('obstacle') || commandText.includes('walk mode') || commandText.includes('walk')) {
            this.setMode('obstacle');
        }
        // 2. Currency Mode Command
        else if (commandText.includes('currency') || commandText.includes('money') || commandText.includes('count')) {
            this.setMode('currency');
        }
        // 3. Repeat Last Command
        else if (commandText.includes('repeat') || commandText.includes('say again')) {
            this.repeatLast();
        }
        // 4. Mute / Stop Speech
        else if (commandText.includes('stop') || commandText.includes('mute') || commandText.includes('quiet')) {
            this.stopSpeech();
            this.speak('Audio stopped.', 'interrupt');
        }
        // 5. Status Command
        else if (commandText.includes('status') || commandText.includes('mode')) {
            this.speakStatus();
        }
        // 6. Help Command
        else if (commandText.includes('help') || commandText.includes('commands')) {
            this.speak('Available commands: obstacle mode, currency mode, repeat, status, and stop.', 'high');
        }
    }

    /**
     * Switch Active Pipeline Mode
     */
    setMode(mode) {
        if (mode !== 'obstacle' && mode !== 'currency') return;
        if (this.activeMode === mode) return; // Do not re-announce if already in this mode!

        this.activeMode = mode;
        const modeName = mode === 'obstacle' ? 'Obstacle Detection Mode' : 'Currency Detection & Counting Mode';

        this.notifyStatus(`Mode switched to: ${modeName}`);
        this.speak(`${modeName} activated.`, 'interrupt');

        if (this.onModeChange) {
            this.onModeChange(mode);
        }
    }

    /**
     * Speaks current assistant status
     */
    speakStatus() {
        const modeName = this.activeMode === 'obstacle' ? 'Obstacle Detection' : 'Currency Counting';
        const voiceName = this.selectedVoice ? this.selectedVoice.name : 'Default voice';
        this.speak(`System ready. Current active mode is ${modeName}. Using voice ${voiceName}.`, 'high');
    }

    notifyStatus(msg) {
        console.log(`[AUDIVUE Voice Assistant] ${msg}`);
        if (this.onStatusUpdate) {
            this.onStatusUpdate(msg);
        }
    }
}

// Export for module systems or window global
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AudivueVoiceAssistant;
} else {
    window.AudivueVoiceAssistant = AudivueVoiceAssistant;
}
