'''
Script used to create table of recently posted papers -- sorted by posting order.
NOTE: ignoring papers that are cross-listed.

Will sort & keep only JWST-related ones


NOTES:
> if hidden item, get_attribute() works with "innerHTML", "innerText", "textContent"


'''

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from datetime import datetime
import threading, time, getpass, sys, subprocess
import pandas as pd
import numpy as np
import sys

__author__ = 'Taylor Hutchison'
__email__ = 'aibhleog@tamu.edu'


# ------------------------ #
# -- creating dataframe -- #
# ------------------------ #
df_dtypes = {'order':int,'id':str,'pri_category':str, 
             'mathjax':bool, 'jwst':bool, 'title':str}#, 'abstract':str}
df = pd.DataFrame({'order':[],'id':[],'pri_category':[],'mathjax':[],'jwst':[],
                   'title':[]})#,'abstract':[]})


# opening browser & going to arXiv.org
driver = webdriver.Firefox()
driver.get("https://export.arxiv.org/list/astro-ph/new")

# date = driver.find_element_by_tag_name("h3") # expecting "New submissions for ___, DD dd YY"
date = driver.find_element(By.TAG_NAME,'h3')
date = date.text.split(', ')[1] # just pulling out the date part
print(f'Pulling arXiv post IDs for {date}',end='\n\n')

# pulling all of the New Submissions
posts = driver.find_element(By.ID,'articles')


# -- arXiv ID -- #
# -------------- #
items = posts.find_elements(By.TAG_NAME,'dt')
meta_infos = posts.find_elements(By.TAG_NAME,'dd')

# running through the posts to pull out arXiv ID
for i,item in enumerate(items[:4]):
    # getting the meta info
    meta_info = meta_infos[i]
    meta_info = meta_info.find_element(By.CLASS_NAME,'meta')
    
    # category, could be >1
    categories = meta_info.find_element(By.CLASS_NAME,'list-subjects')
    primary_category = categories.find_element(By.CLASS_NAME,'primary-subject').text
    other_categories = categories.text.lstrip('Subjects: ').lstrip(primary_category)

    # checking if we include it at all (aka if it's the Galaxies category)
    # if not, we skip this entry
    if 'astro-ph.GA' not in categories.text: continue

    # it IS a Galaxies paper:
    # -------------------------
    # arxiv ID
    arxiv_id = str(item.text.split('arXiv:')[1].split(' [')[0]) # arXiv number
    print(f'https://arxiv.org/abs/{arxiv_id}')
    
    # title
    title = meta_info.find_element(By.CLASS_NAME,'list-title.mathjax').text
    print(title)#,end='\n\n')
    
    # abstract
    abstract_loc = meta_info.find_element(By.TAG_NAME,'p')
    abstract_split = abstract_loc.text.split('\n') # slipt up where missing mathjax is
    new_abstract = abstract_split[0] # if no mathjax, this is full abstract
    mathjax_flag = False
    
    if len(abstract_split)>1: # checks if there IS mathjax involved
        mathjax_flag = True
        mathjax_locs = abstract_loc.find_elements(By.TAG_NAME, 'script') # the mathjax locs
        mathjax = [m.get_attribute("textContent") for m in mathjax_locs] # all mathjax text
        # I'm just manually adding the pre-mathified text back in, because slack won't convert anyway
        new_abstract = abstract_split[0] # piece-wising it together
        for i in range(len(abstract_split)-1):
            new_abstract += ' ' + mathjax[i]
            new_abstract += abstract_split[i+1]

    print('>'+new_abstract,end='\n\n')


    # checking for JWST in title & abstract
    jwst_flag = False
    if 'jwst' in title.lower() or 'jwst' in new_abstract.lower():
        jwst_flag = True


    # adding to end of dataframe
    # order, id, pri_category, mathjax, jwst, title # no abstract
    df.loc[len(df)] = [i, str(arxiv_id), primary_category, mathjax_flag,
                       jwst_flag, title]#, new_abstract]

# ------------------------- #


driver.close()



# -- saving dataframe -- #
# ---------------------- #
tosave_df = df.astype(df_dtypes).copy() # to make sure column dtypes don't change

cat = pd.read_csv('arXiv_exgal.txt',sep='\t',dtype=df_dtypes)
final_df = pd.concat([cat.copy(),tosave_df.copy()])

final_df.drop_duplicates(inplace=True,subset='id') # in case it's been run already that day
final_df.to_csv('arXiv_exgal.txt',sep='\t',index=False)










