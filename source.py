#!/usr/bin/env python
# coding: utf-8

# # {Project Title}📝
# 
# ![Banner](./assets/banner.jpeg)

# ## Topic
# *What problem are you (or your stakeholder) trying to address?*
# 📝 <!-- Answer Below -->
# 
# Historically, women have been underrepresented when it comes to health research and information. Female and male bodies are biologically different and can behave differently under the same circumstances or conditions, so it is very important that adequate research is done on both sexes so both halves of the population are able to be diagnosed and cared for correctly. There have been circumstances where female patients who are actively experiencing heart attacks are misdiagnosed or sent home because the common symptoms associated with it were drawn from research on men while women show different warning signs. 
# 
# I want to investigate the ratio of male and female representation in clincial trials overtime and see how it matches with the ratio of each sex experiencing that condition (their burden ratio). 

# ## Project Question
# *What specific question are you seeking to answer with this project?*
# *This is not the same as the questions you ask to limit the scope of the project.*
# 📝 <!-- Answer Below -->
# 
# Is there a gap in sex representation in clinical trials compared to their reported burden of the condition? Has this changed overtime?
# 
# Are there specific conditions that are more overlooked than others?
# 
# Is there a correlation between better representation and higher funding for different conditions?

# ## What would an answer look like?
# *What is your hypothesized answer to your question?*
# 📝 <!-- Answer Below -->
# 
# The answer will be the difference between the ratio of male and female representation in trials and the ratio of male and female burden of that condition. The difference can be calculated initially by condition, then by year, and then all together to show how that has evolved, if at all, overtime. 
# 
# Each step in calculations will answer different parts of our overarching question. The first step will reveal if there are specific conditions that are more overlooked than others, then how much of a gap there is per year, and finally if a gap exists, how it has changed through the years. 

# ## Data Sources
# *What 3 data sources have you identified for this project?*
# *How are you going to relate these datasets?*
# 📝 <!-- Answer Below -->
# 
# #### AACT 
# *Aggregate Analysis of ClinicalTrials.gov*
# 
# Extensive data collection on every clinical study registered in ClinicalTrials.gov. The data includes necessary information for the project question like trial dates, participants, sex of participants, and condition being studied. It also includes a variety of extra information that can be analyzed for this project such as trial phase, involvement of FDA regulated drugs/devices, and accepted participant age limits.
# 
# #### GBD
# *Global Burden of Disease*
# 
# Database of medical conditions and how much they are experienced (2008-2022). The data can be filtered by age, location, date, cause, measure, and more. For this project it will return the number of people reported to have experienced certain conditions in the United States by sex and year. The measure for people experiencing a condition will be "Prevalence", which reports how many people are experiencing it at a given time (a specific year). 
# 
# We will also use the "DALY" (Disability-Adjusted Life Years) measure to rank and choose the conditions that we will be comparing trial ratios on. DALY sums the years of life lost due to premature death with years lived with disability to count the years of healthy years lost. This way we can find the most prevalent conditions that are also more serious and more likely to require clinical research and trials for.
# 
# #### NIH RCDC
# *National Institute of Health, Research, Condition, and Disease*
# 
# Reports the annual monetary support level for conditions measured by grants, contracts, and other funding mechanisms used at the National Institute of Health (NIH). This will allow for analysis to see if there is a correlation with conditions that receive more funding and their levels of representation in clinical trials.
# 
# ### Connecting the Data
# 
# These datasets need to be connected on the basis on condition, but each define conditions with different terms or at different levels of generality. So to connect them we need to make hand-verified crosswalk tables that are keyed on condition and year. The top 15 Level 3 GBD causes by 2022 DALYs will be picked after removing all sex-specific, "other", and unmappable causes. GBD cause will match on AACT MeSH terms. Each cause will also be mapped to its closest NIH RCDC category, which will be joined on category and fiscal year. 

# ## Approach and Analysis
# *What is your approach to answering your project question?*
# *How will you use the identified data to answer your project question?*
# 📝 <!-- Start Discussing the project here; you can add as many code cells as you need -->
# 
# Using the data, I will be able to compare the participation in clinical trials by sex compared to the condition burden each sex reports. This will reveal if there are gaps between those who experience different conditions, and who is actually included in research for that. With data spanning from 2008-2022, we will be able to compare these gaps overtime to see if they have widened, stayed the same, or improved. 
# 
# Using the male and female share of prevalence from the GBD by condition, I can compare this ratio with the male and female share of enrolled participants from trials that report sex. The difference between these two ratios is the participation gap, which I will chart by condition and track overtime. Using the NIH RCDC set, I can join by condition and year to explore any possible correlations between wider participation gaps and amount of funding. Since RCDC only covers US funding, the GBD data and trials are also limited to the United States so all three describe the same population.

