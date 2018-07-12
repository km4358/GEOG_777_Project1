# "Nitrates and Cancer in Wisconsin" Python code by Kerry C. McAlister, 2018

import os
import arcpy
from arcpy import env
from arcpy.sa import *
import arcpy.mapping
from tkinter import *
from tkinter import messagebox
from tkinter import Tk
from PIL import Image, ImageTk
import ImageTk
import tkFont

# Set IDW function 
def runAnalysis():
    
    # Establish environment
    arcpy.env.resamplingMethod = "BILINEAR"
    env.workspace = "D:\\Workspace\\Wisconsin\\2018\\Summer_2018\\GEOG777\\projects\\1\\files"
    arcpy.env.overwriteOutput = True

    # Set variables
    inPointFeatures = "input\\well_nitrate_WGS.shp"
    zField = "nitr_ran"
    cellSize = 0.01722298928
    e = float(k.get()) #convert any potential decimal value entry   
    power = e
    print power
    searchRadius = RadiusVariable(10, 15)

    # Check out ESRI license
    arcpy.CheckOutExtension("Spatial")

    # run IDW
    outIDW = Idw(inPointFeatures, zField, cellSize, power, searchRadius)

    outIDW.save("D:\\Workspace\\Wisconsin\\2018\\Summer_2018\\GEOG777\\projects\\1\\files\\output\\idw.tif")
    
    #load IDW results into map doc, symbolize, and prep for export
    #set mxd path to receive output data
    mxd = arcpy.mapping.MapDocument("D:\\Workspace\\Wisconsin\\2018\\Summer_2018\\GEOG777\\projects\\1\\files\\input\\idw.mxd")
	#assign data frame variable
    dataFrame = arcpy.mapping.ListDataFrames(mxd, "Layers")[0]
	#assign tif variable 
    tif = arcpy.mapping.Layer(r"output\\idw.tif")
	#assign tract variable
    tracts = arcpy.mapping.Layer(r"input\\cancer_tracts_WGS.shp")
	#assign IDW result symbology variable
    idwSym = "input\\idw_symbology.lyr" 
	#assign tract symbology variable
    tractSym = "input\\cancer_tracts.lyr" 
	#apply symbology to IDW results TIFF
    arcpy.ApplySymbologyFromLayer_management(tif, idwSym)
	#apply symbology to tracts
    arcpy.ApplySymbologyFromLayer_management(tracts, tractSym)
	#add TIFF layer to mxd
    arcpy.mapping.AddLayer(dataFrame, tif, "AUTO_ARRANGE")
	#add tracts to mxd
    arcpy.mapping.AddLayer(dataFrame, tracts, "AUTO_ARRANGE") 
    
    # export pdf and png results
    arcpy.mapping.ExportToPDF(mxd, "D:\\Workspace\\Wisconsin\\2018\\Summer_2018\\GEOG777\\projects\\1\\files\\output\\idw_map.pdf")
    arcpy.mapping.ExportToPNG(mxd, "D:\\Workspace\\Wisconsin\\2018\\Summer_2018\\GEOG777\\projects\\1\\files\\output\\idw.png")    
  
    # run zonal stats at census tract level
    inData = "D:\\Workspace\\Wisconsin\\2018\\Summer_2018\\GEOG777\\projects\\1\\files\\input\\cancer_tracts_WGS.shp"
    zoneField = "GEOID10"
    inRaster = "D:\\Workspace\\Wisconsin\\2018\\Summer_2018\\GEOG777\\projects\\1\\files\\output\\idw.tif"
    outTable = "D:\\Workspace\\Wisconsin\\2018\\Summer_2018\\GEOG777\\projects\\1\\files\\output\\zonalstat.dbf"

    outZStaT = ZonalStatisticsAsTable(inData, zoneField, inRaster, 
                                     outTable, "NODATA", "MEAN")    

    # join the zonal stats to the cancer_tracts table
    try:

        env.qualifiedFieldNames = False
        arcpy.env.overwriteOutput = True
        
        inFeatures = "D:\\Workspace\\Wisconsin\\2018\\Summer_2018\\GEOG777\\projects\\1\\files\\input\\cancer_tracts_WGS.dbf"
        layerName = "cancer_tracts"
        joinTable = "D:\\Workspace\\Wisconsin\\2018\\Summer_2018\\GEOG777\\projects\\1\\files\\output\\zonalstat.dbf"
        joinField = "GEOID10"
        expression = ""
        outFeature = "D:\\Workspace\\Wisconsin\\2018\\Summer_2018\\GEOG777\\projects\\1\\files\\output\\censusjoin"
        isCommon = "KEEP_COMMON"
        
        #create feature layer
        arcpy.MakeFeatureLayer_management (inFeatures,  layerName)
        
        # join feature layer to table
        arcpy.AddJoin_management(layerName, joinField, joinTable, joinField, isCommon)
        
        #copy to new feature class
        arcpy.CopyFeatures_management(layerName, outFeature)
     
    #trap errors and return popup window  
    except Exception, e:
        import traceback, sys
        tb = sys.exc_info()[2]
        messagebox.showinfo("Error", "Line %i" % tb.tb_lineno + '/n' + e.message)
                
    # overwrite existing
    arcpy.env.overwriteOutput = True

    # set workspace location
    workspace = "D:\\Workspace\\Wisconsin\\2018\\Summer_2018\\GEOG777\\projects\\1\\files"

    try:
        arcpy.env.workspace = workspace

        # run OLS geoproccessing
        ols = arcpy.OrdinaryLeastSquares_stats("D:\\Workspace\\Wisconsin\\2018\\Summer_2018\\GEOG777\\projects\\1\\files\\output\\censusjoin.shp", "OID_", 
                            "D:\\Workspace\\Wisconsin\\2018\\Summer_2018\\GEOG777\\projects\\1\\files\\output\\olsResults.shp", "canrate", "MEAN",
                            "D:\\Workspace\\Wisconsin\\2018\\Summer_2018\\GEOG777\\projects\\1\\files\\output\\OLSOutput\\OLSCoeff.dbf",
                            "D:\\Workspace\\Wisconsin\\2018\\Summer_2018\\GEOG777\\projects\\1\\files\\output\\OLSOutput\\OLSDiag.dbf",
                            "D:\\Workspace\\Wisconsin\\2018\\Summer_2018\\GEOG777\\projects\\1\\files\\output\\OLSOutput\\OLSReport.pdf")   

        # run spatial weights matrix 
        swm = arcpy.GenerateSpatialWeightsMatrix_stats("D:\\Workspace\\Wisconsin\\2018\\Summer_2018\\GEOG777\\projects\\1\\files\\output\\censusjoin.shp", "OID_",
                            "D:\\Workspace\\Wisconsin\\2018\\Summer_2018\\GEOG777\\projects\\1\\files\\output\\euclid.swm",
                            "K_NEAREST_NEIGHBORS",
                            "#", "#", "#", 6) 
                              
        # run Morans I   
        morans = arcpy.SpatialAutocorrelation_stats("D:\\Workspace\\Wisconsin\\2018\\Summer_2018\\GEOG777\\projects\\1\\files\\output\\olsResults.shp", "Residual",
                            "GENERATE_REPORT", "GET_SPATIAL_WEIGHTS_FROM_FILE", 
                            "EUCLIDEAN_DISTANCE", "NONE", "#", 
                            "D:\\Workspace\\Wisconsin\\2018\\Summer_2018\\GEOG777\\projects\\1\\files\\output\\euclid.swm")

    # trap errors
    except:
        #print(arcpy.GetMessages())
        messagebox.showinfo("Error", arcpy.GetMessages())

    # load OLS results into map doc, symbolize, prep for export, essentially same as IDW
    mxdOls = arcpy.mapping.MapDocument("D:\\Workspace\\Wisconsin\\2018\\Summer_2018\\GEOG777\\projects\\1\\files\\input\\olsmap.mxd")
    dfOls = arcpy.mapping.ListDataFrames(mxdOls, "Layers")[0]    
    olsResults = arcpy.mapping.Layer(r"D:\\Workspace\\Wisconsin\\2018\\Summer_2018\\GEOG777\\projects\\1\\files\\output\\olsResults.shp")
    olsSym = "D:\\Workspace\\Wisconsin\\2018\\Summer_2018\\GEOG777\\projects\\1\\files\\input\\ols_symbology.lyr"
    arcpy.ApplySymbologyFromLayer_management(olsResults, olsSym)
    arcpy.mapping.AddLayer(dfOls, olsResults, "AUTO_ARRANGE")

    # export to pdf and png
    arcpy.mapping.ExportToPDF(mxdOls, "D:\\Workspace\\Wisconsin\\2018\\Summer_2018\\GEOG777\\projects\\1\\files\\output\\Ols_map.pdf")
    arcpy.mapping.ExportToPNG(mxdOls, "D:\\Workspace\\Wisconsin\\2018\\Summer_2018\\GEOG777\\projects\\1\\files\\output\\ols.png")
   
    #popup window alerting user that analysis is complete
    messagebox.showinfo("Analysis", "Analysis successfully proccessed!")
    
    # update with new map image    
    olsImage = ImageTk.PhotoImage(file="D:\\Workspace\\Wisconsin\\2018\\Summer_2018\\GEOG777\\projects\\1\\files\\output\\ols.png")
    widgetf.configure(image=olsImage)
    widgetf.image = olsImage
    Image.ANTIALIAS
       
    
