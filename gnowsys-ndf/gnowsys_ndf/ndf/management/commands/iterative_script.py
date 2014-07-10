''' imports from installed packages '''
from django.core.management.base import BaseCommand, CommandError

from mongokit import IS

from django_mongokit import get_database

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

''' imports from application folders/files '''
from gnowsys_ndf.ndf.models import Node, GSystemType
from gnowsys_ndf.ndf.models import Group
from gnowsys_ndf.ndf.models import DATA_TYPE_CHOICES, QUIZ_TYPE_CHOICES_TU
from gnowsys_ndf.settings import GAPPS
from gnowsys_ndf.settings import META_TYPE
from gnowsys_ndf.factory_type import factory_gsystem_types, factory_attribute_types, factory_relation_types


import datetime
#from dateutil.parser import parse
from mongokit import Collection
from gnowsys_ndf.ndf.models import *

db = get_database()
collection = get_database()[GSystem.collection_name]
import csv
import os
import urllib2
import json
import pprint

from system_script2 import *
from log_script import *


#relative path of file
fn = os.path.join(os.path.dirname(__file__), '../../static/ndf/wikidata/list_of_objects')

log_flag = 0
gen_url_json="http://www.wikidata.org/wiki/Special:EntityData/"
gen_url_page="http://www.wikidata.org/wiki/"
language ="en" #this script is scalable and can be run for any given language .All relevant extracting functions will extract info in that language only.

commonsMedia_base_link="http://commons.wikimedia.org/wiki/File:" #link used to access the images 


#url="http://www.wikidata.org/wiki/Special:EntityData"
"""
def json_parse(url_json):
	'''
	The function extracts the json available at the url and returns it to the calling function.
	If the JSON is not found due to any reason like Network error JSON format error is thrown.
	'''
	js={}
	try:
		j = urllib2.urlopen(url_json)
		js = json.load(j)
	except (ValueError, KeyError, TypeError):
   		print "JSON format error"
	
	return js
"""


def json_parse(url_json):
	"""
	The function extracts the json available at the url and returns it to the calling function.
	If the JSON is not found due to any reason like Network error JSON format error is thrown.
	"""

	js={}
	try:
		j = urllib2.urlopen(url_json)
		js = json.load(j)
	except (ValueError, KeyError, TypeError):
   		print "JSON format error"
	
	return js


def extract_aliases(json_obj,topic_title,language_choice):
	"""
	Returns list of aliases extracted from the json object in the choice of language passed as a parameter.
	Parameters being passed to the function -
	1) json_obj - JSON for that item available at url of wikidata
	2)topic title- the item id /topic_id of an item like Q17 stands for Japan.
	3)language_choice - choice of language in which aliases are to be extracted

	"""


	alias_dict={}
	en_list=[]

	Result =json_obj['entities'][str(topic_title)]
	for k,v in Result.items():	
		if k =="aliases":
			alias_dict=v
	
	for key,value in alias_dict.items():
		if key == language_choice:
			for dict1 in value:
				for key1,value1 in dict1.items():
					if key1=="value":
						en_list.append(value1)

	return en_list  # returns a list of english aliases for the given item


def extract_labels(json_obj,topic_title,language_choice):
	"""
	Returns label extracted from the json object in the choice of language passed as a parameter.
	Parameters being passed to the function -
	1)json_obj - JSON for that item available at url of wikidata
	2)topic title- the item id /topic_id of an item like Q17 stands for Japan.
	3)language_choice - choice of language in which labels are to be extracted

	"""	

	Result =json_obj['entities'][str(topic_title)]
	for k,v in Result.items():	
		if k =="labels":
			label_dict=v
	
	
	#code to extract labels
	
	for key,val in label_dict.items():
		if key.startswith(language_choice)==True:
			for key1,val1 in val.items():
				if key1=="value":
					return val1 # returns an english label for the item
					