# ### AACT
# Only interventional trials (clinical trials, not observational studies) that started from 2008 to 2022 are pulled. Each trial's primary purpose and whether it accepts healthy volunteers are also pulled so trials that don't enroll patients can be filtered out later.

# In[65]:


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


# ### GBD
# Located in `data/` folder, downloaded from filterable queries and download abilities directly from site ([vizhub.healthdata.org/gbd-results](vizhub.healthdata.org/gbd-results)).
# 
# **File Name:** GBD_2008_2023.csv
# 
# #### Filters
# | Filter | Selection |
# |---|---|
# | GBD Estimate | Cause of death or injury |
# | Measure | Deaths, DALYs, Prevalence, Incidence |
# | Metric | Number |
# | Cause | All level 3 |
# | Location | United States of America |
# | Age | All ages |
# | Sex | Male, Female (not Both, each selected separately) |
# | Total percentage change | False |
# | Year | 2008–2022 |

# ### NIH RCDC
# Downloaded directly from [https://report.nih.gov/funding/categorical-spending#/](https://report.nih.gov/funding/categorical-spending#/) with "Download as Excel". Converted to CSV through Excel, cleaned extra rows above and below data, and uploaded as "/data/RCDC_2008_2025".

# ## Data Cleaning and Transformation

# ### GBD

# In[66]:


import os
import pandas as pd

os.makedirs("data/processed", exist_ok=True)

gbd = pd.read_csv("data/GBD_2008_2023.csv")
gbd.info()


# Dropping 2023 so the years match the 2008–2022 window, and keeping only the columns needed. Location, age, and metric only have one value each, so they are removed.

# In[67]:


gbd = gbd[gbd["year"] <= 2022]
gbd = gbd[["measure_name", "sex_name", "cause_name", "year", "val"]]
gbd["measure_name"] = gbd["measure_name"].replace("DALYs (Disability-Adjusted Life Years)", "DALYs")

print(gbd.isna().sum())
print("Duplicates:", gbd.duplicated().sum())


# Male and Female are moved into their own columns so the female share can be calculated. Sex-specific causes like prostate cancer only have rows for one sex, so the missing sex is filled with 0. Values are decimals because GBD numbers are model estimates, not exact counts.

# In[68]:


gbd = gbd.pivot_table(index=["measure_name", "cause_name", "year"], columns="sex_name", values="val").reset_index()
gbd = gbd.fillna(0)
gbd["Both"] = gbd["Male"] + gbd["Female"]
gbd["female_share"] = gbd["Female"] / gbd["Both"]
gbd.head()


# #### Choosing conditions
# Ranking causes by 2022 DALYs and dropping:
# - Sex-specific causes (one sex has less than 5% of prevalence)
# - Causes with no prevalence data
# - "Other" catch-all categories
# - Causes that don't have data for every year

# In[69]:


dalys_2022 = gbd[(gbd["measure_name"] == "DALYs") & (gbd["year"] == 2022)]
prev_2022 = gbd[(gbd["measure_name"] == "Prevalence") & (gbd["year"] == 2022)]

causes = dalys_2022[["cause_name", "Both"]].rename(columns={"Both": "dalys_2022"})
causes = causes.merge(prev_2022[["cause_name", "female_share"]], on="cause_name", how="left")
causes = causes.sort_values("dalys_2022", ascending=False)

zero_dalys = gbd[(gbd["measure_name"] == "DALYs") & (gbd["Both"] == 0)]["cause_name"].unique()

sex_specific = (causes["female_share"] < 0.05) | (causes["female_share"] > 0.95)
no_prevalence = causes["female_share"].isna()
other = causes["cause_name"].str.startswith("Other") | (causes["cause_name"] == "Endocrine, metabolic, blood, and immune disorders")
not_all_years = causes["cause_name"].isin(zero_dalys)

drop = sex_specific | no_prevalence | other | not_all_years
dropped_causes = causes[drop]
causes = causes[~drop]
dropped_causes


# The top 15 causes are used, after removing five that are poor fits:
# - **Low back pain:** no RCDC funding data before 2016
# - **Age-related and other hearing loss:** few trials with results, mostly device studies
# - **Headache disorders:** GBD combines migraine and tension-type headache, but most trials are for migraine, which affects mostly women, so the comparison doesn't line up
# - **Hypertensive heart disease:** the closest trial term and funding category are both "hypertension", which is much broader than heart disease caused by high blood pressure
# - **Neonatal disorders:** trials enroll newborns, so the sex of participants isn't something researchers choose

# In[70]:


