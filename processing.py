import os
import tempfile
import whisper
from pyannote.audio import Pipeline
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
from pydub import AudioSegment

class MeetingPipeline:
    def __init__(self):
        # We assume the user has set the HF_TOKEN environment variable.
        self.hf_token = os.environ.get("HF_TOKEN")
        
        print("Loading Whisper model...")
        # Loading medium model for better accuracy. 
        self.whisper_model = whisper.load_model("medium")
        
        print("Loading Pyannote Diarization pipeline...")
        try:
            self.diarization_pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                token=self.hf_token
            )
            # Use GPU if available
            if torch.cuda.is_available() and self.diarization_pipeline:
                self.diarization_pipeline.to(torch.device("cuda"))
        except Exception as e:
            print(f"Warning: Could not load diarization pipeline. Make sure HF_TOKEN is set. Error: {e}")
            self.diarization_pipeline = None

        print("Loading Summarization model...")
        self.tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")
        self.summary_model = AutoModelForSeq2SeqLM.from_pretrained("facebook/bart-large-cnn")

    def preprocess_audio(self, file_path):
        """Convert audio to standard format required by models."""
        audio = AudioSegment.from_file(file_path)
        # Convert to mono and 16kHz
        audio = audio.set_channels(1).set_frame_rate(16000)
        temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        audio.export(temp_wav.name, format="wav")
        return temp_wav.name

    def transcribe_with_whisper(self, audio_path):
        """Transcribe audio using Whisper."""
        result = self.whisper_model.transcribe(audio_path, word_timestamps=True)
        return result

    def diarize_audio(self, audio_path):
        """Perform speaker diarization."""
        if not self.diarization_pipeline:
            print("Warning: Diarization pipeline is not loaded (likely missing HF_TOKEN). Falling back to dummy single-speaker diarization.")
            audio = AudioSegment.from_file(audio_path)
            duration = len(audio) / 1000.0
            return [{"start": 0.0, "end": duration, "speaker": "SPEAKER_00"}]
            
        diarization = self.diarization_pipeline(audio_path)
        
        speakers = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            speakers.append({
                "start": turn.start,
                "end": turn.end,
                "speaker": speaker
            })
        return speakers

    def align_transcription_and_diarization(self, transcription, diarization):
        """Align whisper segments with diarization segments."""
        aligned_segments = []
        for seg in transcription['segments']:
            segment_start = seg['start']
            segment_end = seg['end']
            
            # Find the most overlapping speaker
            best_speaker = "Unknown"
            max_overlap = 0
            
            for d in diarization:
                overlap = max(0, min(segment_end, d['end']) - max(segment_start, d['start']))
                if overlap > max_overlap:
                    max_overlap = overlap
                    best_speaker = d['speaker']
            
            aligned_segments.append({
                "start": segment_start,
                "end": segment_end,
                "speaker": best_speaker,
                "text": seg['text'].strip()
            })
        return aligned_segments

    def calculate_statistics(self, aligned_segments):
        """Calculate speaker statistics."""
        speaker_time = {}
        for seg in aligned_segments:
            duration = seg['end'] - seg['start']
            speaker = seg['speaker']
            speaker_time[speaker] = speaker_time.get(speaker, 0) + duration
            
        total_time = sum(speaker_time.values())
        stats = []
        for speaker, time in speaker_time.items():
            stats.append({
                "speaker": speaker,
                "total_time_seconds": round(time, 2),
                "percentage": round((time / total_time) * 100, 2) if total_time > 0 else 0
            })
        return stats

    def generate_summary(self, aligned_segments):
        """Generate summary using HuggingFace Transformers."""
        full_text = " ".join([f"{seg['speaker']}: {seg['text']}" for seg in aligned_segments])
        
        # Simple chunking if text is too long for BART (max 1024 tokens)
        max_chunk_length = 3000 # chars
        chunks = [full_text[i:i+max_chunk_length] for i in range(0, len(full_text), max_chunk_length)]
        
        summary = ""
        for chunk in chunks:
            if len(chunk) > 50: # Avoid summarizing very small leftover chunks
                inputs = self.tokenizer(chunk, max_length=1024, return_tensors="pt", truncation=True)
                summary_ids = self.summary_model.generate(
                    inputs["input_ids"], 
                    max_length=130, 
                    min_length=30, 
                    length_penalty=2.0, 
                    num_beams=4, 
                    early_stopping=True
                )
                summary += self.tokenizer.decode(summary_ids[0], skip_special_tokens=True) + " "
                
        return summary.strip()

    def process(self, audio_file_path):
        """Main processing function."""
        print(f"Preprocessing {audio_file_path}...")
        processed_path = self.preprocess_audio(audio_file_path)
        
        try:
            print("Transcribing with Whisper...")
            transcription = self.transcribe_with_whisper(processed_path)
            
            print("Diarizing with Pyannote...")
            diarization = self.diarize_audio(processed_path)
            
            print("Aligning segments...")
            aligned_segments = self.align_transcription_and_diarization(transcription, diarization)
            
            print("Calculating statistics...")
            stats = self.calculate_statistics(aligned_segments)
            
            print("Generating summary...")
            summary = self.generate_summary(aligned_segments)
            
            return {
                "language": transcription.get('language', 'unknown'),
                "segments": aligned_segments,
                "statistics": stats,
                "summary": summary
            }
        finally:
            if os.path.exists(processed_path):
                os.remove(processed_path)

# Singleton instance for easy import
# pipeline = MeetingPipeline()
