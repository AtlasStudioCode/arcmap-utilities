import sys, os, comtypes.client, PyPDF2, zipfile, re
from PyPDF2 import PdfFileMerger, PdfFileReader

def join_pdf(in_files, out_file):
    # merge multiple input pdf files into a single output pdf file
    merger = PdfFileMerger()
    for in_file in in_files:
        merger.append(PdfFileReader(open(in_file, "rb")))
    merger.write(out_file)

def word_to_pdf(in_file):
    # convert word documents to pdf files of the same name
    out_file = in_file.replace(".doc", ".pdf").replace(".docx", ".pdf")
    doc = word.Documents.Open(in_file)
    doc.SaveAs(out_file, FileFormat = 17)
    doc.Close()

def convert_doc(in_files):
    # convert input word documents to pdf files and merge them into a single output pdf file
    word = comtypes.client.CreateObject("Word.Application")
    for in_file in in_files:
        out_file = word_to_pdf(in_file)
        pdf_files.append(out_file)
    word.Quit()

# create a list of files in the current working directory
files = os.listdir(os.getcwd())

# create initial lists for word documents, pdf files, and zip files
word_files = []
pdf_files = []
zip_file = None

for file in files:
    # sort files into their associated variables
    if (".doc" in file) or (".docx" in file):
        word_files.append(file)
    if ".pdf" in file:
        pdf_files.append(file)
    if ".zip" in file:
        zip_file = file

if word_files:
    # convert word documents
    convert_doc(word_files)

if pdf_files:
    # merge pdf files
    sort_files = []
    sort_files.extend([f for f in pdf_files if "crcr" in f.lower()])
    sort_files.extend([f for f in pdf_files if "ccs" in f.lower()])
    join_pdf(sort_files, "report.pdf")

if zip_file:
    # extract zip file contents to a gis folder
    os.mkdir("gis")
    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        zip_ref.extractall("gis")