weak_causes = ["Low back pain", "Age-related and other hearing loss", "Headache disorders", "Hypertensive heart disease", "Neonatal disorders"]
top_causes = causes[~causes["cause_name"].isin(weak_causes)].head(15)
top_causes


# In[71]:


gbd = gbd[gbd["cause_name"].isin(causes["cause_name"])]

gbd.to_csv("data/processed/gbd_clean.csv", index=False)
top_causes.to_csv("data/processed/gbd_top_causes.csv", index=False)
dropped_causes.to_csv("data/processed/gbd_dropped_causes.csv", index=False)


# ### NIH RCDC

# In[72]:


rcdc = pd.read_csv("data/RCDC_2008_2025.csv")
rcdc = rcdc.rename(columns={rcdc.columns[0]: "category"})
rcdc.head()


# Keeping only the 2008–2022 year columns. The ARRA columns are dropped because they were one-time stimulus funding, and the 2024 mortality and prevalence columns aren't funding. Footnote numbers at the end of category names (e.g. "Diabetes 5") are removed.

# In[73]:


years = [str(y) for y in range(2008, 2023)]
rcdc = rcdc[["category"] + years]
rcdc["category"] = rcdc["category"].str.replace(r"[\d,\s]+$", "", regex=True)
print("Duplicate categories:", rcdc["category"].duplicated().sum())


# Funding values are text like `1,132` with a dollar sign in front, so the dollar signs and commas are removed to make them numbers. Cells with `+` or `*` aren't dollar amounts, so they become missing (NaN) instead of 0.

# In[74]:


for year in years:
    rcdc[year] = pd.to_numeric(rcdc[year].str.replace("$", "").str.replace(",", ""), errors="coerce")

print(rcdc.isna().sum())


# Reshaping so each row is one category and year, which makes it easier to join with GBD later.

# In[75]:


rcdc = rcdc.melt(id_vars="category", var_name="year", value_name="funding_millions")
rcdc["year"] = rcdc["year"].astype(int)

rcdc.to_csv("data/processed/rcdc_clean.csv", index=False)
rcdc.head()


# ### AACT
# Only interventional trials (clinical trials, not observational studies) that started from 2008 to 2022 are pulled.

# In[76]:


studies_query = """
SELECT s.nct_id, s.start_date, s.enrollment, d.primary_purpose, e.healthy_volunteers
FROM studies s
LEFT JOIN designs d ON d.nct_id = s.nct_id
LEFT JOIN eligibilities e ON e.nct_id = s.nct_id
WHERE s.study_type = 'INTERVENTIONAL'
  AND s.start_date BETWEEN '2008-01-01' AND '2022-12-31'
"""
with engine.connect() as conn:
    studies = pd.read_sql(text(studies_query), conn)

studies.info()


# Start dates are converted to datetime so the start year can be pulled out and later joined to the GBD year.

# In[77]:


studies["start_date"] = pd.to_datetime(studies["start_date"])
studies["start_year"] = studies["start_date"].dt.year

print(studies.isna().sum())
print("Duplicate trials:", studies["nct_id"].duplicated().sum())


# Sex counts come from the baseline table using the standard "Sex: Female, Male" measure. Trials that used custom sex/gender categories are left out.

# In[78]:


sex_query = """
SELECT bm.nct_id, rg.title AS group_title, bm.category, bm.param_value_num AS count
FROM baseline_measurements bm
JOIN result_groups rg ON rg.id = bm.result_group_id
WHERE bm.title = 'Sex: Female, Male'
  AND bm.param_type = 'COUNT_OF_PARTICIPANTS'
  AND bm.classification IS NULL
"""
with engine.connect() as conn:
    sex = pd.read_sql(text(sex_query), conn)

sex["category"].value_counts()


# Some trials use all caps ("FEMALE"), so the labels are standardized. Each trial has a count for every arm plus a "Total" row, so the Total rows are removed and the arms are added up to avoid counting participants twice. Trials with 0 participants are dropped, and only trials in the 2008–2022 studies list are kept.

# In[79]:


sex["category"] = sex["category"].str.title()
sex = sex[sex["group_title"] != "Total"]

sex = sex.pivot_table(index="nct_id", columns="category", values="count", aggfunc="sum").reset_index()
sex = sex.fillna(0)
sex["total"] = sex["Female"] + sex["Male"]
sex = sex[sex["total"] > 0]
sex["female_share"] = sex["Female"] / sex["total"]
sex = sex[sex["nct_id"].isin(studies["nct_id"])]

studies["has_sex_results"] = studies["nct_id"].isin(sex["nct_id"])
print(f"{len(sex):,} of {len(studies):,} trials have sex counts")
sex.describe()


# In[80]:


