#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -------------------------
# (c) kelu124
# cc-by-sa/4.0/
# -------------------------
# Requires GraphViz and Wand
# -------------------------

'''Description: script to build autodocumentation. module for autodocumentation generation.'''

__author__      = "kelu124"
__copyright__   = "Copyright 2016, Kelu124"
__license__ 	= "cc-by-sa/4.0/"

import os
from glob import glob
import markdown
import re
import graphviz as gv
import functools
# Wand for SVG to PNG Conversion
from wand.api import library
import wand.color
import wand.image
import Image
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from bs4 import BeautifulSoup
import urllib2


# -------------------------
# Get icons for compiler log
# -------------------------

tagAuto = "[](@autogenerated - invisible comment)"
tagDesc = "[](@description"
log = []
GreenMark = ":white_check_mark:"
RedMark = ":no_entry:"
WarningMark = ":warning:"
ValidH = ["h1","h2","h3","h4","h5"]

ModulesChaptDeux = ["tobo","retroATL3","mogaba","goblin","tobo","toadkiller"]
ModulesChaptTrois = ["silent","cletus","croaker","doj","sleepy","oneeye"]

ListOfMurgenSessions = ["Session_1.md","Session_2.md","Session_3.md","Session_4.md","Session_4b.md","Session_5.md","Session_6.md","Session_7.md","Session_8.md","Session_9_ATL.md",]

ExcludeDirs = ["include","tools",".git","gh-pages","doc","gitbook","bomanz"]
ExcludeDirsRetired = ExcludeDirs+["retired"]


# -------------------------
# Graph customised
# -------------------------

styles = {
    'graph': {
        'label': 'my mind',
	'layout':"neato",
	'fontsize':"26",
	'outputorder':'edgesfirst',
	#"overlap":"false",
        'rankdir': 'BT',
    }
}


# -------------------------
# Aide pour le graphe
# -------------------------

graph = functools.partial(gv.Graph, format='svg')
digraph = functools.partial(gv.Digraph, format='svg')

def Svg2Png(svgfile):
	output_filename = svgfile+'.png'
	input_filename = svgfile+'.svg'

	svg_file = open(input_filename,"r")

	with wand.image.Image() as image:
	    with wand.color.Color('transparent') as background_color:
		library.MagickSetBackgroundColor(image.wand, background_color.resource) 
	    image.read(blob=svg_file.read())
	    png_image = image.make_blob("png32")

	with open(output_filename, "wb") as out:
	    out.write(png_image)

def apply_styles(graph, styles):
    graph.graph_attr.update(
        ('graph' in styles and styles['graph']) or {}
    )
    graph.node_attr.update(
        ('nodes' in styles and styles['nodes']) or {}
    )
    graph.edge_attr.update(
        ('edges' in styles and styles['edges']) or {}
    )
    return graph

# -------------------------
# Get Murgen Stats
# -------------------------

def GetMurgenStats():
	MurgenURL = "https://hackaday.io/project/9281-murgen-open-source-ultrasound-imaging"
	page = urllib2.urlopen(MurgenURL)
	soup = BeautifulSoup(page.read())
	print soup.find_all("div","section-profile-stats")[0]
#div content-left section-profile-stats

# -------------------------
# Gestion des modules
# -------------------------


def GetListofModules(dirname):
	ListOfDirs = os.listdir(dirname)  
	ModulesDirs = []
	for f in ListOfDirs:
		if  os.path.isdir(dirname+"/"+f):
			ModulesDirs.append(f)
	# On retire les repertoires non modules
	if ("retired" not in dirname):
		f = [x for x in ModulesDirs if x not in ExcludeDirsRetired]
	else:
		f = [x for x in ModulesDirs if x not in ExcludeDirs]
	return f

def getText(path):
	f = open(path,'r')
	text = f.read()+"\n"
	text.replace(tagAuto,"")
	f.close()
	return text

def returnSoup(path):
	f = open(path, 'r')
	RawHTML=markdown.markdown( f.read() )
	f.close()
	return [BeautifulSoup(RawHTML,"lxml"),RawHTML]

