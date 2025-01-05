# Code GPT Auto Doc Uploader

## Setup

1.Unzip or Clone into Directory of your choice.

2.Create Directory in the Root Directory of the Application called PDF_DIRECTORY *(this is where you stick all your PDFs)* I did make a change to the code so you can specify any directory. So you don't need to make this. If you do when prompted for the PDF directory just put in `PDF_DIRECTORY`. Since it is in your root directory you don't need to add anything special.

3.Create your Virtual Enviroment

`
python -m venv twitter_bot_env
`

Activate the virtual environment:

 -On Windows:

`
venv\Scripts\activate
`

or

`
.\venv\Scripts\activate
`

 -On macOS and Linux:

`
source venv/bin/activate
`

4.Install all dependancies.


`
pip install -r requirement.txt
`

**If for whatever reason it doesnt work or is missing, these are the dependancies needed:**

`
certifi==2024.12.14
charset-normalizer==3.4.1
idna==3.10
PyPDF2==3.0.1
python-dotenv==1.0.1
requests==2.32.3
urllib3==2.3.0
`

5.Once you are all setup, load all PDF files into the PDF_directory you created in the Root App Directory.

6.Then Fire it Up!

`
python uploadAgent.py
`

**For whatever reason it wouldnt let me upload `.pdf` files but it would do `.txt` files. So the `.pfg` Files are converted to `.txt` files and then all uploaded to your Orginizations Agent Knowledge Directory. **