studies.to_csv("data/processed/aact_studies.csv", index=False)
sex.to_csv("data/processed/aact_sex_counts.csv", index=False)


# ### Connecting the datasets
# The datasets don't share IDs, so each top 15 cause is matched by hand to an RCDC funding category and to MeSH condition terms in AACT.
# 
# #### GBD to RCDC
# Anxiety Disorders and Osteoarthritis only have funding from 2015.

# In[81]:


rcdc_matches = {
    "Ischemic heart disease": "Heart Disease - Coronary Heart Disease",
    "Drug use disorders": "Drug Abuse (NIDA only)",
    "Diabetes mellitus": "Diabetes",
    "Chronic obstructive pulmonary disease": "Chronic Obstructive Pulmonary Disease",
    "Stroke": "Stroke",
    "Tracheal, bronchus, and lung cancer": "Lung Cancer",
    "Alzheimer's disease and other dementias": "Alzheimer's Disease",
    "Chronic kidney disease": "Kidney Disease",
    "Depressive disorders": "Depression",
    "Anxiety disorders": "Anxiety Disorders",
    "Cirrhosis and other chronic liver diseases": "Chronic Liver Disease and Cirrhosis",
    "Alcohol use disorders": "Alcoholism, Alcohol Use and Health",
    "Colon and rectum cancer": "Colorectal Cancer",
    "Osteoarthritis": "Osteoarthritis",
    "Asthma": "Asthma",
}
rcdc_crosswalk = pd.DataFrame(rcdc_matches.items(), columns=["cause_name", "rcdc_category"])
rcdc_crosswalk


# #### GBD to AACT
# AACT tags each trial with MeSH condition terms. Terms were found by searching the list of terms with a keyword for each cause, then picking the matches by hand. Trials are tagged with both their direct terms and the broader "parent" terms above them, so a broad term like "myocardial ischemia" also picks up trials tagged with narrower terms like "myocardial infarction".

# In[82]:


terms_query = """
SELECT downcase_mesh_term, COUNT(DISTINCT nct_id) AS trials
FROM browse_conditions
GROUP BY downcase_mesh_term
"""
with engine.connect() as conn:
    mesh_terms = pd.read_sql(text(terms_query), conn)

# example search for one cause
mesh_terms[mesh_terms["downcase_mesh_term"].str.contains("stroke")].sort_values("trials", ascending=False).head(10)


# In[83]:


mesh_matches = {
    "Ischemic heart disease": ["myocardial ischemia"],
    "Drug use disorders": ["narcotic-related disorders", "cocaine-related disorders", "amphetamine-related disorders", "marijuana abuse"],
    "Diabetes mellitus": ["diabetes mellitus"],
    "Chronic obstructive pulmonary disease": ["pulmonary disease, chronic obstructive"],
    "Stroke": ["stroke"],
    "Tracheal, bronchus, and lung cancer": ["lung neoplasms"],
    "Alzheimer's disease and other dementias": ["alzheimer disease", "dementia"],
    "Chronic kidney disease": ["renal insufficiency, chronic"],
    "Depressive disorders": ["depressive disorder", "depression"],
    "Anxiety disorders": ["anxiety disorders"],
    "Cirrhosis and other chronic liver diseases": ["liver cirrhosis", "fatty liver"],
    "Alcohol use disorders": ["alcohol-related disorders"],
    "Colon and rectum cancer": ["colorectal neoplasms"],
    "Osteoarthritis": ["osteoarthritis"],
    "Asthma": ["asthma"],
}
mesh_crosswalk = pd.DataFrame(mesh_matches.items(), columns=["cause_name", "mesh_term"]).explode("mesh_term")
mesh_crosswalk


# Gestational diabetes trials are tagged under "diabetes mellitus", but gestational diabetes isn't part of the GBD cause, so those trials are removed. A trial matched by more than one term for the same cause is only counted once.

# In[84]:


exclude_terms = ["diabetes, gestational"]
terms = "', '".join(mesh_crosswalk["mesh_term"].tolist() + exclude_terms)
conditions_query = f"""
SELECT nct_id, downcase_mesh_term AS mesh_term
FROM browse_conditions
WHERE downcase_mesh_term IN ('{terms}')
"""
with engine.connect() as conn:
    conditions = pd.read_sql(text(conditions_query), conn)

excluded_trials = conditions[conditions["mesh_term"].isin(exclude_terms)]["nct_id"]
conditions = conditions[~conditions["nct_id"].isin(excluded_trials)]

trials = conditions.merge(mesh_crosswalk, on="mesh_term")[["nct_id", "cause_name"]].drop_duplicates()
trials = trials.merge(sex, on="nct_id").merge(studies[["nct_id", "start_year", "primary_purpose", "healthy_volunteers"]], on="nct_id")