#function to view the IDW map
def viewIDW():
    try:
        idwImage = ImageTk.PhotoImage(file="D:\\Workspace\\Wisconsin\\2018\\Summer_2018\\GEOG777\\projects\\1\\files\\output\\idw.png")
        widgetf.configure(image=idwImage)
        widgetf.image = idwImage
    except:
        messagebox.showinfo("IDW Analysis", "Please run application before viewing results.")     

# function to view the OLS map
def viewOLS():
    try:
        olsImage = ImageTk.PhotoImage(file="D:\\Workspace\\Wisconsin\\2018\\Summer_2018\\GEOG777\\projects\\1\\files\\output\\ols.png")
        widgetf.configure(image=image3)
        widgetf.image = image3
    except:
        messagebox.showinfo("OLS Analysis", "Please run application before viewing results.")
            
#define refresh button
def viewHome():
    try:
        widgetf.configure(image = imagePath)
        widgetf.image = imagePath
    except:
        messagebox.showinfo("Unable to load basemap.")

# Set window and title
window = Tk()
window.title('Something in The Water: Nitrates and Cancer in Wisconsin')
window.resizable(width = FALSE, height = FALSE)

# Initiate background
background = ImageTk.PhotoImage(file="D:\\Workspace\\Wisconsin\\2018\\Summer_2018\\GEOG777\\projects\\1\\files\\input\\background.jpg")
Image.ANTIALIAS
backgroundImage = Label(window, image=background)
backgroundImage.place(x=0, y=0, relwidth=1, relheight=1)

