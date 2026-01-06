from flask import Flask, request, jsonify, send_from_directory, render_template
import os
import subprocess

app = Flask(__name__)

FILE_PATH = r'C:\Users\sruth\Downloads'
UPLOAD_FOLDER = r'C:\Users\sruth\separated\mdx_extra_q'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def check_and_execute_if_missing(filename):
    file_directory = os.path.join(UPLOAD_FOLDER, filename)
    required_files = ['vocals.wav', 'other.wav', 'drums.wav', 'bass.wav']

    # Check if all required files exist in the directory
    if not all(os.path.exists(os.path.join(file_directory, f)) for f in required_files):
        # Run demucs to generate the required files
        song_path = os.path.join(FILE_PATH, filename + '.mp3')
        try:
            print(f"Running demucs command for {song_path}")
            result = subprocess.run(
                ['demucs', '-n', 'mdx_extra_q', song_path],
                capture_output=True, text=True, encoding='utf-8', errors='replace'
            )
            # Print the output of the command
            print(result.stdout)
            print(result.stderr)
        except UnicodeDecodeError as e:
            print(f"UnicodeDecodeError: {e}")
        
        # Define the output directory where Demucs saves the tracks
        output_dir_base = r'C:\Users\sruth\separated\mdx_extra_q'
        output_dir = os.path.join(output_dir_base, filename)

        # Check if the output directory exists
        if not os.path.exists(output_dir):
            print(f'Error: The output directory {output_dir} does not exist.')
            return False
        
        # Move the generated files to the correct directory
        for file in os.listdir(output_dir):
            if file in required_files:
                os.rename(os.path.join(output_dir, file), os.path.join(file_directory, file))
        
        # Check again if all required files now exist
        if not all(os.path.exists(os.path.join(file_directory, f)) for f in required_files):
            return False  # Indicate that files are still missing
    return True  # Indicate that all files exist

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/login', methods=['POST'])
def login():
    return render_template('music.html')

@app.route('/register', methods=['POST'])
def register():
    return render_template('home.html')

@app.route('/contact')
def contact():
    return render_template('Contactus.html')

@app.route('/music')
def music():
    return render_template('music.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and file.filename.endswith('.mp3'):
        filename_without_ext = os.path.splitext(file.filename)[0]
        file_path = os.path.join(UPLOAD_FOLDER, filename_without_ext)
        os.makedirs(file_path, exist_ok=True)
        file.save(os.path.join(file_path, file.filename))
        print('Uploaded file name:', file.filename)

        # Check if files are missing and handle if necessary
        if not check_and_execute_if_missing(filename_without_ext):
            return jsonify({'error': 'Required audio files are missing or not yet generated'}), 404

        return jsonify({'file_name': filename_without_ext}), 200
    else:
        return jsonify({'error': 'File type not allowed'}), 400

@app.route('/play/<filename>/<audio_file>')
def play_audio(filename, audio_file):
    allowed_files = ['vocals.wav', 'other.wav', 'drums.wav', 'bass.wav']
    file_directory = os.path.join(UPLOAD_FOLDER, filename)

    if audio_file == filename + '.mp3':
        return send_from_directory(file_directory, audio_file)
    elif audio_file in allowed_files:
        file_path = os.path.join(file_directory, audio_file)
        if os.path.exists(file_path):
            return send_from_directory(file_directory, audio_file)
        else:
            # File not found, check and execute if missing
            if not check_and_execute_if_missing(filename):
                return jsonify({'error': 'Required audio files are missing or not yet generated'}), 404
            return jsonify({'error': 'File not found'}), 404
    else:
        return jsonify({'error': 'File type not allowed'}), 400

if __name__ == '__main__':
    app.run(debug=True)