def getHs(soupH,h,hText):
	Text = BeautifulSoup("", "lxml")
	if (h in ValidH):
		allH = soupH.find_all(h)
		for H in allH:
			if hText in H:
 				nextSib = H.find_next(True)
   				while nextSib is not None and h not in nextSib.name :
 
					Text.append(nextSib)
					#print nextSib.text
               				nextSib = nextSib.nextSibling
	return Text

def returnHList(soup,h,hText):
	ListItem = []
	if (h in ValidH):
		desch3 = soup.find_all(h)
		for H in desch3:
			if hText in H.text:
			    for item in H.find_next("ul").find_all("li"):
				ListItem.append(item)
	else:
		print "H Error"
	return ListItem

def getCode(string):
	ListOfCodes = []
	for item in string.find_all("code"):
		ListOfCodes.append(item.text)
	return ListOfCodes

# -------------------------
# Preparing gitbook
# -------------------------

def GitBookizeModule(s,module):
	t = s.split("\n## ")
	del t[1]
	titreModule = t[1]
	titreModule = titreModule.replace("\n","").replace("Title","")
	del t[1]
	del t[1]
	del t[1]
	del t[1]
	#del t[-1]
	del t[-1]
	del t[0]	
	joiner = "\n## "
	u = joiner.join(t)
	u = "## "+u.replace("![Block schema](source/blocks.png)","![Block schema](https://raw.githubusercontent.com/kelu124/echomods/master/"+module+"/source/blocks.png)")
	HeaderModule = "# "+titreModule+ "\n\n## What does it look like? \n\n <img src='https://raw.githubusercontent.com/kelu124/echomods/master/"+module+"/viewme.png' align='center' width='150'>\n\n"
	u = HeaderModule+ u
	return u


def SearchString(s, leader, trailer):
  end_of_leader = s.index(leader) + len(leader)
  start_of_trailer = s.index(trailer, end_of_leader)
  return s[end_of_leader:start_of_trailer]

def AddOneLevel(s):
	return s.replace("# ", "## ")

def AddTwoLevels(s):
	return s.replace("# ", "### ")

def WorkLogLevel(s):
	return s.replace("#### ", "## ")

def IncludeImage(s):
	return s.replace("<img src='https://github.com/kelu124/echomods/blob/master/", "<img src='https://raw.githubusercontent.com/kelu124/echomods/master/")

def AddRawHURL(s):
	BaseURL = "https://kelu124.gitbooks.io/echomods/content"
	URL = "https://raw.githubusercontent.com/kelu124/echomods/master/"
	for moduledeux in ModulesChaptDeux:
		s = s.replace("](/"+moduledeux+"/)", "]("+BaseURL+"/Chapter2/"+moduledeux+".md)")	
		s = s.replace("](/"+moduledeux+"/source/blocks.png)", "](https://raw.githubusercontent.com/kelu124/echomods/master/"+moduledeux+"/source/blocks.png)")	
		s = s.replace("](/"+moduledeux+"/Readme.md)", "]("+BaseURL+"/Chapter2/"+moduledeux+".md)")
	for moduletrois in ModulesChaptTrois:
		s = s.replace("](/"+moduletrois+"/)", "]("+BaseURL+"/Chapter3/"+moduletrois+".md)")	
		s = s.replace("](/"+moduletrois+"/Readme.md)", "]("+BaseURL+"/Chapter3/"+moduletrois+".md)")
		s = s.replace("](/"+moduletrois+"/source/blocks.png)", "](https://raw.githubusercontent.com/kelu124/echomods/master/"+moduletrois+"/source/blocks.png)")	

	s = s.replace("![](/", "![]("+URL)


	return s

