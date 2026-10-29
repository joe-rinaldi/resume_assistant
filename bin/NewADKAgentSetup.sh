#create folder 
mkdir my-adk-agent
cd my-adk-agent
#install local virtual python version 
python -m venv .venv
source .venv/Scripts/activate
#install adk 
pip install google-adk

#go to ai studio create project and get api key 
export GEMINI_API_KEY=<APIKey>
export GOOGLE_API_KEY=<APIKey>
export GOOGLE_CLOUD_PROJECT=gen-lang-client-0667941054
export GOOGLE_CLOUD_LOCATION=us-central1

#
gcloud auth login
gcloud auth application-default login
gcloud auth application-default print-access-token
gcloud projects list
gcloud config set project $GOOGLE_CLOUD_PROJECT
echo $GOOGLE_CLOUD_PROJECT
gcloud services enable aiplatform.googleapis.com



adk web 
