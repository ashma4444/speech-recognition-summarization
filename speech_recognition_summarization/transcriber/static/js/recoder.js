// Collect DOM elements
const displayElement = document.querySelector(".display");
const controlsContainer = document.querySelector(".controllers");

const AppStates = ["Initial", "Recording", "ReadyToDownload"];
let currentState = 0;
let audioRecorder,
	audioChunks = [],
	recordedAudioURL = "";

// Setup audioRecorder for audio recording
if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
	navigator.mediaDevices
		.getUserMedia({ audio: true })
		.then((stream) => {
			audioRecorder = new MediaRecorder(stream);

			audioRecorder.ondataavailable = (event) => {
				audioChunks.push(event.data);
			};

			audioRecorder.onstop = () => {
				const audioBlob = new Blob(audioChunks, {
					type: "audio/ogg; codecs=opus",
				});
				audioChunks = [];
				recordedAudioURL = window.URL.createObjectURL(audioBlob);
				document.querySelector("audio").src = recordedAudioURL;
			};
		})
		.catch((error) => {
			console.error("An error occurred: ", error);
		});
} else {
	currentState = "";
	runApplication(currentState);
}

const resetDisplay = () => {
	displayElement.textContent = "";
};

const resetControls = () => {
	controlsContainer.textContent = "";
};

const startRecording = () => {
	currentState = 1;
	audioRecorder.start();
	runApplication(currentState);
};

const stopRecording = () => {
	currentState = 2;
	audioRecorder.stop();
	runApplication(currentState);
};

const saveAudio = () => {
	const downloadAnchor = document.createElement("a");
	downloadAnchor.href = recordedAudioURL;
	downloadAnchor.setAttribute("download", "audio_recording");
	downloadAnchor.click();
};

const createButton = (id, onClickFunction, buttonText) => {
	const button = document.createElement("button");
	button.id = id;
	button.setAttribute("onclick", onClickFunction);
	button.textContent = buttonText;
	controlsContainer.append(button);
};

const displayMessage = (messageText) => {
	const message = document.createElement("p");
	message.textContent = messageText;
	displayElement.append(message);
};

const embedAudioPlayer = () => {
	const audioElement = document.createElement("audio");
	audioElement.controls = true;
	audioElement.src = recordedAudioURL;
	displayElement.append(audioElement);
};

const runApplication = (stateIndex) => {
	switch (AppStates[stateIndex]) {
		case "Initial":
			resetDisplay();
			resetControls();

			createButton("startRecording", "startRecording()", "Start Recording");
			break;

		case "Recording":
			resetDisplay();
			resetControls();

			displayMessage("Recording in progress...");
			createButton("stopRecording", "stopRecording()", "Stop Recording");
			break;

		case "ReadyToDownload":
			resetDisplay();
			resetControls();

			embedAudioPlayer();
			createButton("startRecording", "startRecording()", "Record Again");
			createButton("downloadAudio", "saveAudio()", "Download Recording");
			break;

		default:
			resetDisplay();
			resetControls();

			displayMessage("Your browser does not support audio recording.");
			break;
	}
};

runApplication(currentState);
