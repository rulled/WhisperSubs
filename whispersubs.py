import os
import argparse
import subprocess
import concurrent.futures
import whisper
import time
import platform
from whisper.utils import WriteSRT
from tqdm import tqdm

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def clear_console():
    os.system('cls' if platform.system() == 'Windows' else 'clear')

def print_step(step, message):
    timestamp = time.strftime("%H:%M:%S")
    print(f"{Colors.OKGREEN}[{timestamp}][STEP {step}] {message}{Colors.ENDC}")

def print_progress(current, total, message):
    progress = current / total
    bar_length = 40
    filled = int(bar_length * progress)
    bar = '█' * filled + '-' * (bar_length - filled)
    print(f"\r{Colors.OKBLUE}[{time.strftime('%H:%M:%S')}][PROGRESS] {message} |{bar}| {progress:.1%}{Colors.ENDC}", end='')

def convert_to_mp3(input_file, output_audio):
    start_time = time.time()
    print_step(1, f"Starting audio conversion to MP3...")
    
    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_file,
        "-q:a", "0",
        "-map", "a",
        "-threads", "4",
        "-hide_banner",
        "-loglevel", "error",
        "-stats",
        output_audio
    ]
    
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )
    
    for line in process.stdout:
        if "time=" in line:
            time_str = line.split("time=")[1].split(" ")[0]
            print(f"\r{Colors.OKBLUE}[FFMPEG] Current processing time: {time_str}{Colors.ENDC}", end='')
    
    process.wait()
    duration = time.time() - start_time
    print_step(1, f"Audio conversion completed in {duration:.1f}s")

def generate_subtitles(audio_file, base_srt_path, model, langs):
    srt_files = []
    total_langs = len(langs)
    
    for idx, lang in enumerate(langs, 1):
        start_time = time.time()
        print_step(2, f"Generating {lang} subtitles ({idx}/{total_langs})...")
        
        srt_path = os.path.abspath(f"{base_srt_path}_{lang}.srt")
        output_dir = os.path.dirname(srt_path)
        os.makedirs(output_dir, exist_ok=True)
        
        result = model.transcribe(
            audio_file,
            language=lang,
            task="transcribe",
            verbose=False
        )
        
        writer = WriteSRT(output_dir=output_dir)
        writer(result, os.path.basename(srt_path).replace('.srt', ''))
        
        srt_files.append((srt_path, lang))
        
        duration = time.time() - start_time
        print_step(2, f"{lang.upper()} subtitles created in {duration:.1f}s")
    
    return srt_files

def convert_to_mkv(input_file, output_file, srt_files):
    start_time = time.time()
    print_step(3, "Muxing subtitles into MKV container...")
    
    cmd = [
        "ffmpeg",
        "-y",
        "-i", os.path.abspath(input_file)
    ]
    
    for srt, _ in srt_files:
        cmd.extend(["-i", os.path.abspath(srt)])
    
    cmd.extend(["-map", "0:v", "-map", "0:a"])
    
    for i in range(len(srt_files)):
        cmd.extend(["-map", f"{i+1}:0"])
    
    cmd.extend([
        "-c:v", "copy",
        "-c:a", "copy",
        "-c:s", "srt",
        "-disposition:s", "0",
        "-hide_banner",
        "-loglevel", "error",
        "-stats"
    ])
    
    for idx, (_, lang) in enumerate(srt_files):
        cmd.extend([f"-metadata:s:s:{idx}", f"language={lang}"])
    
    cmd.append(os.path.abspath(output_file))
    
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print(f"{Colors.FAIL}Error during muxing:{Colors.ENDC}")
        print("Command:", " ".join(cmd))
        print("Error output:", stderr)
        raise subprocess.CalledProcessError(process.returncode, cmd)
    
    duration = time.time() - start_time
    print_step(3, f"MKV container created in {duration:.1f}s")

def replace_original(input_file, output_file):
    try:
        os.remove(input_file)
        os.rename(output_file, input_file)
        print(f"{Colors.OKGREEN}Original file replaced successfully!{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}Error replacing file: {e}{Colors.ENDC}")
        raise

def main():
    clear_console()
    
    parser = argparse.ArgumentParser(description="Video processing with multi-language subtitles")
    parser.add_argument("input", help="Input video file")
    parser.add_argument("-o", "--output", help="Output video file (default: replace original)")
    parser.add_argument("-m", "--model", default="base", help="Whisper model name")
    parser.add_argument("-l", "--langs", default="en", help="Comma-separated language codes")
    parser.add_argument("-r", "--replace", action="store_true", help="Replace original file")
    args = parser.parse_args()
    args.langs = args.langs.split(',')

    temp_audio = "temp_audio.mp3"
    srt_files = []
    output_file = args.output or "temp_output.mkv"

    try:
        print_step(0, f"Starting processing for {args.input}")
        start_total = time.time()
        
        with tqdm(total=1, desc=f"{Colors.BOLD}Loading model{Colors.ENDC}", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}") as pbar:
            model = whisper.load_model(args.model)
            pbar.update(1)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            audio_future = executor.submit(convert_to_mp3, args.input, temp_audio)
            audio_future.result()
            
            srt_files = generate_subtitles(temp_audio, "temp_subs", model, args.langs)
            
            convert_to_mkv(args.input, output_file, srt_files)

        if args.replace or not args.output:
            replace_original(args.input, output_file)

        total_duration = time.time() - start_total
        print(f"\n{Colors.OKGREEN}Processing completed in {total_duration:.1f} seconds!{Colors.ENDC}")
        print(f"{Colors.BOLD}Final file: {args.input if args.replace else output_file}{Colors.ENDC}")

    finally:
        if os.path.exists(temp_audio):
            os.remove(temp_audio)
        for srt, _ in srt_files:
            if os.path.exists(srt):
                os.remove(srt)
        if os.path.exists("temp_output.mkv") and not args.replace:
            os.remove("temp_output.mkv")

if __name__ == "__main__":
    main()