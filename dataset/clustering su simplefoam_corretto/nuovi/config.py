
'''
################ FTF ################

ALWATS SPECIFY THE KIND OF SIMULATION TO 
PERFORM, THE INPUT DICT WILL BE CHOESED
ACCORDINGLY

#####################################

###Clustering ID parameters:###
userID = -1: clustering on multiple snapshot, the script save different scaler and models
    for every snapshot of the clustering (the ones corresponding to the startID and endID interval)
userID = everything else: clustering on a single snapshot and results stored for a single 
    scaler and model, use this for forwarding on a desired time instant (to be expressed in userID) 


# TO DO:

- control origineScalato etc. (line77)

### ALWAYS REMEMBER THAT Z IS VERTICAL AXIS AND X IS THE STREAMWISE AXIS ###
### ALWAYS REMEMBER TO EXPORT THE SLICES OF THE MESH WITH EXTRACTSURFACE.PY ###

'''


## KIND OF SIMULATION ##

sim='LES' # RANS or LES

## Confusion Matrix ##
Conf_Matrix = False # set true to plot confusion matrix, remember that the confusion matrix 
                   # can be calculated only on the same mesh
  
inputDict = {
    # General parameters
    "sourceFile": "src/config.py",
    "in_simulation_dir":True, # if True, the analysis is in the simulation directory
    "turbine": 'turbine1', # define, for multi machines simulation, the turbine of the analysis
    #### if in_simulation_dir is false specify: ####
    "origin": [0,0,0],
    "towerHeight": 0,
    "hubAxDist": 5,
    "axis": [-1,0,0], # axis of rotation of the turbine
    "tilt": 0, # tilt angle of the turbine in radians
    "yaw": 0, # yaw angle of the turbine in radians
    "turbineRadius": 63,
    #################################################
    "outputPath": "output_seep_2/", # ALWAYS USE ABSOLUTE PATHS
    "dataPath": "", #ALWAYS USE ABSOLUTE PATHS
    "z_normal": False, # if the dataset is z_normal put true for viasualization
    "isolated": False, # if the turbine is isolated or in ABL
    "startID": 0, # ID of the first snapshot to be read
    "endID": 2, # ID of the last snapshot to be read
    "userID": 0, # if equal to -1 is deactivated, otherwise force the ID of the snapshot to be read (e.g. forwarding on a different snapshot wrt clustering)
    # numeration for id numbers starts from 0

    
    # Clustering parameters
    "scaler": "minmax", # minmax (MinMax), standardscaler (StandardScaler),  robust (RobustScaler)
    "algorithm": "km", # km (k-Means), kmd (k-Medoids), gm (Gaussian Mixture), Hierarchical (agglomerative clustering), DBSCAN
    "toCluster": [
                  'Ux',
                  'Ut',
                  'Ur',
                  #'k',
                  # 'p',
                  #'nut',
                  #'vort_x',
                  #'vort_t',
                  # 'vort_r',
                  #'ax',
                  #'rho',
                  # 'theta'
                  #'z_original'
                  ], # features selection
    "nCluster": 7,
    "clusterReorderMethod": "Ux", # feature to be used for reordering the clusters (based on the mean value)
    "ascendingOrder": False, # if True, the clusters are ordered in ascending order, otherwise in descending order
    "mask": False, # if True, data are parsed through a mask for avoiding the NaN values
    
    # Feature selection analysis
    "elbow": True,
    
    # Operations
    "onlyPreprocessing": False,
    "clustering": True,
    "forwarding": False, 
    "multipleClustering": False,
    "pcaClustering": False,   # FIRST: Do PCA clustering to train models  
    "pcaMultipleClustering": False,  # New: PCA-based multiple clustering
    "pcaForwarding": False,  # SECOND: Then do PCA forwarding
    "postprocessing": True,
    
    # Dataset analysis (cartesian or cylindrical) (Preprocessing)
    "CART": True, # If True, the dataset is analyzed in cartesian coordinates
    "CYL": True, # If True, the dataset is analyzed in cylindrical coordinates 
    "cyl_abs": False, # If True, the radial and tangential components in cylindrical coordinates are considered in absolute value
    "PCA": True, # If True, the PCA analysis is performed (after normalization) (both for cyl and cart coordinates)
    "PCA_weighted_importance": True, # If True, the weighted importance of the PCA components is calculated (after normalization) (both for cyl and cart coordinates)
    "CORR_MATRIX": True, # If True, the correlation matrix is calculated (before normalization) (both for cyl and cart coordinates)
    "DISTRIBUTION": False, # If True, the distribution of the features is calculated (before normalization) (both for cyl and cart coordinates)
    "SCATTER": False, # If True, the scatter plot of the dataset is plotted (Uax/k) (after normalization)
    "variabili_CM": ['Ux','Uy','Uz','Ut','Ur','vort_x','vort_y','vort_z','vort_t','vort_r','p','k','nut'], # list of features to be used in the correlation matrix (normalized)

    # PCA Clustering specific parameters
    "pcaComponents": 0.95,  # Number of PCA components (float for explained variance, int for exact number)
    "pcaFeatureSet": "CART",  # Feature set for PCA: "CART" or "CYL"
    "pcaTrainingSnapshotId": 0,  # Snapshot ID to use for training PCA model (for forwarding)
    
    # Operations in postprocessing (after clustering)
    "boxplot": False,
    "scatterplot":False,
    "singleTurbulenceTriangle": False,
    "multipleTurbulenceTriangle": False,
    "pairplot": False, # if scatterplot not True scatterplot will not work
                      # pairplot will be slow, remember to turn it off 
    "meanLabel": False, # if True, for multi snapshot clustering, plot the mean value of the ID per cells
    

    # PPTX parameters
    "ifPres": True,  
    "presFile": "ClusteringReport",
    "presFileForw": "ForwardingReport",
    "presFileForClus": "ClusteringForwardingReport",
    "folder": "dataTest",
    "footer": "giovanni.delibra@uniroma1.it",
    "version": "alpha",
    "template": "src/test-template.pptx",
    "title": "Clustering Report",
    "title_forwarding": "Forwarding Report",
    "title_for_clus": "Clustering Forwarding Report",
    "title_for_multi_clus": "Multiple Clustering Report",
    "title_for_pca_clus": "PCA-based Clustering Report",
    "title_for_pca_multi_clus": "PCA-based Multiple Clustering Report",

    #use custom palette colors
    "palette": {
    "customColors": True,
    "colors":
    [
      "#616161","#e41a1c","#377eb8","#4daf4a","#ff5500",
      "purple", "limegreen"
    ]
  }
}

