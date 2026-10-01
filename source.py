#!/usr/bin/env python
# coding: utf-8

# # {Project Title}📝
# 
# ![Banner](./assets/banner.jpeg)

# ## Topic
# *What problem are you (or your stakeholder) trying to address?*
# 📝 <!-- Answer Below -->
# 
# I want to investigate the disparity in health research for women. Historically, health research on conditions that happen to both men and women can have a disproportionate amount of testing and studies done on men. Due to the biological differences between sexes, women may react differently or show different symptoms for conditions yet these findings are unknown due to lack of research. For example, the symptoms of a heart attack are typically a crushing, chest pain, but for women they actually more often have nausea, jaw or back pain, shortness of breath, or other symptoms. This has led to women actively experiencing heart attacks getting misdiagnosed and/or sent home when they need help.

# ## Project Question
# *What specific question are you seeking to answer with this project?*
# *This is not the same as the questions you ask to limit the scope of the project.*
# 📝 <!-- Answer Below -->
# 
# How has women's representation in clinical trials changed over time relative to their share of disease burden, and which conditions remain most overlooked?

# ## What would an answer look like?
# *What is your hypothesized answer to your question?*
# 📝 <!-- Answer Below -->
# 
# I hypothesize that women's representation in trials will appear close to parity with all the trials data combined, but that this will initially hide large gaps in specific conditions. I expect women to be underrepresented relative to their disease burden in cardiovascular disease and some cancers based on prior research.
# 
# Charts may be trendlines per condition showing representation over time compared with their disease burden. Conditions with a significantly higher burden than representation will be those that are overlooked signaling a gap in research.

# ## Data Sources
# *What 3 data sources have you identified for this project?*
# *How are you going to relate these datasets?*
# 📝 <!-- Answer Below -->
# 
# **AACT** - *Aggregate Analysis of ClinicalTrials.gov*
# Contains data elements for every study registered in ClinicalTrials.gov. Includes dates, trial phase data, participant counts by sex, and the conditions being studied.
# 
# **GBD** - *Global Burden of Disease*
# The Institute for Health Metrics and Evaluation (IHME) publishes a searchable and downloadable set of data relating to GBD estimates. Covers from 1990 onward.
# 
# **NHAMCS** - *National Hospital Ambulatory Medical Care Survey*
# Public CDC dataset of emergency department vists with information like patient sex, reason for visit, wait time, tests ordered, diagnosis, and whether patient was admitted or sent home.
# 
# The biggest difficulty will be connecting these datasets by condition. Conditions are defined differently and may need to be generalized with terms like "cardiovascular diseases". The joining table may need to be manually created to create connections to specific terms depending on how it is defined in each set. In addition to the condition, tables will be joined by date (year). This is how I will relate the AACT and GBD tables.
# 
# The NHAMCS will be analyzed based off of results of the other datasets. Where there tend to be gaps it can reveal more insight into how certain symptoms and conditions are treated between sexes. 
# 

# ## Approach and Analysis
# *What is your approach to answering your project question?*
# *How will you use the identified data to answer your project question?*
# 📝 <!-- Start Discussing the project here; you can add as many code cells as you need -->
# 
# I will download the datasets from their sources and build the connector between the AACT and GBD datasets. These can be unified via the `mesh_term` and `cause_name` fields from each database respectively.
# 
# I will pull trials from the AACT dataset that have sex specific enrollment data and map total female and overall participants by condition and time period. Using the GBD dataset I can calculate how each sex has historically fared with a certain condition. By calculating something like the number of deaths, per case, per sex we can see how it is affecting each individually. Based off of each dataset we can also calculate the ratio of female research participants with their share of burden.
# 
# I can plot these overtime by condition and find if there are any significant gaps that correlate with a lack of research.

# ### AACT
# Connected by establishing connection to database with credentials generated after creating account.
# 
# ### GBD
# Located in `data/` folder, downloaded from filterable queries and download abilities directly from site.

# In[ ]:


import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, URL, text
import pandas as pd

load_dotenv()

# -- AACT
# Establish connection
url = URL.create(
    "postgresql+psycopg2",
    username=os.getenv("AACT_USER"),
    password=os.getenv("AACT_PASSWORD"),
    host="aact-db.ctti-clinicaltrials.org",
    port=5432,
    database="aact",
)
engine = create_engine(url)

with engine.connect() as conn:
    df = pd.read_sql(text("SELECT nct_id, brief_title FROM studies LIMIT 5"), conn)
df


# ### NHAMCS
# Downloaded from CDC's FTP server. Added code here so downloading is easily reproducible for others.

# In[8]:


from pathlib import Path
from urllib.request import Request, urlopen
from zipfile import ZipFile

BASE_URL = "https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Dataset_Documentation/NHAMCS/stata/"
FILES = {
    2016: "ED2016-stata.zip", 2017: "ed2017-stata.zip", 2018: "ED2018-stata.zip",
    2019: "ED2019-stata.zip", 2020: "ed2020-stata.zip", 2021: "ed2021-stata.zip",
    2022: "ed2022-stata.zip",
}

data_dir = Path("data/nhamcs")
data_dir.mkdir(parents=True, exist_ok=True)

for year, filename in FILES.items():
    zip_path = data_dir / filename
    if not zip_path.exists():
        req = Request(BASE_URL + filename, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req) as response, open(zip_path, "wb") as f:
            f.write(response.read())
        print(f"Downloaded {filename}")
    with ZipFile(zip_path) as z:
        z.extractall(data_dir / str(year))


# ## Resources and References
# *What resources and references have you used for this project?*
# 📝 <!-- Answer Below -->

# In[2]:


# ⚠️ Make sure you run this cell at the end of your notebook before every submission!
get_ipython().system('jupyter nbconvert --to python source.ipynb')