def extract_modified(json_obj,topic_title):
	"""
	Returns modified datetime extracted from the json object .
	Parameters being passed to the function -
	1)json_obj - JSON for that item available at url of wikidata
	2)topic title- the item id /topic_id of an item like Q17 stands for Japan.
	"""	
	Result =json_obj['entities'][str(topic_title)]
	for k,v in Result.items():
		if k=="modified":
			return v #return date time of last update of wiki data page but data type is still not clear



def extract_type(json_obj,topic_title):
	"""
	Returns datatype extracted from the json object.
	Parameters being passed to the function -
	1)json_obj - JSON for that item available at url of wikidata
	2)topic title- the item id /topic_id of an item like Q17 stands for Japan.
	"""	
	Result =json_obj['entities'][str(topic_title)]
	for k,v in Result.items():
		if k=="type":
			return v #return type of entity like say "item"

def extract_pageid(json_obj,topic_title):
	"""
	Returns pageid extracted from the json object .
	Parameters being passed to the function -
	1)json_obj - JSON for that item available at url of wikidata
	2)topic title- the item id /topic_id of an item like Q17 stands for Japan.
	"""	
	Result =json_obj['entities'][str(topic_title)]
	for k,v in Result.items():
		if k=="pageid":
			return v #return pageid of the item


def extract_namespace(json_obj,topic_title):
	"""
	Returns namespace extracted from the json object .There are 3 namespaces in wikidata - Items ,Properties and Queries
	Parameters being passed to the function -
	1)json_obj - JSON for that item available at url of wikidata
	2)topic title- the item id /topic_id of an item like Q17 stands for Japan.
	"""	
	Result =json_obj['entities'][str(topic_title)]
	for k,v in Result.items():
		if k=="ns":
			return v #return  namespace of the item

"""
def extract_claims(json_obj,topic_title):
	prop_dict={}
	Result =json_obj['entities'][str(topic_title)]
	for k,v in Result.items():	
		if k =="claims":
			prop_dict=v
			break

	if prop_dict!={}:
		for key,val in prop_dict.items():
    		url_prop= gen_url_json+key+".json"
    		#print url_prop

"""


def extract_descriptions(json_obj,topic_title,language_choice):
	"""
	Returns description extracted from the json object in the choice of language passed as a parameter.
	Parameters being passed to the function -
	1)json_obj - JSON for that item available at url of wikidata
	2)topic title- the item id /topic_id of an item like Q17 stands for Japan.
	3)language_choice - choice of language in which labels are to be extracted

	"""	
	description=""
	description_dict={}
	Result =json_obj['entities'][str(topic_title)]
	for k,v in Result.items():	
		if k =="descriptions":
			description_dict=v

	for key,value in description_dict.items():
		if key.startswith(language_choice):
			for key1,val1 in value.items():
				if key1=="value":
						description+=" - "+val1
	
	return description	
		

def extract_datatype_from_property(property_value_list):
	"""
	property_value_list is a list that has been extracted from the object's json
	This function returns the datatype of one particular property , that property whose value has been passed to this function as a list
	"""
	for element in property_value_list:
		if(type(element)) == type({}):
			for k,v in element.items():
				if k=="mainsnak":
					for k1,v1 in v.items():
						if k1=="datatype":
							return v1

def extract_from_property_value(property_value_list):
	"""
	property_value_list is a list that has been extracted from the object's json for any particular property.
	This function returns a flag value between 1,2 and 3.
	3-Showing that the property is to be created as a relation because "datatype" is "wikibase-item"
	2-Showing that the property is a globe-coordinate and hence the geo-json needs to be populated inside the
	 location filed."datatype" is "globe-coordinate". 
	1-Showing that the property is to be created as an attribute.

	"""
	for element in property_value_list:
		if(type(element)) == type({}):
			for k,v in element.items():
				if k=="mainsnak":
					for k1,v1 in v.items():
						if k1=="datatype":
							if v1=="wikibase-item":
								return 3  # RelationType and Relation will have to be created
							elif v1=="globe-coordinate" :
								return 2  # location field of the GSystemType will have to filled
							else:
								return 1 #all others for which AttributeType and Attributes will be created