print("Trials matched to more than one cause:", trials["nct_id"].duplicated().sum())
trials["cause_name"].value_counts()


# A few random trial titles per cause are checked to make sure the matches make sense.

# In[85]:


sample = trials.groupby("cause_name").sample(3, random_state=1)
ids = "', '".join(sample["nct_id"])
with engine.connect() as conn:
    titles = pd.read_sql(text(f"SELECT nct_id, brief_title FROM studies WHERE nct_id IN ('{ids}')"), conn)

sample.merge(titles, on="nct_id")[["cause_name", "brief_title"]]


# Prevention trials and trials that accept healthy volunteers enroll people who don't have the condition, so they can't be compared with the female share of people who have it. The main comparison only uses treatment trials that don't accept healthy volunteers. Prevention trials are kept separately for a side comparison.

# In[86]:


prevention_trials = trials[trials["primary_purpose"] == "PREVENTION"]
trials = trials[(trials["primary_purpose"] == "TREATMENT") & (trials["healthy_volunteers"] == False)]

print(f"{len(trials):,} treatment trials, {len(prevention_trials):,} prevention trials")
trials["cause_name"].value_counts()


# RCDC and GBD are US data, so trials are limited to ones where more than half of their sites are in the United States. AACT only reports sex counts for the whole trial, not by country, so this removes trials where most participants are outside the US. Trials with no sites listed are dropped.

# In[87]:


facilities_query = """
SELECT nct_id, COUNT(*) AS sites,
       SUM(CASE WHEN country = 'United States' THEN 1 ELSE 0 END) AS us_sites
FROM facilities
GROUP BY nct_id
"""
with engine.connect() as conn:
    facilities = pd.read_sql(text(facilities_query), conn)
facilities["us_site_share"] = facilities["us_sites"] / facilities["sites"]

trials = trials.merge(facilities[["nct_id", "us_site_share"]], on="nct_id")
trials = trials[trials["us_site_share"] > 0.5]
prevention_trials = prevention_trials.merge(facilities[["nct_id", "us_site_share"]], on="nct_id")
prevention_trials = prevention_trials[prevention_trials["us_site_share"] > 0.5]

print(f"{len(trials):,} treatment trials, {len(prevention_trials):,} prevention trials")
trials["cause_name"].value_counts()


# #### Combining
# Trials are grouped by cause and start year to get the female share of trial participants. That is compared with the female share of prevalence from GBD for the same cause and year, and the difference is the participation gap. A negative gap means women are underrepresented. RCDC funding is added on by category and year.

# In[88]:


gap = trials.groupby(["cause_name", "start_year"]).agg(
    trials=("nct_id", "count"), female=("Female", "sum"), total=("total", "sum")
).reset_index()
gap["trial_female_share"] = gap["female"] / gap["total"]

prevalence = gbd[gbd["measure_name"] == "Prevalence"][["cause_name", "year", "female_share"]]
prevalence = prevalence.rename(columns={"female_share": "prevalence_female_share"})
gap = gap.merge(prevalence, left_on=["cause_name", "start_year"], right_on=["cause_name", "year"]).drop(columns="start_year")
gap["gap"] = gap["trial_female_share"] - gap["prevalence_female_share"]

gap = gap.merge(rcdc_crosswalk, on="cause_name", how="left")
gap = gap.merge(rcdc, left_on=["rcdc_category", "year"], right_on=["category", "year"], how="left").drop(columns="category")
gap.head()


# In[89]:


rcdc_crosswalk.to_csv("data/processed/crosswalk_rcdc.csv", index=False)
mesh_crosswalk.to_csv("data/processed/crosswalk_mesh.csv", index=False)
trials.to_csv("data/processed/trials_matched.csv", index=False)
prevention_trials.to_csv("data/processed/trials_prevention.csv", index=False)
gap.to_csv("data/processed/gap_by_cause_year.csv", index=False)


# ## Exploratory Data Analysis
# 
# ### Female share in trials vs. female share of people with the condition
# For each cause, treatment trials from 2008–2022 are combined (total women / total participants) and compared with the average female share of prevalence from GBD. The median female share per trial is also shown. It counts each trial once, so a few very large trials can't drive the result. As a check, the gap is also calculated using only trials with all of their sites in the US.

# In[90]:


import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import PercentFormatter

gap = pd.read_csv("data/processed/gap_by_cause_year.csv")
trials = pd.read_csv("data/processed/trials_matched.csv")

by_cause = gap.groupby("cause_name").agg(
    female=("female", "sum"), total=("total", "sum"), prevalence_female_share=("prevalence_female_share", "mean")
).reset_index()
by_cause["trial_female_share"] = by_cause["female"] / by_cause["total"]
by_cause["gap"] = by_cause["trial_female_share"] - by_cause["prevalence_female_share"]