# DA SISTEMARE
toDrop = [] #?????????? #####non viene usato

# ADDITIONAL PARAMETERS
'''
###PAY ATTENTION###
Remembre to alway reduce the number of elbow number of cluster 
if working with KMD, GMM or Hierarchical to avoid extreme slow 
operations

'''

elbowNC = [1,2,3,4,5,6,7,8,9,10,11,12,15,18,21,25,30,40,50] # number of cluster to be used in the elbow chart
MS= [1,5,10,20,50,75,100,200,500,1000,1500,2000,3000,4000] # min_samples to be used in the DBSCAN algorithm


toIncludeVTK = ['Uax','Ur','Ut','UMeanx','UMeanr','UMeant','k','nut','k_res', 'k', 'Q', 'rho', 'ax', 'theta', 'z_original'] # features to include in the final vtk file with clusters
# Dictionary to rename the variables in the df
toRename = {
            'turbulenceProperties:R:0': 'Rxx',
            'turbulenceProperties:R:1': 'Rxy',
            'turbulenceProperties:R:2': 'Rxz',
            'turbulenceProperties:R:3': 'Ryy',
            'turbulenceProperties:R:4': 'Ryz',
            'turbulenceProperties:R:5': 'Rzz',
            'Points:0': 'x',
            'Points:1': 'y',
            'Points:2': 'z',
            'U:0': 'Ux',
            'U:1': 'Uy',
            'U:2': 'Uz',
            'UMean:0': 'UMeanx',
            'UMean:1': 'UMeany',
            'UMean:2': 'UMeanz',
            'vorticity:0':'vort_x',
            'vorticity:1': 'vort_y',
            'vorticity:2': 'vort_z',
            'vorticityax': 'vort_ax', 
            'vorticityr': 'vort_r', 
            'vorticityt': 'vort_t'
            }

vectors = [
            "U", 
            "vorticity", 
            "UMean", 
            "Points"
            ] # list of vectors in the df to be projected in cylindrical coords
symtensors = [
            "UPrime2Mean", 
            "turbulenceProperties:R"
            ] # list of symmetric tensors to be projected in cylindrical coords
tensors = []
xyz = [
            'Points:0', 
            'Points:1', 
            'Points:2'
            ] # list of coordinates in the df xyz

# Features to be used in the PCA analysis (cartesian or cylindrical) if PCA_SELECTED_FEAT is True
featurePCA_cyl = [ 
              'Q', 
              'Rrr', 'Rrt', 'Rtt', 'Rxr', 'Rxt', 'Rxx', 
              'Ur', 'Ut', 'Ux', 
              'k', 
              'nut', 
              'p',
              'vort_r', 'vort_t', 'vort_ax',
              'ax', 'rho', 'theta'
              ]

featurePCA_cart = [ 
              'Q', 
              'Rxx', 'Rxy', 'Rxz', 'Ryy', 'Ryz', 'Rzz', 
              'Ux', 'Uy', 'Uz', 
              'k', 
              'nut', 
              'p',
              'vort_x', 'vort_y', 'vort_z',
              'x', 'y', 'z'
              ]

listToDistr = ['Uax', 'Ur', 'Ut', 'k', 'nut', 'Q',  'Ux', 'Uy', 'Uz'] #list of features to be used in the distribution
listToBoxPlot = ['Uax', 'Ur', 'Ut', 'k', 'nut', 'Ux', 'Uy', 'Uz','UMeanx','UMeanr','UMeant'] #list of features to be used in the boxplot
listToPairplot = ['Uax', 'Ur', 'Ut', 'k', 'nut', 'Uy', 'Uz','ID'] #list of features to be used in the pairplot