def AddRawMurgenURL(s):
	ListOfMurgenSessions = ["Session_1.md","Session_2.md","Session_3.md","Session_4.md","Session_4b.md","Session_5.md","Session_6.md","Session_7.md","Session_8.md","Session_9_ATL.md",]
	BaseURL = "https://kelu124.gitbooks.io/echomods/content"
	URL = "https://raw.githubusercontent.com/kelu124/murgen-dev-kit/master/"
	for Session in ListOfMurgenSessions:
		s = s.replace("](/worklog/"+Session+")", "]("+BaseURL+"/Chapter4/"+Session+")")	
	s= re.sub('!\[.*\]', '![]', s)
	return s.replace("![](/", "![]("+URL)


def OpenWrite(Write,Open):
	f = open(Open,"w+")
	f.write(Write+"\n"+tagAuto)
	return f.close()

def CopyFile(From,To):
	return OpenWrite(getText(From),To)

def CopyGitBookFile(From,To):
	result = []
	with open("./"+From) as FileContent:
		for line in FileContent:
			i = 0
			result.append(line)
	return OpenWrite(AddRawHURL("".join(result)),To)

def CopyGitBookMurgenFile(From,To):
	return OpenWrite(AddRawMurgenURL(getText(From)),To)

def GraphModule(Paires,GraphThisModule,ReadMe,FullSVG):
        for eachPair in Paires:
	    eachPair = eachPair.text
	    if ("->" in eachPair):
	   	Couples = eachPair.split("->")
		for single in Couples:
		    GraphThisModule.node(single, style="rounded")
		# Add the edge		
		for k in range(len(Couples)-1):
		    GraphThisModule.edge(Couples[k], Couples[k+1])
	if FullSVG:
		GraphThisModule.render(ReadMe+'/source/blocks')
		Svg2Png(ReadMe+'/source/blocks')


# -------------------------
# Check update suppliers
# -------------------------

def GetSuppliersList(path):
	results = [y for x in os.walk(path) for y in glob(os.path.join(x[0], 'sup*.md'))]
	Text = ""
	for eachSupplier in results:
		[soup,ReadMehHtmlMarkdown] = returnSoup(eachSupplier)
		#print getParam(ReadMe,"ds")
		Infos = returnHList(soup,"h3","Info")
		NameSupplier = ""
		SiteSupplier = ""
		for info in Infos:
			if "Name:" in info.text:
				NameSupplier = info.text.replace("Name:", "").strip()
			if "Site:" in info.text:
				SiteSupplier = info.text.replace("Site:", "").strip()
		Text += "\n* ["+NameSupplier+"]("+SiteSupplier+"): "
		Status = returnHList(soup,"h3","Status")
		for status in Status:
			Text += status.text.replace("</li>", "").replace("<li>", "")+", "
	Text += "\n\n"

	return Text	

# -------------------------	
# Check auto-files
# Check other files
# -------------------------

def GetGeneratedFiles(path):
	ManualFiles = []
	ManualDesc = []
	AutoFiles = []
	log = []
	results = [y for x in os.walk(path) for y in glob(os.path.join(x[0], '*.md'))]
	ExcludeDirs = ["tools",".git","gh-pages","doc","retired"]
	f = [x for x in results if x.split("/")[1] not in ExcludeDirs]
	for eachMd in f:
		Desc = ""
		with open(eachMd) as FileContent:
			found = False
			foundDesc= False
			for line in FileContent:  #iterate over the file one line at a time(memory efficient)
			    if tagAuto in line:
				found = True
			    if tagDesc in line:
				foundDesc = True
				start = '\[\]\(@description'
				end = '\)'
				Desc = re.search('%s(.*)%s' % (start, end), line).group(1).strip()

				#  Pitch/Intro of the project)
			if not found:
				ManualFiles.append(eachMd)
				ManualDesc.append(Desc)	
			else: 
				AutoFiles.append(eachMd)
			if (not found) and (not foundDesc):
				log.append("__[MD Files]__ "+RedMark+" `"+eachMd+"` : Missing description")

	#AutoFiles.sort()
	#ManualFiles.sort()
	return [AutoFiles,ManualFiles,ManualDesc,log]

