# Code GPT Auto Doc Uploader

## Setup

1.Unzip or Clone into Directory of your choice.
- to unzip, unzip straight into directory of choice.
- to clone, navigate to directory of choice in your terminal than clone with SSH-key use:
   -  `git clone git@github.com:IceMasterT/codeGPTAutoKnowledge.git`

2.Create Directory in the Root Directory of the Application called PDF_DIRECTORY *(this is where you stick all your PDFs)* I did make a change to the code so you can specify any directory. So you don't need to make this. If you do when prompted for the PDF directory just put in `PDF_DIRECTORY`. Since it is in your root directory you don't need to add anything special. So your Directory looks like this,
- |
- L_PDF_DIRECTORY
- |    <PDFs>
- |
- L_myvenv 
- |    <myvenv-files>
- |
- L_README.md
- L_env.example
- L_requirment.txt
- L_uploadAgent.py


3.Create your Virtual Enviroment

`
python -m venv myvenv
`

Activate the virtual environment:

 -On Windows:

`
myvenv\Scripts\activate
`

or

`
.\myvenv\Scripts\activate
`

 -On macOS and Linux:

`
source myvenv/bin/activate
`

4.Install all dependancies.


`
pip install -r requirement.txt
`

**If for whatever reason it doesnt work or is missing, these are the dependancies needs and they can be individually installed with `pip install <package name==number>`. just do down the list and install each one:**

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

6.Find the env.example file and put in your info from CodeGPT. You'll only need your API and ORG ID. I previously had it so it set your pdf directory for you but since I changed it so you can specify any directory. It doesn't really matter. once you add you directory in it **Change the Name of the file to .env**. Changing the name of the file to **.env** tells the python script to keep this file secret and hidden from anyone as it connects to the API and uploads your files. 

7.Then Fire it Up!

`
python uploadAgent.py  
`
**or**
`
python3 uploadAgent.py
`

`

**For whatever reason it wouldnt let me upload `.pdf` files but it would do `.txt` files. So the `.pfg` Files are converted to `.txt` files and then all uploaded to your Orginizations Agent Knowledge Directory. **



**TODO: Add in Advanced Upload Options to generate Metadata and change the Chunk Size. Currently it just uses the default settings.**
