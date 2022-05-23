# Import packages necessary for these functions
from Bio import Entrez
import urllib
from xmljson import yahoo as yh
from xml.etree.ElementTree import fromstring
import numpy as np
from copy import deepcopy

def get_abstract(pmid):
    handle = Entrez.efetch(db='pubmed', id=pmid, retmode='xml', retmax=4000, rettype='abstract')
    return handle.read()

def get_info():
    email = input('Please provide email address: ')
    return email

def findformat_abstract(terms):
    new_abstracts = {}
    Entrez.email = get_info()
    for term in terms:
        try:
            pub_handle = Entrez.esearch(db = "pubmed", term=term, retmax=4000,sort="relevance", retmode = "xml")
            pub_record = Entrez.read(pub_handle)
            pub_id = pub_record["IdList"]
            abstracts= get_abstract(pub_id)
            y_abstracts = yh.data(fromstring(abstracts))
            try:
                format_abstracts = y_abstracts['PubmedArticleSet']['PubmedArticle']
                for ref_data in (format_abstracts):
                    ref_medline_citation = ref_data['MedlineCitation']
                    ref_pubmeddata = ref_data['PubmedData']['ArticleIdList']['ArticleId']
                    pmid = ref_medline_citation['PMID']['content']
                    journal = ref_medline_citation['Article']['Journal']['Title']
                    title = ref_medline_citation['Article']['ArticleTitle']
                    authors = ref_medline_citation['Article']['AuthorList']['Author']
                    try:
                        pmc = [each_id['content'] for each_id in ref_pubmeddata if each_id['IdType']=='pmc']
                        doi = [each_id['content'] for each_id in ref_pubmeddata if each_id['IdType']=='doi']
                    except:
                        pass
                    names = []
                    if not isinstance(authors,list):
                        authors=[authors,]
                    for item in authors:
                        names.append(item.get('LastName',"")+ ' '+ item.get('ForeName',"") + ' ' + item.get('Initials',""))
                    mesh = []
                    try:
                        headings = ref_medline_citation['MeshHeadingList']['MeshHeading']
                        for item2 in headings:
                            mesh.append(item2['DescriptorName']['content'])
                    except KeyError:
                        mesh = "NONE"
                    try:
                        abstract = ref_medline_citation['Article']['Abstract']['AbstractText']
                    except KeyError:
                        abstract = "NONE"
                    try:
                        month = ref_medline_citation['Article']['ArticleDate']['Month']
                        day = ref_medline_citation['Article']['ArticleDate']['Day']
                        year = ref_medline_citation['Article']['ArticleDate']['Year']
                        date =  month,day,year
                    except KeyError:
                        date = "NONE"
                    if pmid in new_abstracts:
                         new_abstracts[pmid]['Search Terms'].append(term)
                    else:
                         new_abstracts[pmid] = {'Search Terms': [term], 'DOI': doi, 'PMC': pmc,'Date': date, 'Authors':names, 'Journal':journal, 'Title':title, 'Abstract':abstract,'MESH':mesh, 'Methods': [], 'Results':[], 'fit_main_keywords':[]}
            except (KeyError, TypeError):
                continue
        #except (HTTPError): #Python2
        except urllib.error.HTTPError:
            sleep(10)
    return new_abstracts


def getTexts(pmc_abstract):
    '''find open access files, extract results and methods sections and convert xml to json format'''
    for k, v in deepcopy(pmc_abstract).items():
        pmc = pmc_abstract[k]['PMC']
        if len(pmc)>0:
            pmc_idno =(s.strip('PMC') for s in v['PMC'])
            #confirm that file is Open Access
            try_this = pmc_abstract[k]['PMC']
            find_pdf = "https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id={}".format(*try_this)
            #get xml record
            url = "https://www.ncbi.nlm.nih.gov/pmc/oai/oai.cgi?verb=GetRecord&identifier=oai:pubmedcentral.nih.gov:{}&metadataPrefix=pmc".format(*pmc_idno)
            pmc_abstract[k]['OA web address'] = url
            with urllib.request.urlopen(find_pdf) as response:
                the_file = response.read().decode('utf-8')
                dict_file = xmltodict.parse(the_file)
    
                try:
                    pmc_abstract['ftp_record'] = dict_file['OA']['records']['record']['link']['@href']
                except KeyError:
                    pmc_abstract['ftp_record'] = dict_file['OA']['error']['#text']
                except TypeError:
                    pmc_abstract['ftp_record'] = dict_file['OA']['records']['record']

            with urllib.request.urlopen(url) as responsec:
                the_filec = responsec.read().decode('utf-8')
                dict_filec = xmltodict.parse(the_filec)
         
                try:
                    data_level = dict_filec['OAI-PMH']['GetRecord']['record']['metadata']['article']['body']['sec']

                    methods = []
                    for m_level in data_level:
                        if type(m_level['title']) == str:
                            if m_level['title'].lower() in {'materials and methods','experimentalprocedures','experimental procedures','materialsandmethods', 'methods', 'method'}:
                                methods.append(m_level['sec'])
                        else:
                            methods = m_level['title']['ETHODS']

                    results = [r_level['sec'] for r_level in data_level if r_level['title'].lower()=='results']
                    pmc_abstract[k]['Methods'] = methods
                    pmc_abstract[k]['Results'] = results
                except (KeyError, TypeError):
                    continue            

    return pmc_abstract