# Initiate map container and load basemap
imagePath = ImageTk.PhotoImage(file="D:\\Workspace\\Wisconsin\\2018\\Summer_2018\\GEOG777\\projects\\1\\files\\input\\basemap.png")
widgetf = Label(window, image=imagePath, bg="gray")
widgetf.pack(side="top", padx=10, pady=10)
Image.ANTIALIAS

# create "about" frame
about = Frame(window, highlightbackground="gray", highlightcolor="gray", highlightthickness=.5, bg="white")
about.pack(side = "left", padx=10, pady=10)

#set menu for refresh function
menu = Menu(window)
menu.add_command(label = "View Well Map", command = viewHome)
window.config(menu=menu)

# title for "about" frame
aboutTitle = Text(about, width=20, height=1, borderwidth=0, bg="white", highlightthickness=0, wrap=WORD)
aboutTitle.insert(INSERT, "Something in the water?")
aboutTitle.config(state=DISABLED)
aboutTitle.configure(font=("Calibri", 14))
aboutTitle.pack(pady=2)

# "about" text body
aboutText = Text(about, width=35, height=16, borderwidth=0, highlightthickness=0, wrap=WORD, bg="white")
aboutText.insert(INSERT, "Explore the relationship between nitrate levels in water wells and cancer in the state of Wisconsin. Use the tools below to create maps from IDW* and OLS** analysis. The application folder will contain output statistics, tables, and PDF reports after analysis has been successfully completed." +
                 '\n' + " " + '\n' + "*IDW: Inverse Distance Weighted Interpolation" + '\n' + " " + '\n' + "**OLS: Ordinary Least Squares Regression Testing")
aboutText.config(state=DISABLED)
aboutText.configure(font=("Calibri", 11))
aboutText.pack(padx=1)

# analysis frame
run = Frame(window, highlightbackground="gray", highlightcolor="gray", highlightthickness=.5, bg="white")
run.pack(padx=10, pady=10)

# analysis title
runTitle = Text(run, width=12, height=1, borderwidth=0, bg="white", highlightthickness=0, wrap=WORD)
runTitle.insert(INSERT, "Run Analysis")
runTitle.config(state=DISABLED)
runTitle.configure(font=("Calibri", 12))
runTitle.pack(padx=4, pady=2)

# analysis text
runText = Label(run, text="Enter a power (k) value for IDW:", bg="white")
runText.pack()

# text box for user entry
k = Entry(run, bg="gray")
k.pack(pady=1)

# button to run both OLS and IDW
runButton = Button(run, text ="Analyze", command=runAnalysis)
runButton.pack(pady=1)

# results frame
results = Frame(window, highlightbackground="gray", highlightcolor="gray", highlightthickness=.5, bg="white")
results.pack(padx=10, pady=10)

# results title
resultsTitle = Text(results, width=18, height=1, borderwidth=0, bg="white", highlightthickness=0, wrap=WORD)
resultsTitle.insert(INSERT, "Click to Switch View:")
resultsTitle.config(state=DISABLED)
resultsTitle.configure(font=("Calibri", 12))
resultsTitle.pack(anchor = CENTER)

# results buttons
idwButton = Button(results, text ="IDW", command=viewIDW)
idwButton.pack(side="left", padx=10, pady=10)
olsButton = Button(results, text ="OLS", command=viewOLS)
olsButton.pack(side="right", padx=10, pady=10)

#use status bar to show attribution
status = Label(window, text="© Kerry C. McAlister, 2018; Data: UW-Madison", borderwidth=1, anchor=E)
status.pack(side="bottom", fill=X)

window.mainloop()