def GetPythonFiles(path):
	results = [y for x in os.walk(path) for y in glob(os.path.join(x[0], '*.py'))]
	ExcludeDirs = ["tools",".git","gh-pages"] 
	PythonFilesList = [x for x in results if x.split("/")[1] not in ExcludeDirs]
	return PythonFilesList

def GetInoFiles(path):
	results = [y for x in os.walk(path) for y in glob(os.path.join(x[0], '*.ino'))]
	ExcludeDirs = ["tools",".git","gh-pages"] 
	InoFiles = [x for x in results if x.split("/")[1] not in ExcludeDirs]

	return InoFiles

def GetPptFiles(path):
	results = [y for x in os.walk(path) for y in glob(os.path.join(x[0], 'ppt_*.md'))]
	ExcludeDirs = ["tools",".git","gh-pages"] 
	PptFiles = [x for x in results if x.split("/")[1] not in ExcludeDirs]

	return PptFiles

def CheckPythonFile(files):
	## See http://stackoverflow.com/questions/1523427/what-is-the-common-header-format-of-python-files for an idea 
	log = []
	PythonDesc = []
	for PythonFile in files:
		with open(PythonFile) as f:
		    lN = 0
		    moduleDesc = ""
		    # Description, author, copyright, license
		    ErrorConditions = [True, True, True, True]
		    for line in f:
			if (lN == 0) and ("#!/usr/bin/env python" not in line):
				log.append("__[Python]__ "+RedMark+" `"+PythonFile+"` : Header error ")
			if ("__author__") in line:
				ErrorConditions[1]=False
			if ("__copyright__") in line:
				ErrorConditions[2]=False
			if ("__license__") in line:
				ErrorConditions[3]=False
			if ("'''Description") in line:
				ErrorConditions[0]=False
				moduleDesc = line.replace("'''", "").replace("Description:", "").strip()
 
			line = line.rstrip('\r\n').rstrip('\n')
			lN+=1
		    if (ErrorConditions[0]):
			log.append("__[Python]__ "+RedMark+" `"+PythonFile+"` : Missing description")
			PythonDesc.append("")
		    else:
			PythonDesc.append(moduleDesc)
		    if (ErrorConditions[1]):
			log.append("__[Python]__ "+RedMark+" `"+PythonFile+"` : Missing Author ")
		    if (ErrorConditions[2]):
			log.append("__[Python]__ "+RedMark+" `"+PythonFile+"` : Missing Copyright ")
		    if (ErrorConditions[3]):
			log.append("__[Python]__ "+RedMark+" `"+PythonFile+"` : Missing License")
	return log,PythonDesc

def CheckInoFile(files):
	log = []
	InoDesc = []
	for InoFile in files:
		InoD = ""
		with open(InoFile) as f:
		    lN = 0
		    # Description, author, copyright, license
		    ErrorConditions = [True, True, True, True]
		    for line in f:
			if ("Description:") in line:
				ErrorConditions[1]=False
				InoD = line.replace("Description:", "").strip()
			if ("Author:") in line:
				ErrorConditions[2]=False
			if ("Licence:") in line:
				ErrorConditions[3]=False
			if ("Copyright") in line:
				ErrorConditions[0]=False
			line = line.rstrip('\r\n').rstrip('\n')
			lN+=1
		    if (ErrorConditions[0]):
			log.append("__[Arduino]__ "+RedMark+" `"+InoFile+"` : Missing description")
		    if (ErrorConditions[1]):
			log.append("__[Arduino]__ "+RedMark+" `"+InoFile+"` : Missing Author ")
		    if (ErrorConditions[2]):
			log.append("__[Arduino]__ "+RedMark+" `"+InoFile+"` : Missing Copyright ")
		    if (ErrorConditions[3]):
			log.append("__[Arduino]__ "+RedMark+" `"+InoFile+"` : Missing License")
		InoDesc.append(InoD)
	return log, InoDesc