median_share = trials.groupby("cause_name")["female_share"].median().reset_index(name="median_trial_share")
by_cause = by_cause.merge(median_share, on="cause_name")
by_cause["median_gap"] = by_cause["median_trial_share"] - by_cause["prevalence_female_share"]

us_only = trials[trials["us_site_share"] == 1].groupby("cause_name")[["Female", "total"]].sum().reset_index()
us_only["us_only_share"] = us_only["Female"] / us_only["total"]
by_cause = by_cause.merge(us_only[["cause_name", "us_only_share"]], on="cause_name")
by_cause["us_only_gap"] = by_cause["us_only_share"] - by_cause["prevalence_female_share"]

by_cause = by_cause.sort_values("gap")
by_cause[["cause_name", "trial_female_share", "prevalence_female_share", "gap", "median_gap", "us_only_gap"]]


# In[91]:


fig, ax = plt.subplots(figsize=(10, 7))
ax.hlines(by_cause["cause_name"], by_cause["prevalence_female_share"], by_cause["trial_female_share"], color="lightgray", linewidth=2)
sns.scatterplot(data=by_cause, x="prevalence_female_share", y="cause_name", color="#eb6834", s=80, zorder=3, ax=ax,
                label="People with the condition (GBD)")
sns.scatterplot(data=by_cause, x="trial_female_share", y="cause_name", color="#2a78d6", s=80, zorder=3, ax=ax,
                label="Trial participants (AACT)")
ax.axvline(0.5, color="gray", linestyle="--", linewidth=1)
ax.xaxis.set_major_formatter(PercentFormatter(1, decimals=0))
ax.set_xlabel("Female share")
ax.set_ylabel("")
ax.set_title("Female share of trial participants vs. people with the condition, 2008–2022")
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=2)
plt.tight_layout()
plt.show()


# Each row is one cause. The orange dot is the female share of people who have the condition, and the blue dot is the female share of trial participants. When the blue dot is to the left of the orange dot, women are underrepresented in trials compared to how many women have the condition.
# 
# - Women are most underrepresented in stroke, with trials 17 percentage points below their share of the burden. Alzheimer's and other dementias, COPD, ischemic heart disease, chronic kidney disease, and anxiety disorders follow at 8–13 points below. Ischemic heart disease matches the heart attack example from the Topic section.
# - Cirrhosis is the only cause where women are clearly overrepresented, by 14 points.
# - The other causes, including drug and alcohol use disorders, are within about 3 points of even.
# - The median gap and the US-only gap point the same direction as the pooled gap for every cause except drug use disorders and asthma, which are close to 0. Stroke's gap is smaller on both checks (about −10 points), so a few large trials make it look worse in the pooled number. Chronic kidney disease's median gap is bigger (−16 points), so many smaller trials enroll even fewer women.
# - The gap isn't only about conditions that mostly affect men. Alzheimer's, anxiety disorders, chronic kidney disease, and COPD all affect more women than men in the US, but women are underrepresented in their trials.
# - Using US prevalence changes some results a lot. Lung cancer looked overrepresented compared with global prevalence (about 34% female), but in the US about half of people with lung cancer are women, so the gap is close to 0.

# #### Prevention trials
# Prevention trials enroll people who are at risk rather than people who have the condition, so they are compared with the treatment trials instead of with prevalence.

# In[92]:


prevention = pd.read_csv("data/processed/trials_prevention.csv")

prevention_by_cause = prevention.groupby("cause_name").agg(
    prevention_trials=("nct_id", "count"), female=("Female", "sum"), total=("total", "sum")
).reset_index()
prevention_by_cause["prevention_female_share"] = prevention_by_cause["female"] / prevention_by_cause["total"]
prevention_by_cause = prevention_by_cause.merge(by_cause[["cause_name", "trial_female_share"]], on="cause_name")
prevention_by_cause[["cause_name", "prevention_trials", "prevention_female_share", "trial_female_share"]].sort_values("prevention_trials", ascending=False)


# - Prevention trials enroll a higher share of women than treatment trials for alcohol use disorders (23 points higher), ischemic heart disease (14 points), Alzheimer's (9 points), drug use disorders (8 points), diabetes (7 points), and stroke (6 points). For these, women are included in research on preventing the condition, but less so in trials testing treatments for people who already have it.
# - Cirrhosis, colon and rectum cancer, osteoarthritis, and depressive disorders go the other way, with a 5–9 point lower female share in prevention trials. COPD, cirrhosis, and osteoarthritis have 10 or fewer prevention trials, so those comparisons are less reliable.

