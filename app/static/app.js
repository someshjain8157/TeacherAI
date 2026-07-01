const askButton = document.getElementById("askButton");
const questionBox = document.getElementById("question");

const loading = document.getElementById("loading");

const answerBox = document.getElementById("answerBox");
const answer = document.getElementById("answer");
const sources = document.getElementById("sources");

const subject = document.getElementById("subject");

const micButton = document.getElementById("micButton");

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();
recognition.lang = "en-IN";
recognition.continuous = false;
recognition.interimResults = false;

micButton.addEventListener("click", () => {
    recognition.start();
});

recognition.onresult = async (event) => {
    questionBox.value = event.results[0][0].transcript;
    await askQuestion();
};

loadSubjects();

askButton.addEventListener("click", askQuestion);

questionBox.addEventListener("keydown", function (event) {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        askQuestion();
    }
});

async function loadSubjects() {
    try {
        const response = await fetch("/subjects");
        const data = await response.json();
        data.subjects.forEach(item => {
            const option = document.createElement("option");
            option.value = item;
            option.textContent = item;
            subject.appendChild(option);
        });
    } catch (error) {
        console.error(error);
    }
}

function cleanAnswerText(text) {
    return text
        .replace(/^When work done equals zero in a Grade 9 physics class,?\s*/i, "")
        .trim();
}

const speechDelayMs = 3000;

function getPreferredVoice() {
    if (!window.speechSynthesis) {
        return null;
    }

    const voices = window.speechSynthesis.getVoices();
    if (!voices || voices.length === 0) {
        return null;
    }

    return (
        voices.find(v => v.lang && v.lang.toLowerCase().startsWith("en-in")) ||
        voices.find(v => v.lang && v.lang.toLowerCase().startsWith("en")) ||
        voices[0]
    );
}

function speakAnswer(text) {
    return new Promise((resolve) => {
        if (!window.speechSynthesis || !window.SpeechSynthesisUtterance) {
            resolve(false);
            return;
        }

        const startSpeaking = () => {
            const utterance = new SpeechSynthesisUtterance(text);
            const voice = getPreferredVoice();

            if (voice) {
                utterance.voice = voice;
                utterance.lang = voice.lang || "en-IN";
            } else {
                utterance.lang = "en-IN";
            }

            utterance.rate = 1;
            utterance.pitch = 1;
            utterance.volume = 1;

            utterance.onend = () => {
                resolve(true);
            };
            utterance.onerror = () => {
                resolve(false);
            };

            window.speechSynthesis.cancel();
            window.speechSynthesis.resume();
            window.speechSynthesis.speak(utterance);
        };

        const voices = window.speechSynthesis.getVoices();
        if (voices && voices.length > 0) {
            startSpeaking();
            return;
        }

        const onVoicesChanged = () => {
            startSpeaking();
        };

        window.speechSynthesis.addEventListener("voiceschanged", onVoicesChanged, { once: true });

        setTimeout(() => {
            const loadedVoices = window.speechSynthesis.getVoices();
            if (loadedVoices && loadedVoices.length > 0) {
                startSpeaking();
            } else {
                resolve(false);
            }
        }, 250);
    });
}

async function askQuestion() {
    const question = questionBox.value.trim();
    if (question === "") {
        alert("Please enter a question.");
        return;
    }

    loading.style.display = "block";
    answerBox.style.display = "none";
    askButton.disabled = true;

    try {
        const response = await fetch("/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                question: question,
                subject: subject.value
            })
        });

        if (!response.ok) {
            throw new Error(`Request failed with status ${response.status}`);
        }

        answer.innerText = "";
        sources.innerHTML = "";
        window.speechSynthesis.cancel();

        let fullText = "";

        const renderResponse = (text) => {
            const marker = "[SOURCES]";
            if (text.includes(marker)) {
                const [answerText, sourcesText] = text.split(marker);
                const cleanedAnswer = cleanAnswerText(answerText);
                answer.innerText = cleanedAnswer;

                try {
                    const parsedSources = JSON.parse(sourcesText);
                    parsedSources.forEach(source => {
                        const li = document.createElement("li");
                        li.textContent = `${source.subject} | ${source.chapter} | Page ${source.page}`;
                        sources.appendChild(li);
                    });
                } catch (e) {
                    console.error("Failed to parse sources:", e);
                }

                return cleanedAnswer;
            }

            const cleanedAnswer = cleanAnswerText(text);
            answer.innerText = cleanedAnswer;
            return cleanedAnswer;
        };

        if (!response.body || !response.body.getReader) {
            fullText = await response.text();
        } else {
            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                fullText += decoder.decode(value, { stream: true });
            }
        }

        const spokenText = renderResponse(fullText);
        answerBox.style.display = "block";
        await new Promise(resolve => requestAnimationFrame(resolve));

        if (spokenText) {
            await new Promise(resolve => setTimeout(resolve, speechDelayMs));
            await speakAnswer(spokenText);
        }
    } catch (error) {
        alert("Unable to contact Akanksh AI 1.0.");
        console.error(error);
    } finally {
        loading.style.display = "none";
        askButton.disabled = false;
    }
}