def CheckLink(path,autogen):
	log = []
	with open(path) as f:
		if ("gitbook" not in path):
		    for line in f:
			patternCode = r"\]\((.*?)\)"
			links = re.findall(patternCode, line, flags=0)
			if len(links):
			    for link in links:
				    Error = False
				    Message = "__[Links]__ "+RedMark+" `"+path+"`"
				    if ("http" not in link) and ("www" not in link) and  (not (link =="")) and  ("@autogenerated" not in link):
					    if (not link.startswith("/") and "@description" not in link):
						Error = True
						Message += " : Error in link definition, non-absolute path in link to `"+link+"`"
				    if (link.startswith("/")) and (link.endswith("/")):
					if not (os.path.isdir("."+link)):
						Error = True
						Message += " : Link to non-existing folder `."+link+"`"
				    if (link.startswith("/")) and not (link.endswith("/")):
					if not (os.path.exists("."+link)):
						Error = True
						Message += " : Link to non-existing file `."+link+"`"
				    if autogen:
					Message = Message +" _(@autogenerated)_"
				    if Error:
					log.append(Message)
	return log
# -------------------------
# Creation of dev-kit sets
# -------------------------

def GetParams(ListOfItems):
    results = []	
    for item in ListOfItems:
	pattern = r"<li>(.*?):"
	results += re.findall(pattern, str(item), flags=0) 
    return results

def getParam(Module,Parameter):
	Param = "Missing parameter for "+Parameter
	Parameter=Parameter+":"
	soupModule = returnSoup(Module+"/Readme.md")[0]
	LIs = soupModule.find_all("li")
	for eachParam in LIs:
		if (eachParam.text.startswith(Parameter)):
			Param = eachParam.text
	Param = Param.replace(Parameter, '').strip()
	return Param

# -------------------------
# Create the kits
# -------------------------