def extract_property_value(property_value_list):
	"""
	property_value_list is a list that has been extracted from the object's json for any particular property.
	This function returns the exact value of a property for a particular item . Frequently the returned value may be a dictionary.
	"""
	for element in property_value_list:
		if(type(element)) == type({}):
			for k,v in element.items():
				if k=="mainsnak":
					for k1,v1 in v.items():
						if k1=="datavalue":
							for k2,v2 in v1.items():
								if k2=="value":
									return v2


def extract_value_for_relation(property_value_list):
	"""
	This function is called exclusively while creating Relations.property_value_list is a list that has been extracted from the object's json
	for any particular property.
	This function returns the wikibase numeric id of the right subject of the relation. 
	"""

	for element in property_value_list:
		if(type(element)) == type({}):
			for k,v in element.items():
				if k=="mainsnak":
					for k1,v1 in v.items():
						if k1=="datavalue":
							for k2,v2 in v1.items():
								if k2=="value":
									for k3,v3 in v2.items():
										if k3=="numeric-id":
											return v3


def property_create_AttributeType(property_id, property_data_type, json_obj, call_flag):
	"""
	This function receives the following parameters-
	1)property_id -The id by which this property is referred in wikidata.eg - P31 -instance of etc
	2)property_data_type -The datatype of the property eg - unicode
	3)json_obj - actually the json of the property.
	This function extracts useful information from the property_json like label ,description etc and then calls the create_AttributeType function of system_script2.
	Meanwhile the suitable entries are being made into the log file as well.

	Call flag - Decides which iteration it is and which method of system_script2 needs to be called.
		1 - iteration 1
	"""
	if(json_obj):
		property_alias_list=extract_aliases(json_obj,property_id,language)
		property_label =extract_labels(json_obj,property_id,language)
		property_description =extract_descriptions(json_obj,property_id,language)
		property_last_update =extract_modified(json_obj,property_id)
		property_entity_type =extract_type(json_obj,property_id)
		property_namespace =extract_namespace(json_obj,property_id)
		attribute_type_exists = False
		if call_flag == int(1):
			attribute_type_exists = create_AttributeType_for_class(property_label, property_data_type,property_description,property_id,language, user_id)
		else:
			attribute_type_exists = create_AttributeType(property_label, property_data_type,property_description,property_id,language, user_id)		
		
		if attribute_type_exists:
			log_attributeType_exists(property_label, log_flag)
		else:
			log_attributeType_created(property_label, log_flag)

		



def property_create_Attribute(label,property_id,property_value,property_json):
	"""
	This function receives the following parameters-
	1)label -The label of the item for which the attribute is being created.eg -"Japan is a country".Japan is the label
	2)property_id - The id by which the property is referred to in wikidata.
	3)property_value - The value of that attribute that is the third part of any triplet.
	4)property_json - The json of the property for which the attribute is being made.This json too is extracted 
	from its wikidata url.
	This function first ensures that any attribute with image in its name has a commonsmedia url stored as a value.
	It then calls create_Attribute function of system_script2 appropriately.

	Meanwhile suitable messages are being written in the log files as well depending on wether the attribute exists
	 before hand or not.

	"""	
	property_label =extract_labels(property_json,property_id,language)
	if 'image' in property_label:
		property_value=	commonsMedia_base_link+property_value
		property_value=property_value.replace(" ","_")

	attribute_exists = create_Attribute(label, property_label, property_value, language, user_id)
	if attribute_exists:
        	log_attribute_exists(property_label, log_flag)
        else:
                log_attribute_created(property_label, log_flag)



