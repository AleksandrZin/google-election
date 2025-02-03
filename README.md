# Post-Election Search Trends: Can Voters Change Their Minds?
# Introduction
This project is a web dashboard that displays data and provides the results of a t-test analysis, inspired by a Tik-Tok video discussing the increase in Google searches related to changing votes.

# Data
- __Votes Data__: Due to the unavailability of real-time vote data from providers at the project's inception, votes data is scraped from [Routers](https://www.reuters.com/graphics/USA-ELECTION/RESULTS/zjpqnemxwvx/). The scraping script can be found at scrap_script.py, and the raw data is saved at `data/raw`.

- __Geo Data__: This dataset is taken from [MappingAPI](https://github.com/PublicaMundi/MappingAPI).

- __Google Trends Data__: This data is manually downloaded from Google Trends.

# Usage
To use the project, you can run the web dashboard locally and interact with the data and t-test results.

1. **Clone the Git Repository**

   To clone the repository, open your terminal and run the following command:

   ```
   git clone https://github.com/your-username/vote-change-trend-analysis.git
   ```

2. **Go to the new folder**
    ```
    cd US_election
    ```

3. **Create a Virtual Environment**

   To create a virtual environment, navigate to the project directory and run the following command:

   ```
   python3 -m venv venv
   ```

4. **Activate the Virtual Environment**

   To activate the virtual environment, run the following command:

   - On Linux/macOS:

     ```
     source venv/bin/activate
     ```

   - On Windows:

     ```
     venv\Scripts\activate
     ```

5. **Install Requirements**

   To install the required packages, run the following command:

   ```
   pip install -r requirements.txt
   ```

6. **Run the Web Dashboard**

   To run the web dashboard, activate the virtual environment and run the following command:

   ```
   python dashboard.py
   ```

   The web dashboard will be accessible at `http://localhost:5000`.





