#create folder 
mkdir my-adk-agent
cd my-adk-agent

#install python 
py install 3.12
#set system env path 
export PATH=/c/Users/josep/AppData/Local/Python/bin/:$PATH
#set PATH=%PATH%;%USERPROFILE%\AppData\Local\Python\bin
echo $PATH

uv python update-shell
#install local virtual python version 
python -m venv .venv
source .venv/Scripts/activate

#install adk 
pip install google-adk

#Auth. optional 
gcloud auth login
gcloud auth application-default login
gcloud auth application-default print-access-token
gcloud projects list
gcloud config set project $GOOGLE_CLOUD_PROJECT
echo $GOOGLE_CLOUD_PROJECT
gcloud services enable aiplatform.googleapis.com