def property_create_RelationType(property_id,property_json, call_flag):
	"""	
	This function receives the following parameters-
	1)property_id -The id by which this property is referred in wikidata.eg - P31 -instance of etc
	2)property_json - json of the property.
	This function extracts useful information from the property_json like label and then calls  the create_RelationType function of system_script2.
	Meanwhile the suitable entries are being made into the log file as well.
	"""
	property_label = extract_labels(property_json,property_id,language)
	inverse_name="-"+property_label
	
	if call_flag == int(1):
		#Iteration 1 - creating classes
		relation_type_exists = create_RelationType(property_label, inverse_name, "WikiData", "WikiData",property_id,language, user_id)
	else:
		#Iteration 3 - creating acual relations between topics.
		relation_type_exists = create_RelationType(property_label, inverse_name, "WikiTopic", "WikiTopic",property_id,language, user_id)

	if relation_type_exists:
        	log_relationType_exists(property_label, log_flag)
       	else:
        	log_relationType_created(property_label, log_flag)





def property_create_Relation(label,property_id,property_value,property_json):
	"""
	This function receives the following parameters-
	1)label -The label of the item for which the attribute is being created.eg -"Japan is a country".Japan is the label
	2)property_id - The id by which the property is referred to in wikidata.
	3)property_value - The value of that attribute that is the third part of any triplet.
	4)property_json - The json of the property for which the attribute is being made.This json too is extracted 
	from its wikidata url.
	Function checks that the right subject name must exist as a GSystem or a GsystemType i.e. it only creates a relation if there
	exists an object with name as right_subject_name.
	Function calls create_Relation function of system_script2 appropriately.

	Meanwhile suitable messages are being written in the log files as well depending on wether the relation exists
	 before hand or not.

	"""	
	property_label=extract_labels(property_json,property_id,language)
	property_value =unicode("Q")+unicode(property_value)
	right_json_url=gen_url_json+str(property_value)+".json"

	print property_id+"%%%%%%%%%%%%%%",right_json_url
	right_json=json_parse(right_json_url) #property_value is supposed to be the id of the right subject in case of a relation

	right_subject_name=extract_labels(right_json,property_value,language)
	print "$$$$$$$$",right_subject_name," ",property_value
	log_inner_topic_start(log_flag)
	if right_subject_name!=None:
		#initiate_new_topic_creation(right_json,property_value,language)
		if item_exists(right_subject_name):
			log_inner_topic_end(log_flag)
			relation_exists = create_Relation(label, property_label, right_subject_name, user_id)
		
			if relation_exists :
        			log_relation_exists(property_label, log_flag)
        
        
        		else:
	        		log_relation_created(property_label, log_flag)

        	else:
			print "The right subject does not exist at all"

	else:
		print "*****the right subject is not an item of english, is not supposed to be created*****"
		#create a log function



def class_create(class_id, class_json):
	label = extract_labels(class_json, class_id, language)
	alias_list = extract_aliases(class_json, class_id, language)
	description = extract_descriptions(class_json, class_id, language)
	last_update = extract_modified(class_json, class_id)
	entity_type = extract_type(class_json, class_id)
	page_id =extract_pageid(class_json, class_id)
	namespace =extract_namespace(class_json, class_id)
	
	if label!= None:
		global log_flag
		class_exists = create_Class(label, description, alias_list, class_id, None, int(1))
		if class_exists:	
			log_class_exists(label, log_flag)
		else:
			log_class_created(label, log_flag)
			#Creating all the Attributes for class
			extract_property_json(class_json, label, class_id, int(1))
			