# ### Participation gap over time
# One small chart per cause, in the same order as the chart above. The gap is in percentage points: below the dashed line at 0 means women are underrepresented in that year's trials. The dotted line marks 2016, when NIH started requiring researchers to consider sex as a biological variable.

# In[93]:


import plotly.express as px

gap["gap_points"] = gap["gap"] * 100

fig = px.line(
    gap, x="year", y="gap_points", facet_col="cause_name", facet_col_wrap=3,
    category_orders={"cause_name": by_cause["cause_name"].tolist()},
    hover_data=["trials"], markers=True, height=1100,
    labels={"gap_points": "Gap (pts)", "year": "Year", "trials": "Trials"},
    title="Participation gap over time (female share of trial participants minus female share of people with the condition)",
)
fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[1]))
fig.update_traces(line_color="#2a78d6")
fig.add_hline(y=0, line_dash="dash", line_color="gray")
fig.add_vline(x=2016, line_dash="dot", line_color="lightgray")
fig.show()


# - Stroke, ischemic heart disease, Alzheimer's, and COPD are below 0 every year, and chronic kidney disease is below 0 every year except 2020.
# - Some causes improve over time. COPD moves from about −16 to −21 points in 2008–2009 to between −3 and −9 after 2018. Diabetes is below 0 most years before 2016 and above 0 from 2016 on. Alzheimer's is between −6 and −8 points in 2020–2022, compared with −10 to −18 before 2016.
# - Ischemic heart disease, stroke, and chronic kidney disease don't show a clear improvement.
# - Drug and alcohol use disorders swing a lot from year to year (from about −20 to +20 points), with only 6–23 trials per year. Cirrhosis only has 1–8 trials per year before 2015. Fewer trials from 2022 have posted results yet, so the last year is also less reliable.

# ### NIH funding vs. participation gap
# Each point is one cause. Funding is the average yearly NIH funding for the cause's RCDC category from 2008–2022, on a log scale because the largest categories get over 10 times more than the smallest. The gap is the same combined gap from the first chart.

# In[94]:


import numpy as np

funding = gap.groupby("cause_name")["funding_millions"].mean().reset_index(name="avg_funding")
by_cause = by_cause.merge(funding, on="cause_name")
by_cause["gap_points"] = by_cause["gap"] * 100

short_names = {
    "Ischemic heart disease": "Ischemic heart disease",
    "Drug use disorders": "Drug use",
    "Diabetes mellitus": "Diabetes",
    "Chronic obstructive pulmonary disease": "COPD",
    "Stroke": "Stroke",
    "Tracheal, bronchus, and lung cancer": "Lung cancer",
    "Alzheimer's disease and other dementias": "Alzheimer's",
    "Chronic kidney disease": "Kidney disease",
    "Depressive disorders": "Depression",
    "Anxiety disorders": "Anxiety",
    "Cirrhosis and other chronic liver diseases": "Cirrhosis",
    "Alcohol use disorders": "Alcohol use",
    "Colon and rectum cancer": "Colorectal cancer",
    "Osteoarthritis": "Osteoarthritis",
    "Asthma": "Asthma",
}
by_cause["short_name"] = by_cause["cause_name"].map(short_names)

print("Correlation (log funding vs. gap):", round(np.log10(by_cause["avg_funding"]).corr(by_cause["gap_points"]), 2))

fig, ax = plt.subplots(figsize=(10, 6))
sns.scatterplot(data=by_cause, x="avg_funding", y="gap_points", color="#2a78d6", s=80, ax=ax)

# move a few labels so they don't overlap
for _, row in by_cause.iterrows():
    if row["short_name"] == "Asthma":
        ax.annotate(row["short_name"], (row["avg_funding"], row["gap_points"]), xytext=(-6, 4), textcoords="offset points", fontsize=9, ha="right")
    elif row["short_name"] == "Depression":
        ax.annotate(row["short_name"], (row["avg_funding"], row["gap_points"]), xytext=(0, -14), textcoords="offset points", fontsize=9, ha="center")
    else:
        ax.annotate(row["short_name"], (row["avg_funding"], row["gap_points"]), xytext=(6, 4), textcoords="offset points", fontsize=9)

ax.axhline(0, color="gray", linestyle="--", linewidth=1)
ax.set_xscale("log")
ax.set_xticks([100, 200, 500, 1000], ["100", "200", "500", "1,000"])
ax.set_xlabel("Average yearly NIH funding, 2008–2022 (millions of dollars, log scale)")
ax.set_ylabel("Participation gap (percentage points)")
ax.set_title("NIH funding vs. participation gap by cause")
plt.tight_layout()
plt.show()