def CreateKits(path,pathmodules,FullSVG):
	Slides = ""
	AllCosts = "# What does it cost?\n\n"
	log = []

	for file in os.listdir(path):
	    if file.endswith(".set.md"):
		CostOfSet = ""
		ListOfDirs = []
		KitModuleFile = []
		NomDuSet = file[:-7]
		log.append("__[SET]__ Added `"+NomDuSet+"`\n")
		Slides = Slides + "### "+NomDuSet+"\n\n<ul>"
		with open(path+file) as f:
		    for line in f:
			line = line.rstrip('\r\n').rstrip('\n')
			if len(line)>1 and not line.startswith("#"):
				ListOfDirs.append(line)
			if len(line)>1 and line.startswith("#"):
				KitModuleFile.append(line)
		SetName = ""
		SetDescription = ""

		for item in KitModuleFile:
			if "#Title:" in str(item):
				patternCode = r"#Title:(.*?)$"
				if (re.findall(patternCode, str(item), flags=0)):
					SetName = "## "+re.findall(patternCode, str(item), flags=0)[0]
					
			if "#Description:" in str(item):
				patternCode = r"Description:(.*?)$"
				if (re.findall(patternCode, str(item), flags=0)):
					SetDescription = re.findall(patternCode, str(item), flags=0)[0]

			item = item.replace("#", "")
			Slides += "<li>"+item+"</li>\n"

		CostOfSet += SetName+"\n\n"+SetDescription.strip()+"\n"
		CostOfSet += "\n\n"
		Slides += "</ul>" +"\n\n### "+NomDuSet+": diagram\n\n![](https://raw.githubusercontent.com/kelu124/echomods/master/include/sets/"+NomDuSet+".png)"+"\r\n\n"

		GraphModules = digraph()
		# Dans chaque sous-ensemble..
		PrixSet = 0

		for eachInput in ListOfDirs:
			ModuleCost = ""
			ModuleSourcing = ""
			GraphModules.node(eachInput, style="filled", fillcolor="blue", shape="box",fontsize="22")
			ReadMe = eachInput

			ReadMehHtmlMarkdown = returnSoup("./"+eachInput+"/Readme.md")[1]
			soupSet = returnSoup("./"+eachInput+"/Readme.md")[0]

			# Getting the Desc of the Module
			ModuleTitle = getHs(soupSet,"h2","Title").text

			#print ModuleDesc

			with open("./"+eachInput+"/Readme.md") as FileContent:
				for line in FileContent:  #iterate over the file one line at a time(memory efficient)
					if "* cost:" in line:
						patternCode = r"cost:(.*?)$"
						ModuleCost = re.findall(patternCode, line, flags=0)[0]
						PrixSet += int(''.join(c for c in ModuleCost if c.isdigit()))
					if "* sourcing:" in line:
						patternCode = r"\* sourcing:(.*?)$"
						ModuleSourcing = re.findall(patternCode, line, flags=0)[0]

			if (len(ModuleCost)  and len(ModuleSourcing)):
				CostOfSet += "* "+ModuleTitle+" (["+eachInput+"](/"+eachInput
				CostOfSet += "/)) -- get for _"+ModuleCost+"_ (Where? " + ModuleSourcing+")\n"
			if len(ModuleCost) == 0:
				log.append("__[MDL "+eachInput+"]__ "+ RedMark+" Cost missing\n")
			if len(ModuleSourcing) == 0:
				log.append("__[MDL "+eachInput+"]__ "+ RedMark+" Sourcing missing\n")

			
			# Getting the Innards of the Module // inside the block diagram
			pattern = r"block diagram</h3>([\s\S]*)<h2>About"
			results = re.findall(pattern, ReadMehHtmlMarkdown, flags=0) 
			patternCode = r"<li>(.*?)</li>"

			Pairs = []
			GraphThisModule = digraph()
			for item in results:
			    Pairs= (map(str, re.findall(patternCode, item, flags=0)))
			    for eachPair in Pairs:
				eachPair = eachPair.replace("<code>", "")
				eachPair = eachPair.replace("</code>", "")
				Couples = eachPair.split("-&gt;")		
				for single in Couples:
				    GraphThisModule.node(single, style="rounded")
				# Add the edge		
				for k in range(len(Couples)-1):
				    GraphThisModule.edge(Couples[k], Couples[k+1])
				# GraphModules.render('include/'+ReadMe)

			# OK - Getting the Inputs of the Module
			Module = []
			ItemList =  returnHList(soupSet,"h3","Inputs")
		 	for OneIO in ItemList:
				codes = getCode(OneIO)
				if len(codes) > 0:
				    for EachIO in codes:
					Module.append(EachIO)
			if len(Module)>0:
			    for item in Module:
				if "ITF-m" not in item:
				    GraphModules.node(item, style="rounded,filled", fillcolor="yellow")
				else:
				    GraphModules.node(item, style="rounded,filled", fillcolor="green")		
				GraphModules.edge(item, ReadMe, splines="line", nodesep="1")


			# Getting the Ouputs of the Module
			ItemList =  returnHList(soupSet,"h3","Outputs")
		 	for OneIO in ItemList:
				codes = getCode(OneIO)
				if len(codes) > 0:
				    for EachIO in codes:
					Module.append(EachIO)
			if len(Module)>0:
			    for item in Module:
				if "ITF-m" not in item:
				    GraphModules.node(item, style="rounded,filled", fillcolor="yellow")
				else:
				    GraphModules.node(item, style="rounded,filled", fillcolor="green")		
				GraphModules.edge(item, ReadMe, splines="line", nodesep="1")
			GraphModules.edge(ReadMe, item, splines="line", nodesep="1", fillcolor="red")


			GraphPath = path+"/sets/"+NomDuSet
			if FullSVG:
				GraphModules.render(GraphPath)	
				Svg2Png(GraphPath) 
		CostOfSet+="\n\n_Total cost of the set: "+str(PrixSet)+"$_\n\n"
		OpenWrite(CostOfSet,path+"/sets/"+NomDuSet+".cost.md")
		AllCosts += CostOfSet
	# Writing the slides
	OpenWrite(Slides,path+"sets/sets_slides.md")
	OpenWrite(AllCosts,path+"sets/KitCosts.md")





	return log