def initiate_class_creation(json_obj,label,topic_title,call_flag):
	"""	
	This function receives the following parameters-
	1)json_obj -The json of the item for which attributes and relations are to be created.
	2)label -The label of the item for which claims will be parsed and attributes and relations will be made. 
	3)topic_title - The topic_title of the item . eg - Q17 stands for Japan.
	4)call_flag - shows wether the function is being called first time or second time for a particular object.
		-In the first iteration the call_flag=1 and only the topic,attributetypes and attributes must be created.
		-In the second iteration the call_flag=2 and the relationtypes and relations must be created.

	The function is responsible for parsing the json of any item and then creating attributes and relations 
	depending on the value of flag and call_flag.
	The tags are also being populated as and when the property_id is either P279 or P31.
	P31 - instance of
	P279 - subclass of
	"""
	claim_dict={}
	Result =json_obj['entities'][str(topic_title)]

	for k,v in Result.items():	
		if k =="claims":
			claim_dict=v


	for k,v in claim_dict.items():
		property_id = k
		property_json_url =gen_url_json+property_id+".json"
		property_json =json_parse(property_json_url)
		property_value_list =v
		flag=-1
		flag=extract_from_property_value(property_value_list)
		property_value =extract_property_value(property_value_list) #property_value has the value of that property for a particular object
		print "Property Id: " + str(property_id)		
		print "Property Value: " + unicode(property_value) 
		
		global log_flag
		log_flag += 1
		
		if property_id == "P31":
			print "Property Value" + str("!!!!!!!!!!!!!!!!!!!--------------------!!!!!!!!!!!!!") + str(property_value)
			for key, val in property_value.items():
				if key == u'numeric-id':
					class_id = "Q" + str(val)
					class_url = gen_url_json+class_id+".json"
					class_json =json_parse(class_url)
					print class_url + str("this is the class iD!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!------------=====================================")
					class_create(class_id, class_json)	
					
	
		log_flag -= 1
		"""	
		if flag==1 and call_flag==1: #attribute has to be made
			property_data_type = extract_datatype_from_property(property_value_list)
			#print topic_title," ",property_id," ",label," - ",property_data_type ," :",property_value
			#print property_data_type

			property_create_AttributeType(property_id,property_data_type,property_json) #assuming that the name of the attribute type id the property id like say P131
			property_create_Attribute(label,property_id,property_value,property_json) #entire triple is being passed as a parameter
		
		
		if flag==3 and call_flag==2: #relation has to be made
			
			property_value_for_relation=extract_value_for_relation(property_value_list)
			
			property_create_RelationType(property_id,property_json)
			property_create_Relation(label,property_id,property_value_for_relation,property_json)
			
			
		
			if property_id=="P31" or property_id=="P279":
				print "^^entering tags^^ ",label, " - ",property_value_for_relation	
				property_value_for_relation=unicode("Q")+unicode(property_value_for_relation)
				property_value_json=gen_url_json+str(property_value_for_relation)+".json"
				property_value_json=json_parse(property_value_json) #property_value is supposed to be the id of the right subject in case of a relation
				property_value_name=extract_labels(property_value_json,property_value_for_relation,language)			
				populate_tags(label,property_value_name)
			
		"""


		
