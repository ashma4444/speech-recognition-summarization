from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor, AutoModelForSeq2SeqLM, MBart50Tokenizer
import torch
import librosa
import os
import json

# Load model and processor
MODEL_PATH = "../model"
PREPROCESSOR_PATH = "../processor"
model = Wav2Vec2ForCTC.from_pretrained(MODEL_PATH)
processor = Wav2Vec2Processor.from_pretrained(PREPROCESSOR_PATH)

# Load the summarizer model and tokenizer locally
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
SUMMARIZER_MODEL_PATH = "../summarizer"  # Replace with your local model path
tokenizer = MBart50Tokenizer.from_pretrained("facebook/mbart-large-50", src_lang="ne_NP", tgt_lang="ne_NP")
summarizer_model = AutoModelForSeq2SeqLM.from_pretrained(SUMMARIZER_MODEL_PATH).to(device)

def transcribe_audio(request):
    if request.method == 'POST' and request.FILES.get('audio_file'):
        # Get the uploaded audio file
        audio_file = request.FILES['audio_file']
        
        # Save the uploaded file temporarily
        temp_path = f"temp_{audio_file.name}"
        with open(temp_path, 'wb') as f:
            f.write(audio_file.read())

        # Load and process the audio file
        audio, sr = librosa.load(temp_path, sr=16000)  # Ensure audio is resampled to 16 kHz
        input_values = processor(audio, return_tensors="pt", sampling_rate=16000).input_values

        # Perform transcription
        with torch.no_grad():
            logits = model(input_values).logits
            predicted_ids = torch.argmax(logits, dim=-1)
            transcription = processor.batch_decode(predicted_ids)[0]

        # Clean up the temporary audio file
        os.remove(temp_path)

        # Return the transcription as JSON
        return JsonResponse({'transcription': transcription})

    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def summarize_text(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            input_text = data.get("text", "")

            # Tokenize and summarize the input text
            inputs = tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True)
            inputs = {key: value.to(device) for key, value in inputs.items()}
            summary_ids = summarizer_model.generate(inputs["input_ids"], max_length=150, num_beams=5, early_stopping=True)
            summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)

            return JsonResponse({"summary": summary}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid request method"}, status=400)


def home(request):
    return render(request, 'index.html')
