from flask import Flask, request, send_file, render_template
import os
import tempfile
import zipfile
from fpdf import FPDF
from PIL import Image
import pdf2image
from pdf2docx import Converter
import aspose.words as aw  # For Word to PDF (requires Aspose.Words)
import aspose.slides as slides  # For PDF to PPT (requires Aspose.Slides)
import comtypes.client as comtypes  # For PPT to PDF (Windows only)
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Set your Poppler path here if needed (for Windows)
POPLER_PATH = r'C:/Users/ayush/Downloads/Release-24.08.0-0/poppler-24.08.0/Library/bin'  # Change this to your Poppler bin path, or set to None on Linux/Mac

def jpg_to_pdf(input_path, output_path):
    img = Image.open(input_path)
    pdf = FPDF(unit='mm', format='A4')
    pdf.add_page()
    pdf.image(input_path, x=0, y=0, w=210, h=297)
    pdf.output(output_path)

def pdf_to_docx(input_path, output_path):
    cv = Converter(input_path)
    cv.convert(output_path, start=0, end=None)
    cv.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    file = request.files['file']
    convert_type = request.form['convert_type']
    base_filename, ext = os.path.splitext(file.filename)
    temp_dir = tempfile.mkdtemp()
    input_path = os.path.join(temp_dir, secure_filename(f'input{ext}'))
    file.save(input_path)
    output_path = os.path.join(temp_dir, 'output')

    try:
        if convert_type == 'word2pdf':
            doc = aw.Document(input_path)
            output_path += '.pdf'
            doc.save(output_path)
            return send_file(output_path, as_attachment=True, download_name=base_filename + '.pdf')

        elif convert_type == 'jpg2pdf':
            output_path += '.pdf'
            jpg_to_pdf(input_path, output_path)
            return send_file(output_path, as_attachment=True, download_name=base_filename + '.pdf')

        elif convert_type == 'ppt2pdf':
            powerpoint = comtypes.CreateObject("PowerPoint.Application")
            deck = powerpoint.Presentations.Open(input_path)
            output_path += '.pdf'
            deck.SaveAs(output_path, 32)
            deck.Close()
            powerpoint.Quit()
            return send_file(output_path, as_attachment=True, download_name=base_filename + '.pdf')

        elif convert_type == 'pdf2word':
            output_path += '.docx'
            pdf_to_docx(input_path, output_path)
            return send_file(output_path, as_attachment=True, download_name=base_filename + '.docx')

        elif convert_type == 'pdf2jpg':
            poppler_args = {}
            if POPLER_PATH:
                poppler_args['poppler_path'] = POPLER_PATH
            images = pdf2image.convert_from_path(input_path, dpi=300, **poppler_args)
            output_files = []
            for i, img in enumerate(images):
                out_path = os.path.join(temp_dir, f"{base_filename}_page_{i+1}.jpg")
                img.save(out_path, 'JPEG')
                output_files.append(out_path)
            if len(output_files) == 1:
                return send_file(output_files[0], as_attachment=True, download_name=f"{base_filename}.jpg")
            else:
                zip_path = os.path.join(temp_dir, f"{base_filename}_jpgs.zip")
                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    for file_path in output_files:
                        arcname = os.path.basename(file_path)
                        zipf.write(file_path, arcname)
                return send_file(zip_path, as_attachment=True, download_name=f"{base_filename}_jpgs.zip")

        elif convert_type == 'pdf2ppt':
            with slides.Presentation() as pres:
                pres.slides.add_from_pdf(input_path)
                output_path += '.ppt'
                pres.save(output_path, slides.export.SaveFormat.PPT)
            return send_file(output_path, as_attachment=True, download_name=base_filename + '.ppt')

        else:
            return "Error: Unsupported conversion type.", 400

    except Exception as e:
        return f"Error: {str(e)}", 500

    finally:
        # Clean up temp files
        for f in os.listdir(temp_dir):
            try:
                os.remove(os.path.join(temp_dir, f))
            except:
                pass
        try:
            os.rmdir(temp_dir)
        except:
            pass

if __name__ == '__main__':
    app.run(debug=True)