# - The correlation is about 0, so causes that get more NIH funding don't have smaller gaps.
# - Alzheimer's gets the most funding (about 1.3 billion dollars a year) but women are still 12 points underrepresented. Drug use disorders and diabetes are also highly funded and are close to even.
# - COPD and osteoarthritis get the least funding (about 100 million dollars a year), but COPD has an 11-point gap while osteoarthritis is close to even.
# - Funding is total NIH spending on the condition, not money aimed at including women in trials. Anxiety disorders and osteoarthritis only have funding from 2015, so their averages cover fewer years.

# ### Number of trials per cause
# How many treatment trials with sex counts support each cause's gap. A trial that matches more than one cause is counted for each.

# In[95]:


trial_counts = trials.groupby("cause_name").agg(trials=("nct_id", "count"), participants=("total", "sum")).reset_index()
trial_counts["short_name"] = trial_counts["cause_name"].map(short_names)
trial_counts = trial_counts.sort_values("trials", ascending=False)
print(trial_counts[["cause_name", "trials", "participants"]])

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(data=trial_counts, x="trials", y="short_name", color="#2a78d6", ax=ax)
ax.bar_label(ax.containers[0], padding=3, fontsize=9)
ax.set_xlabel("Number of trials")
ax.set_ylabel("")
ax.set_title("Treatment trials with sex counts per cause, 2008–2022")
plt.tight_layout()
plt.show()


# - Diabetes, lung cancer, and depressive disorders have the most trials (615–861) and make up over 40% of all matched trials. Cirrhosis has the fewest at 145.
# - The number of trials doesn't follow the burden. Ischemic heart disease has the highest US DALYs but only 205 trials, and drug use disorders is second but has 246 trials.
# - Trial sizes are very different between causes. Ischemic heart disease has 205 trials but about 94,000 participants (about 460 per trial), while lung cancer has 696 trials but only about 55,000 participants (about 80 per trial). Causes with fewer, larger trials can have their gap shaped by a few studies.
# - Every cause has at least 145 trials, so the combined gaps in the first chart are based on enough data. Single years have far fewer trials, which is why the lines in the gap-over-time chart jump around.

# ### Female share of trial participants over time
# For context, this uses every interventional trial with sex counts, for all conditions and countries, not just the 15 causes. The median female share per trial is used because a few huge trials (one has about 2.9 million participants) make the pooled share jump from year to year. Treatment trials that don't accept healthy volunteers are shown separately since that is the group used for the gap.

# In[96]:


sex_counts = pd.read_csv("data/processed/aact_sex_counts.csv")
studies = pd.read_csv("data/processed/aact_studies.csv")

all_trials = sex_counts.merge(studies[["nct_id", "start_year", "primary_purpose", "healthy_volunteers"]], on="nct_id")
all_trials["group"] = "All trials"
treatment_trials = all_trials[(all_trials["primary_purpose"] == "TREATMENT") & (all_trials["healthy_volunteers"] == False)].copy()
treatment_trials["group"] = "Treatment trials (no healthy volunteers)"

yearly = pd.concat([all_trials, treatment_trials]).groupby(["group", "start_year"]).agg(
    trials=("nct_id", "count"), median_female_share=("female_share", "median")
).reset_index()

fig = px.line(
    yearly, x="start_year", y="median_female_share", color="group", markers=True, hover_data=["trials"],
    color_discrete_sequence=["#2a78d6", "#eb6834"],
    labels={"start_year": "Start year", "median_female_share": "Median female share", "group": "", "trials": "Trials"},
    title="Median female share of participants per trial, all conditions, 2008–2022",
)
fig.add_hline(y=0.5, line_dash="dash", line_color="gray")
fig.update_yaxes(tickformat=".0%")
fig.update_layout(legend=dict(orientation="h", y=-0.2))
fig.show()


# - In the typical trial, women were slightly under half of participants from 2008–2015 (about 47–48%). This rises to 50% by 2018 and 53% in 2022.
# - Treatment trials enroll fewer women than all trials every year. They stay around 46% until 2016 and only reach 50% in 2021–2022.
# - The increase starts around 2016, the same time as the NIH sex as a biological variable policy, but this chart can't show that the policy caused it. 2022 also has fewer trials with posted results.
# - The gaps in the first chart are condition-specific. Treatment trials overall are only a few points below 50%, while stroke, Alzheimer's, COPD, and ischemic heart disease are 11–17 points below their share of the burden.

# ## Resources and References
# *What resources and references have you used for this project?*
# 📝 <!-- Answer Below -->

# In[98]:


# ⚠️ Make sure you run this cell at the end of your notebook before every submission!
get_ipython().system('jupyter nbconvert --to python source.ipynb')

