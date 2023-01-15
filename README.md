# Random data generator


Generate a dataset of random data. Each column can be configured to generate data with particular data type and pattern. Columns in dataset can also share a relationship by defining data constraints and selecting pattern types like 'calculated' or 'expression'.

Checkout the webapp at [Random data generator](https://random-datagen.streamlit.app). Thanks to streamlit framework and community cloud that helped this development!

---

##### Setting project on local
Clone repository from Github,
1. Create a project folder. Go to project folder and create python virtual environment and 'src' folder.
2. Run command `git clone https://github.com/vedantkau/random-data-generator.git ./src`.
3. Activate python virtual environment and run command `pip install -r ./src/requirements.txt`.
4. Go to src folder and run command `streamlit run webapp.py`
5. Edit config file in libs folder to edit maximum no. of rows or columns.

Pull docker version,
1. Run command `docker pull vedantkau/random-datagen-webapp:no_limits`.
2. Run `docker run -p 8080:8501 --name random-datagen-container1 vedantkau/random-datagen-webapp:no_limits` and go to site `localhost:8080`.
