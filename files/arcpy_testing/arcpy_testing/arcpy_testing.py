import arcpy
from arcpy import env
from arcpy.sa import *
import arcpy.mapping 
import os
from tkinter import *
from Tkinter import Tk
from PIL import Image, ImageTk
import tkFont
from tkinter import messagebox
from tkinter import Menu
import pandas as pd


#submit function that accepts click and starts IDW analysis
def clickIDW():
    entered_text = textentry.get()

    arcpy.env.overwriteOutput = True

    arcpy.env.workspace = "D:\\Workspace\\Wisconsin\\2018\\Summer_2018\\GEOG777\\projects\\1\\files\\output"

    inPointFeature = "D:\\Workspace\\Wisconsin\\2018\\Summer_2018\\GEOG777\\projects\\1\\files\\files\\well_nitrate\\well_nitrate_WGS.shp"
    zField = "nitr_ran"
    outLayer = "D:\\Workspace\\Wisconsin\\2018\\Summer_2018\\GEOG777\\projects\\1\\files\\output\\IDWResults\\wellIDW"
    outRaster = "D:\\Workspace\\Wisconsin\\2018\\Summer_2018\\GEOG777\\projects\\1\\files\\output\\IDWResults\\idwOut"
    cellSize = 0.01722298928
    power = entered_text

    majSemiaxis = 1.818249165689306
    minSemiaxis = 1.818249165689306
    angle = 0
    maxNeighbors = 15
    minNeighbors = 10
    sectorType = "ONE_SECTOR"
    searchNeighborhood = arcpy.SearchNeighborhoodStandard(majSemiaxis, minSemiaxis,
                                                        angle, maxNeighbors, minNeighbors, sectorType)

    arcpy.CheckOutExtension("GeoStats")

    arcpy.IDW_ga(inPointFeature, zField, outLayer, outRaster, cellSize,
                power, searchNeighborhood)

    messagebox.showinfo("IDW Analysis", "Processing complete!")

# create function for OLS click and analysis
def clickOLS():
    arcpy.env.overwriteOutput = True
    arcpy.env.workspace = "D:\\Workspace\\Wisconsin\\2018\\Summer_2018\\GEOG777\\projects\\1\\files\\output"

    try:
        arcpy.env.workspace = "D:\\Workspace\\Wisconsin\\2018\\Summer_2018\\GEOG777\\projects\\1\\files\\output"

        ols = arcpy.OrdinaryLeastSquares_stats("D:\\Workspace\\Wisconsin\\2018\\Summer_2018\\GEOG777\\projects\\1\\files\\files\\cancer_tracts\\cancer_tracts_WGS.shp", "ID",
                                              "D:\\Workspace\\Wisconsin\\2018\\Summer_2018\\GEOG777\\projects\\1\\files\\output\\OLSResults\\olsOut.shp", "canrate", "nitrate",
                                              "D:\\Workspace\\Wisconsin\\2018\\Summer_2018\\GEOG777\\projects\\1\\files\\output\\OLSResults\\olsCoef.dbf", 
                                              "D:\\Workspace\\Wisconsin\\2018\\Summer_2018\\GEOG777\\projects\\1\\files\\output\\OLSResults\\olsDiag.dbf",
                                              "D:\\Workspace\\Wisconsin\\2018\\Summer_2018\\GEOG777\\projects\\1\\files\\output\\OLSResults\\olsReport.pdf")

        messagebox.showinfo("OLS Analysis", "Processing successful!")
        
    except:
        messagebox.showinfo("OLS Analysis", "Processing failed!")

    messagebox.showinfo("OLS Analysis", "Processing complete!")
    
#set window and color
window = Tk()
window.title("Nitrates and Cancer in Wisconsin")
window.configure(background ="#fffcf4")
window.geometry('1900x950')

#set menu NEED TO ADD REFRESH FUNCTIONALITY
menu = Menu(window)
menu.add_command(label = "Refresh")
window.config(menu=menu)

#---------------------------------------
introLbl = Label(window, text="Intro Header Here", bg="#fffcf4", fg="black", padx = 5, pady = 5, font=("Helvetica", 14))
introLbl.grid(row = 1, column = 0)

introLbl = Label(window, text="Let's look at the relationship between" + "\n" + "blah blah blah blah blah blah......", bg="#fffcf4", fg="black", padx = 5, pady = 5, font=("Helvetica", 12))
introLbl.grid(row = 2, column = 0)

#set check boxes
chkLbl = Label(window, text="Choose Layers to Display", bg="#fffcf4", fg="black", padx = 5, pady = 5, font=("Helvetica", 14))
chkLbl.grid(row = 3, column = 0)

chkWell_state = BooleanVar()
chkWell_state.set(True)
chkWells = Checkbutton(window, text = "Water Wells", var = chkWell_state, bg="#fffcf4", fg="black", font=("Helvetica", 12))
chkWells.grid(row = 4, column = 0)

chkTract_state = BooleanVar()
chkTract_state.set(True)
chkTracts = Checkbutton(window, text = "Tracts", var = chkTract_state, bg="#fffcf4", fg="black", font=("Helvetica", 12))
chkTracts.grid(row = 5, column = 0)

chkResults_state = BooleanVar()
chkResults_state.set(False)
chkResults = Checkbutton(window, text = "IDW Results", var = chkResults_state, bg="#fffcf4", fg="black", font=("Helvetica", 12))
chkResults.grid(row = 6, column = 0)

olsResults_state = BooleanVar()
olsResults_state.set(False)
olsResults = Checkbutton(window, text = "OLS Results", var = olsResults_state, bg="#fffcf4", fg="black", font=("Helvetica", 12))
olsResults.grid(row = 7, column = 0)
#-----------------------------------------

#set entry label
idwLbl = Label(window, text="Enter desired power to perform interpolation:", bg="#fffcf4", fg="black", padx = 5, pady = 5, font=("Helvetica", 14))
idwLbl.grid(row=8, column=0)

#create textbox
textentry = Entry(window, width=20, bg="gray")
textentry.grid(row=9, column=0)

#create submit button
btnIDW = Button(window, text="Run Analysis", width=12, font=("Helvetica"), command=clickIDW) 
btnIDW.grid(row=10, column=0)

#set OLS label
olsLbl = Label(window, text="Click below to run Ordinary Least Squares Analysis: ", bg="#fffcf4", fg="black", padx = 5, pady = 5, font=("Helvetica", 14))
olsLbl.grid(row=11, column=0)

#create OLS button
btnOLS = Button(window, text="Run OLS", width=7, font=("Helvetica"), command=clickOLS) 
btnOLS.grid(row=12, column=0)



window.mainloop()




