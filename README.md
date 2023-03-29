# Political Wind Forecast
Political Wind Forecast is a web application built with Streamlit. The application allows users to input the name of a politician and select websites to crawl. Python web crawlers then collect data from the selected websites, and the data is fed into a RoBERTa-large natural language processing model for sentiment analysis. The average sentiment score of the analyzed articles is used to provide an objective rating of the politician's political sentiment.

# Installation
To install the necessary packages, run the following command:

```
pip install -r requirements.txt
```

# Usage
To start the application, run the following command:

```
streamlit run app.py
```

Once the application is running, you can input the name of a politician and select the websites to crawl. The application will crawl the selected websites and analyze the sentiment of the collected data.

# Files
* app.py: The main application file.
* utils.py: Utility functions used in the application.
* requirements.txt: The list of required packages.

# License
This project is licensed under the MIT License. See the LICENSE file for more information.