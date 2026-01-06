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
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from datetime import datetime
import threading, time, getpass, sys, subprocess
import pandas as pd
import numpy as np
import sys

__author__ = 'Taylor Hutchison'
__email__ = 'astro.hutchison@gmail.com'


from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options

# Initialize FirefoxOptions
firefox_options = Options()
firefox_options.add_argument("--headless")

# # Service pattern applies as of Selenium v4
# service = Service('/path/to/geckodriver')

# Initialize the WebDriver using headless options
# driver = webdriver.Firefox(service=service, options=firefox_options)
# driver = webdriver.Firefox(options=firefox_options)


# ------------------------ #
# -- creating dataframe -- #
# ------------------------ #
df_dtypes = {'order':int,'id':str,'pri_category':str, 
             'mathjax':bool, 'jwst':bool, 'sim':bool, 'z':bool, 'title':str}
df = pd.DataFrame({'order':[],'id':[],'pri_category':[],'mathjax':[],'jwst':[],
                   'sim':[],'z':[],'title':[]})


# opening browser & going to arXiv.org
# driver = webdriver.Firefox()
driver = webdriver.Firefox(options=firefox_options)
driver.get("https://export.arxiv.org/list/astro-ph/new")

# date = driver.find_element_by_tag_name("h3") # expecting "New submissions for ___, DD dd YY"
date = driver.find_element(By.TAG_NAME,'h3')
date = date.text.split(', ')[1] # just pulling out the date part
print(f'Pulling high-z + galaxy arXiv postings for {date}',end='\n\n\n')

# pulling all of the New Submissions
posts = driver.find_element(By.ID,'articles')


# flags for identifying highz work
highz_flags = [r'z\sim',r'z \sim','z~','z ~',r' z ',r' z,',r'z=',r'z =',r'z \leq',
               r'z\leq',r'z\geq',r'z \geq',r'z \lesssim',r'z\lesssim',
               r'z \gtrsim',r'z\gtrsim',r'z_',r'z _',r'z>',r'z >',r'z<',r'z <',
               'high-z','high z ','high-redshift','high redshift','cosmic dawn',
               'cosmic noon']

# flags for simulations
sim_flags = ['cosmological simulation',' TNG',' EAGLE',
             'numerical simulation','macroscopic simulation',
             'radiative transfer','hydrodynamical equation']

# flags for identifying lowz & local work
# I add more as I find them
local_things = ['differential radial velocities','differential radial velocity',
                'radial velocities','radial velocity',' AU.', ' AU,',' AU ',
                ' RV ','(RV)','(RVs)',' RVs ',' RV,','Galactic','LPV',
                'Large Magellanic Cloud','LMC','Milky Way',' NGC ','M33',
                'NGC ','polarisation','Polarisation','SDSS MaNGA',
                'Nova Remnant','nova remnant']
lowz_things = ['z < 1 ', 'z < 1.', r'z \sim 1.', 'z < 0.', 
               'z<1 ', 'z<1.', r'z\sim1.', 'z<0.',
               'low-redshift','low redshift','low-z','low z',
               'redshift < 1.','redshift < 1 ','redshift < 0.',
               'redshift of 1.','redshift of 1 ','redshift of 0.',
               'redshift range 0.']




# checking if lowz flags are in there
def check_lowz(abstract,key):
    if type(abstract) == str:
        filler = abstract.split(key) # will return a list
        yes = len(filler) > 1 # if key not in abstract, is false
        return int(yes), ' '.join(filler) # returns a string



# -- arXiv ID -- #
# -------------- #
items = posts.find_elements(By.TAG_NAME,'dt')
meta_infos = posts.find_elements(By.TAG_NAME,'dd')

# running through the posts to pull out arXiv ID
for i,item in enumerate(items):
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
    # print(f'https://arxiv.org/abs/{arxiv_id}')
    
    # title
    title = meta_info.find_element(By.CLASS_NAME,'list-title.mathjax').text
    
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


    # checking for JWST in title & abstract
    jwst_flag = False
    if 'jwst' in title.lower() or 'jwst' in new_abstract.lower():
        jwst_flag = True
        # title = '(_JWST_) ' + title

    # checking for highz language in title & abstract
    # but first removing z < 1 things
    lowz = 0
    for thing in local_things:
        isit,new_abstract = check_lowz(new_abstract,thing)
        lowz += isit

    for thing in lowz_things:
        isit,new_abstract = check_lowz(new_abstract,thing)
        lowz += isit
    
    # if lowz > 0: print('lowz',lowz)

    # after removing the lowz language, checking if a z is still there
    redshift = False
    if any(x in new_abstract for x in highz_flags) == True:
        redshift = True
        # title = 'z ' + title

    # checking if simulation paper
    sims = False
    if any(x in new_abstract for x in sim_flags) == True:
        sims = True

    # adding to end of dataframe
    # order, id, pri_category, mathjax, jwst, sim, z, title
    df.loc[len(df)] = [i, str(arxiv_id), primary_category, mathjax_flag,
                       jwst_flag, sims, redshift, title]
    
    # print(title)
    # # print('>'+new_abstract,end='\n\n')
    # print(f'arxiv.org/abs/{arxiv_id}',end='\n\n')

# ------------------------- #


# running through df for printing high-z first
jwst_high_z = df.query('jwst == True and z == True and sim == False').copy()
high_z = df.query('z == True and sim == False').copy()
high_z.drop(jwst_high_z.index.values,inplace=True) # removing the JWST ones

high_z_sim = df.query('z == True and sim == True').copy()


if len(jwst_high_z) > 0:
    print('''JWST-related high-z papers:
=======================''')
    for i in jwst_high_z.index.values:
        print(jwst_high_z.loc[i,'title'])
        print(f"arxiv.org/abs/{jwst_high_z.loc[i,'id']}",end='\n\n')

if len(high_z) > 0:
    print('''
    
non-JWST high-z papers:
=====================''')
    for i in high_z.index.values:
        print(high_z.loc[i,'title'])
        print(f"arxiv.org/abs/{high_z.loc[i,'id']}",end='\n\n')

if len(high_z_sim) > 0:
    print('''
    
high-z simulation papers:
=======================''')
    for i in high_z_sim.index.values:
        print(high_z_sim.loc[i,'title'])
        print(f"arxiv.org/abs/{high_z_sim.loc[i,'id']}",end='\n\n')













driver.close()






# NOT FOR DATALAB



# -- saving dataframe -- #
# ---------------------- #
tosave_df = df.astype(df_dtypes).copy() # to make sure column dtypes don't change

cat = pd.read_csv('arXiv_exgal.txt',sep='\t',dtype=df_dtypes)
final_df = pd.concat([cat.copy(),tosave_df.copy()])

final_df.drop_duplicates(inplace=True,subset='id') # in case it's been run already that day
final_df.to_csv('arXiv_exgal.txt',sep='\t',index=False)





sys.exit(0)































