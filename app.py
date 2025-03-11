import os
import configparser
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, Response
from werkzeug.utils import secure_filename
import collect_to_md
import md_to_pdf
from datetime import datetime
import threading
import queue
import time

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Ensure directories exist
os.makedirs('input', exist_ok=True)
os.makedirs('output', exist_ok=True)
os.makedirs('uploads', exist_ok=True)

CONFIG_FILE = 'config.txt'

# Global message queue for progress updates
progress_messages = {}

# Add context processor for current year
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

def load_config():
    """Load configuration from config.txt"""
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
    else:
        # Create default config
        config['API'] = {
            'api_key': '',
            'model_id': ''
        }
        config['Processing'] = {
            'batch_size': '10'
        }
    return config

def save_config(api_key, model_id, batch_size):
    """Save configuration to config.txt"""
    config = configparser.ConfigParser()
    config['API'] = {
        'api_key': api_key,
        'model_id': model_id
    }
    config['Processing'] = {
        'batch_size': batch_size
    }
    with open(CONFIG_FILE, 'w') as f:
        config.write(f)

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/api_config', methods=['GET', 'POST'])
def api_config():
    """API configuration page"""
    config = load_config()
    
    if request.method == 'POST':
        api_key = request.form.get('api_key', '')
        model_id = request.form.get('model_id', '')
        batch_size = request.form.get('batch_size', '10')
        
        save_config(api_key, model_id, batch_size)
        flash('Configuration saved successfully!', 'success')
        return redirect(url_for('api_config'))
    
    return render_template('api_config.html', 
                          api_key=config['API'].get('api_key', ''),
                          model_id=config['API'].get('model_id', ''),
                          batch_size=config['Processing'].get('batch_size', '10'))

@app.route('/collect_to_md', methods=['GET', 'POST'])
def collect_to_md_route():
    """Collect URLs to Markdown page"""
    if request.method == 'POST':
        # Check if config is set
        config = load_config()
        if not config['API'].get('api_key') or not config['API'].get('model_id'):
            flash('Please configure API settings first!', 'error')
            return redirect(url_for('api_config'))
        
        # Get URLs from text area or file
        urls = request.form.get('urls', '')
        url_file = request.files.get('url_file')
        
        if url_file and url_file.filename:
            # Save uploaded file
            filename = secure_filename(url_file.filename)
            input_path = os.path.join('input', filename)
            url_file.save(input_path)
        elif urls:
            # Save text area content to file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            input_path = os.path.join('input', f'urls_{timestamp}.txt')
            with open(input_path, 'w', encoding='utf-8') as f:
                f.write(urls)
        else:
            flash('Please provide URLs either in the text area or upload a file!', 'error')
            return redirect(url_for('collect_to_md_route'))
        
        # Generate output filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = os.path.join('output', f'AI_news_summary_{timestamp}.md')
        
        # Create a unique task ID for this processing job
        task_id = f"task_{timestamp}"
        progress_messages[task_id] = queue.Queue()
        
        # Start processing in a background thread
        def process_task():
            try:
                # Define callback function to update progress
                def progress_callback(message):
                    progress_messages[task_id].put(message)
                
                # Call collect_to_md function with progress callback
                collect_to_md.main(input_path, output_path, progress_callback)
                
                # Add a completion message with the download URL
                progress_messages[task_id].put("COMPLETED:" + output_path)
            except Exception as e:
                progress_messages[task_id].put(f"ERROR: {str(e)}")
        
        # Start the background thread
        thread = threading.Thread(target=process_task)
        thread.daemon = True
        thread.start()
        
        # Return the template with the task ID
        return render_template('collect_to_md.html', task_id=task_id)
    
    return render_template('collect_to_md.html')

@app.route('/progress/<task_id>')
def progress_stream(task_id):
    """Stream progress updates for a specific task"""
    def generate():
        if task_id not in progress_messages:
            yield f"data: Task {task_id} not found\n\n"
            return
        
        # Send any messages already in the queue
        q = progress_messages[task_id]
        while True:
            try:
                # Non-blocking get with timeout
                message = q.get(timeout=1)
                yield f"data: {message}\n\n"
                
                # If this is a completion message, clean up
                if message.startswith("COMPLETED:") or message.startswith("ERROR:"):
                    # Keep the queue for a while before removing it
                    time.sleep(60)  # Keep for 1 minute after completion
                    if task_id in progress_messages:
                        del progress_messages[task_id]
                    break
            except queue.Empty:
                # Send a keep-alive message every second
                yield f"data: KEEPALIVE\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/download/<path:filename>')
def download_file(filename):
    """Download a file"""
    return send_file(filename, as_attachment=True)

@app.route('/md_to_pdf', methods=['GET', 'POST'])
def md_to_pdf_route():
    """Convert Markdown to PDF page"""
    if request.method == 'POST':
        # Check if markdown file was uploaded
        if 'md_file' not in request.files:
            flash('No markdown file uploaded!', 'error')
            return redirect(request.url)
        
        md_file = request.files['md_file']
        if md_file.filename == '':
            flash('No markdown file selected!', 'error')
            return redirect(request.url)
        
        # Save markdown file
        md_filename = secure_filename(md_file.filename)
        md_path = os.path.join('uploads', md_filename)
        md_file.save(md_path)
        
        # Check for highlight file
        highlight_path = None
        if 'highlight_file' in request.files:
            highlight_file = request.files['highlight_file']
            if highlight_file.filename != '':
                highlight_filename = secure_filename(highlight_file.filename)
                highlight_path = os.path.join('uploads', highlight_filename)
                highlight_file.save(highlight_path)
        
        try:
            # Generate output filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_base = os.path.splitext(md_filename)[0]
            output_path = os.path.join('output', f'{output_base}_{timestamp}.pdf')
            
            # Call md_to_pdf function
            try:
                pdf_path, md_with_toc_path = md_to_pdf.convert_md_to_pdf(md_path, output_path, highlight_path)
                
                # Check if PDF was generated
                if os.path.exists(pdf_path):
                    flash('Successfully generated PDF file!', 'success')
                    # Get the filename from the path and ensure it has .pdf extension
                    pdf_filename = os.path.basename(pdf_path)
                    if not pdf_filename.lower().endswith('.pdf'):
                        pdf_filename = f"{pdf_filename}.pdf"
                    return send_file(
                        pdf_path, 
                        as_attachment=True,
                        download_name=pdf_filename,
                        mimetype='application/pdf'
                    )
                else:
                    flash(f'PDF generation failed! PDF file not found at {pdf_path}', 'error')
                    
                    # If markdown with TOC was generated, offer it for download
                    if os.path.exists(md_with_toc_path):
                        flash(f'However, Markdown with TOC was generated successfully. You can download it.', 'info')
                        # Get the filename from the path and ensure it has .md extension
                        md_filename = os.path.basename(md_with_toc_path)
                        if not md_filename.lower().endswith('.md'):
                            md_filename = f"{md_filename}.md"
                        return send_file(
                            md_with_toc_path, 
                            as_attachment=True,
                            download_name=md_filename,
                            mimetype='text/markdown'
                        )
                    
                    return redirect(url_for('md_to_pdf_route'))
            except Exception as inner_e:
                flash(f'Error in PDF conversion: {str(inner_e)}', 'error')
                import traceback
                app.logger.error(f'PDF conversion error: {traceback.format_exc()}')
                return redirect(url_for('md_to_pdf_route'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
            import traceback
            app.logger.error(f'General error: {traceback.format_exc()}')
            return redirect(url_for('md_to_pdf_route'))
    
    return render_template('md_to_pdf.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 