def extract_property_json(json_obj,label,topic_title,call_flag):
	"""	
	This function receives the following parameters-
	1)json_obj -The json of the item for which attributes and relations are to be created.
	2)label -The label of the item for which claims will be parsed and attributes and relations will be made. 
	3)topic_title - The topic_title of the item . eg - Q17 stands for Japan.
	4)call_flag - shows wether the function is being called first time or second time for a particular object.
		-In the first iteration the call_flag=1 and only the topic,attributetypes and attributes must be created.
		-In the second iteration the call_flag=2 and the relationtypes and relations must be created.

	The function is responsible for parsing the json of any item and then creating attributes and relations 
	depending on the value of flag and call_flag.
	The tags are also being populated as and when the property_id is either P279 or P31.
	P31 - instance of
	P279 - subclass of
	"""
	claim_dict={}
	Result =json_obj['entities'][str(topic_title)]

	for k,v in Result.items():	
		if k =="claims":
			claim_dict=v


	for k,v in claim_dict.items():
		property_id = k
		property_json_url =gen_url_json+property_id+".json"
		property_json =json_parse(property_json_url)
		property_value_list = v
		flag=-1
		flag=extract_from_property_value(property_value_list)
		property_value =extract_property_value(property_value_list) #property_value has the value of that property fpr a particular object
		global log_flag
		log_flag += 1

		if flag==1 and call_flag==1: #attribute has to be made
			print "Attempting to create an Attribute for Iteration1"			
			property_data_type = extract_datatype_from_property(property_value_list)
			#print topic_title," ",property_id," ",label," - ",property_data_type ," :",property_value
			#print property_data_type
			property_create_AttributeType(property_id,property_data_type,property_json, call_flag) #assuming that the name of the attribute type id the property id like say P131
			property_create_Attribute(label,property_id,property_value,property_json) #entire triple is being passed as a parameter
		
		if flag==3 and call_flag==1: #attribute has to be made
			print "Attempting to create an Relation for Iteration1"
			if property_id == "P279":
				"""
				Code to call DFS.
				"""
				print "DFS Will be starting here"
			
				print "Property Value" + str("!!!!!!!!!!!!!!!!!!!--------------------!!!!!!!!!!!!!") + str(property_value)
				for key, val in property_value.items():
					if key == u'numeric-id':
						class_id = "Q" + str(val)
						class_url = gen_url_json+class_id+".json"
						class_json =json_parse(class_url)

				url_json = gen_url_json+class_id+".json"	#creating url of json by appending words to it to make a proper link
				url_page = gen_url_page+class_id #creating url of the wikidata page itself
				json_obj = json_parse(url_json)
				if(json_obj):
					global log_flag
					log_flag += 1
					label = extract_labels(json_obj,class_id,language)
					initiate_class_creation(json_obj,label,class_id,int(1))
					log_class_done(log_flag)
					log_flag -= 1

				
				
			else:
				property_value_for_relation=extract_value_for_relation(property_value_list)
			
				property_create_RelationType(property_id,property_json, call_flag)
				property_create_Relation(label,property_id,property_value_for_relation,property_json)
		
		
		if flag==3 and call_flag==2: #relation has to be made
			
			property_value_for_relation=extract_value_for_relation(property_value_list)
			
			property_create_RelationType(property_id,property_json)
			property_create_Relation(label,property_id,property_value_for_relation,property_json)
			
			log_flag -= 1
		
			if property_id=="P31" or property_id=="P279":
				print "^^entering tags^^ ",label, " - ",property_value_for_relation	
				property_value_for_relation=unicode("Q")+unicode(property_value_for_relation)
				property_value_json=gen_url_json+str(property_value_for_relation)+".json"
				property_value_json=json_parse(property_value_json) #property_value is supposed to be the id of the right subject in case of a relation
				property_value_name=extract_labels(property_value_json,property_value_for_relation,language)			
				populate_tags(label,property_value_name)
			
			

def create_topic_id():
	"""
	This function is just called once , directly from main so that the topic_id is created as a AttributeType
	"""

	attribute_type_name ="topic_id"
	attribute_type_data_type ="unicode"
	user_id =int(1)
	create_AttributeType(attribute_type_name, attribute_type_data_type,"_id referred in Wikidata","topic_id","en", user_id)
	


def initiate_new_topic_creation(json_obj,topic_title,language_choice):
	"""
	Parameters being passed to the function -
	1)json_obj - JSON for that item available at url of wikidata
	2)topic title- the item id /topic_id of an item like Q17 stands for Japan.
	3)language_choice - choice of language .

	"""
	alias_list=extract_aliases(json_obj,topic_title,language_choice)
	label=extract_labels(json_obj,topic_title,language_choice)	
	description =extract_descriptions(json_obj,topic_title,language_choice)
	last_update =extract_modified(json_obj,topic_title)
	entity_type =extract_type(json_obj,topic_title)
	page_id =extract_pageid(json_obj,topic_title)
	namespace =extract_namespace(json_obj,topic_title)
	global log_flag
	log_flag += 1

	if label!=None:
		topic_exists = create_Topic(label, description, alias_list, topic_title, None, int(1))
		if topic_exists== True:
			log_topic_exists(label, log_flag)
		if topic_exists == False:
			log_topic_created(label, log_flag)
			create_Attribute(label, "topic_id", topic_title, language, user_id)
			extract_property_json(json_obj,label,topic_title,1)


def iteration_1():
	"""
	Parameter passed to the function is flag.
	If -
		flag=1 -The first iteration.Only the topic and its attributetyeps and attributes are supposed to be created.
		flag=2 -The second iteration.The topic and its attributes already exist , now its relationTypes 
		and relations are to be created.

	Function called directly from main.This function starts reading a file with name of items .Now depending on 
	the value of flag it knows wether the script is in first iteration or second iteration.
	In the first iteration.Only the topic and its attributetyeps and attributes are supposed to be created.
	In the second iteration.The topic and its attributes already exist , now its relationTypes 
		and relations are to be created.

	"""
	with open(fn,'rb') as f:
		r = csv.reader(f,delimiter ='\n')
		for row in r:
			for topic_title in row:
				if topic_title.startswith('Q')==True: #first line of wiki file has some metadata
					url_json = gen_url_json+topic_title+".json"	#creating url of json by appending words to it to make a proper link
					url_page = gen_url_page+topic_title #creating url of the wikidata page itself
					json_obj = json_parse(url_json)
					if(json_obj):
						global log_flag
						log_flag = 0
						label = extract_labels(json_obj,topic_title,language)
						initiate_class_creation(json_obj,label,topic_title,int(1))
						log_class_done(log_flag)

					else:
						print "empty json returned"
						continue


def read_file(flag):
	"""
	Parameter passed to the function is flag.
	If -
		flag=1 -The first iteration.Only the topic and its attributetyeps and attributes are supposed to be created.
		flag=2 -The second iteration.The topic and its attributes already exist , now its relationTypes 
		and relations are to be created.

	Function called directly from main.This function starts reading a file with name of items .Now depending on 
	the value of flag it knows wether the script is in first iteration or second iteration.
	In the first iteration.Only the topic and its attributetyeps and attributes are supposed to be created.
	In the second iteration.The topic and its attributes already exist , now its relationTypes 
		and relations are to be created.

	"""
	with open(fn,'rb') as f:
		r = csv.reader(f,delimiter ='\n')
		for row in r:
			for topic_title in row:
				if topic_title.startswith('Q')==True: #first line of wiki file has some metadata
					url_json= gen_url_json+topic_title+".json"	#creating url of json by appending words to it to make a proper link
					url_page=gen_url_page+topic_title #creating url of the wikidata page itself
					json_obj=json_parse(url_json)
					if(json_obj):
						global log_flag
						log_flag = 0
						if flag==1:
							initiate_new_topic_creation(json_obj,topic_title,language)
							log_outer_topic(log_flag)
						else:
							label=extract_labels(json_obj,topic_title,language)
							extract_property_json(json_obj,label,topic_title,int(1))

					else:
						print "empty json returned"
						continue


class Command(BaseCommand):
	def handle(self, *args, **options):
		"""
		First create the GSystemType WikiTopic.
		Then  create the GAttributeType topic_id.
		read_file(int(1)) - starts the first iteration.
		Then read_file(int(2)) -starts the second iteration.
		"""
		create_WikiData_WikiTopic()
		
		create_topic_id()
		log_iteration_1_file_start()
		iteration_1()	
		log_iteration_1_file_complete()
		#iteration_2()
		#iteration_3()
		#read_file(int(1))		# read the file with list of items starting with Q
		#read_file(int(2))		

		

