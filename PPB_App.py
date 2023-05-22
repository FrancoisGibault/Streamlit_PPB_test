import streamlit as st
import requests
from io import BytesIO
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt
import os.path, time
import seaborn as sns
from matplotlib.dates import (YEARLY, MONTHLY, DateFormatter,
                              rrulewrapper, RRuleLocator, drange)

def ouverture_session():
    if 'counter' not in st.session_state:
      st.session_state['counter'] = 0

def init_sidebar():
    st.markdown(
    """
    <style>
        [data-testid=stSidebar] [data-testid=stImage]{
            text-align: center;
            display: block;
            margin-left: auto;
            margin-right: auto;
            width: 100%;
        }
    </style>
    """, unsafe_allow_html=True
    )

    image = Image.open("ppb3.png")
    st.sidebar.image(image)
    st.sidebar.markdown("<h1 style='text-align: center; color: white;'>Version 2023 ltd</h1>", unsafe_allow_html=True)

    mois={'Jan':'janvier', 'Feb':'février', 'Mar':'mars', 'Apr':'avril',
           'May': 'mai', 'Jun':'juin','Jul':'Jui',
           'Aug':'août', 'Sep':'septembre', 'Oct':'octobre', 'Nov':'novembre', 'Dec':'décembre'} 
    dat = time.ctime(os.path.getmtime("PPB_App.py"))
    mon = mois[dat[4:7]]
    j = dat[-16:-14]
    y = dat[-4:]
    h = int(dat[-13:-11])+2
    m = dat[-10:-8]
    str1 = "Dernière modification le " + j +" "+mon+" "+y

    str2 = str(h)+" : "+m
    st.sidebar.markdown('<div style="color:grey;text-align: right;">'+str1+'</div>', unsafe_allow_html=True)
    st.sidebar.markdown('<div style="color:grey;text-align: right;">'+str2+'</div>', unsafe_allow_html=True)

    
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%   
# 〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️
#      Chargement des données & traitement
# 〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%   

@st.experimental_singleton
def load_data(url):
    df = pd.read_csv(url, sep=";", index_col =0)  # 👈 Download the data
    col = df.columns
    nbColInit = df.shape[1]
    if (col[0]!='index'):
      df=df.reset_index()

    retires = ["69 Boulevard Ornano (temporaire)", "69 Boulevard Ornano", "74 Boulevard Ornano", "100 rue La Fayette", "105 rue La Fayette",
             "254 rue de Vaugirard", "3 avenue de la Porte D'Orléans (gare routière)", "2 avenue de la Porte de Bagnolet",
             "21 boulevard Saint Michel", "20 Avenue de Clichy", "26 boulevard de Ménilmontant", "30 rue Saint Jacques (temporaire)"]
    lstcmp = df['Nom du compteur'].unique()

    for x in lstcmp:
      for i in retires:
        if x[:10]==i[:10]:
          df = df[df['Nom du compteur']!=x]

    df["Identifiant du site de comptage"] = df["Identifiant du site de comptage"].astype(str)
    df['annee_cmpt'] = df["mois_annee_comptage"].apply(lambda x: x[:4])
    df['Date du comptage'] = df["Date et heure de comptage"].apply(lambda x: x[:10])
    df['Date du comptage'] = pd.to_datetime(df['Date du comptage'])
 
    df['Date et heure de comptage'] = pd.to_datetime(df['Date et heure de comptage'])
    df['Annee'] =  df['Date et heure de comptage'].apply(lambda x: x.year)
    df['Mois'] =  df['Date et heure de comptage'].apply(lambda x: x.month)
    df['Heures'] =  df['Date et heure de comptage'].apply(lambda x: x.hour)
    df['Jours'] =  df['Date et heure de comptage'].apply(lambda x: x.weekday())

    lstCmptNom = df['Nom du compteur'].unique()
    dfCol = pd.DataFrame({'Date et heure de comptage': df['Date et heure de comptage'].unique()})
    for nm in lstCmptNom:
      dg = df[df['Nom du compteur']==nm]
      dg = dg[['Date et heure de comptage','Comptage horaire']]
      dfCol = dfCol.merge(dg[['Date et heure de comptage','Comptage horaire']], on ='Date et heure de comptage', how="outer")
      dfCol = dfCol.rename(columns={'Comptage horaire' : nm} )
    
    dft =pd.DataFrame({'Date et heure de comptage': df['Date et heure de comptage'].unique()})
    
    lstCmptNom = df['Nom du compteur'].unique()
    dxtrait = df[df['Nom du compteur']==lstCmptNom[0]]
    
    df = df.drop(['Identifiant technique compteur','ID Photos','id_photo_1', 'url_sites',	'type_dimage'], axis=1)

    return df,dfCol,dft,nbColInit,dxtrait


#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%     
#         Généralités
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%     

def stats_gene(df):
    st.subheader("Visualisation de la base")
    st.write("Source :", url_data)
    st.caption("Affichage limité à un compteur")

    
    st.dataframe(dxtrait.iloc[:,1:(nbColInit+1)], height = 200)

    dx = df['Date et heure de comptage'].apply(lambda x: x.strftime("%H:%M")).unique()
    freq = 24/len(dx)

    st.subheader("Caractéristiques générales ")

    st.write("La base contient ",nbColInit," colonnes et ", df.shape[0], "lignes")

    debut =  min(df['Date et heure de comptage']).date().strftime("%d/%m/%Y")
    fin = max(df['Date et heure de comptage']).date().strftime("%d/%m/%Y")

    col1, col2 = st.columns(2)

    with col1:
      txt="Période de compatge : du " + debut + " au " + fin 
      st.markdown(txt)
      st.write("Nombre de comptage par heure : ",freq)

      dinst=df[['Nom du compteur',"Date d'installation du site de comptage"]]
      dinst = dinst.drop_duplicates(subset=['Nom du compteur'])
      dinst["Annee d'installation"]=dinst["Date d'installation du site de comptage"].apply(lambda x: x[:4])
      
      # 〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️    
      plt.rcParams['text.color'] = COLOR
      plt.rcParams['axes.labelcolor'] = COLOR
      plt.rcParams['xtick.color'] = COLOR
      plt.rcParams['ytick.color'] = COLOR
        
      fig, ax =plt.subplots(figsize=(10, 5))
      fig.patch.set_facecolor('black')
      ax.spines[:].set_color(COLOR)
      ax.patch.set_facecolor('black')
      sns.countplot(data = dinst, x = "Annee d'installation")
      #plt.style.use("dark_background")
      plt.ylabel("Nombre de compteurs")
      st.pyplot(fig) 
      # 〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️    
      
    with col2:
      lstCmptNom = df['Nom du compteur'].unique()
      st.write("Nombre de sites de comptage : ",  len(df["Identifiant du site de comptage"].unique()))
      st.write("Nombre de compteurs : ", len(lstCmptNom))

    with st.expander("See explanation"):
        st.markdown('''
                   La mairie fait installer des compteurs permettant de mesurer la fréquentation sur les pistes cyclables depuis 2012.
                   Les données de comptages sont mises à disposition sur le site de l'Open Data de la marie: https://parisdata.opendatasoft.com/

                   Le jeu de données contient les informations d'identification, de comptage horaires des vélos par compteur et leur localisation. 
                   La mise à jour des données est journalière.
                  
                   Il fournit également des liens vers les photos des sites de comptage (voir en page Visual. "individuelle" sélectionnable sur le côté gauche de cette page).
                   

                   Nous renouvelons ici nos remerciement à la Direction de la voirie et des déplacements, Mission vélo – pôle culture vélo,
                    de la Mairie de Paris son accueil et son écoute.

                   Cette application, limitée (ltd), ne prend en charge que le dernier jeu de données.                  


                   Nota : les données concernant les compteurs déposés dans le cadre des travaux
                    de pérennisation des pistes cyclables ont été retirées (voir la page dédiée au jeu de données sur le site https://parisdata.opendatasoft.com/)
          
                  ''')
        


#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%      

#     Stats Générales

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%    
def stats():
    valMax = 0
    col1, col2 = st.columns([1, 3])

    with col1:
      st.write("Statistiques sur les comptages")
      st.write(df["Comptage horaire"].describe())
      agree = st.checkbox('Valeurs extrêmes')
      if agree:
        valMax = 1

 # 〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️
 #   Comptage Max  

    maxi= df["Comptage horaire"].unique().max()
    moyenne = df["Comptage horaire"].unique().mean()*4

    with col2:
      lstCmptNom = df['Nom du compteur'].unique()
      
      # graph global
      plt.rcParams['text.color'] = COLOR
      plt.rcParams['axes.labelcolor'] = COLOR
      plt.rcParams['xtick.color'] = COLOR
      plt.rcParams['ytick.color'] = COLOR
      
      nbcol = len(dfCol.columns)-1
      dfCol['moyenne'] = dfCol.iloc[:,1:nbcol].mean(axis=1)
      #dfCol['moyenne'] = dfCol.mean(axis=1)
      dfCol['min'] = dfCol.iloc[:,1:nbcol].min(axis=1)
      #dfCol['min'] = dfCol.min(axis=1)
      dfCol['max'] = dfCol.iloc[:,1:nbcol].max(axis=1)
      #dfCol['max'] = dfCol.max(axis=1)

      fig, ax = plt.subplots(figsize=(8, 5))
      fig.patch.set_facecolor('black')
      ax.spines[:].set_color('grey')
      ax.patch.set_facecolor('black')
      plt.grid(axis = 'y', color='dimgrey')
      sns.lineplot(data =dfCol[dfCol["max"] < (moyenne + maxi*valMax)], x='Date et heure de comptage', y="max",label='Max', color='cornflowerblue')
      sns.lineplot(data =dfCol[dfCol["max"] < (moyenne + maxi*valMax)], x='Date et heure de comptage', y="moyenne",label='Moyenne', color='tan')
      sns.lineplot(data =dfCol[dfCol["max"] < (moyenne + maxi*valMax)], x='Date et heure de comptage', y="min",label='Min',color='darkviolet')
      plt.ylabel('Comptage')
      plt.legend(frameon=False)
      plt.style.use("dark_background")
      st.pyplot(fig)
    
      
 # 〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️
 #   Comptage Max  

    st.dataframe(df[df["Comptage horaire"]>moyenne][['Identifiant du compteur', 'Nom du compteur',
       'Identifiant du site de comptage',
       'Comptage horaire', 'Date et heure de comptage',
       "Date d'installation du site de comptage"]])

 # 〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️    
    dm = df.groupby(["Mois",'Annee']).agg({'Comptage horaire':'mean'})
    dm = dm.reset_index()
    #st.write(type(dm.Annee.unique()[0]))
    #cols = ['royalblue' if x < '2023' else 'chocolate' for x in dm.Annee]
    # Create an array with the colors you want to use
    colors = ["#FF0B04", "#4374B3"]
    # Set your custom color palette
    sns.set_palette(sns.color_palette(colors))
    #sns.set_style('whitegrid')
    
    fig, ax =plt.subplots(figsize=(15, 3))
    fig.patch.set_facecolor('black')
    ax.spines[:].set_color(COLOR)
    ax.patch.set_facecolor('black')
    plt.grid(axis = 'y', color='dimgrey')
  
    sns.barplot(data =dm, x='Mois', y="Comptage horaire", hue='Annee')
    plt.legend(frameon=False);
    plt.style.use("dark_background")
    st.pyplot(fig)
    

 # 〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️
    dm = df.groupby(["Heures",'Annee']).agg({'Comptage horaire':'mean'})
    dm = dm.reset_index()
    
    fig, ax =plt.subplots(figsize=(15, 3))
    fig.patch.set_facecolor('black')
    ax.spines[:].set_color(COLOR)
    ax.patch.set_facecolor('black')
    plt.grid(axis = 'y', color='dimgrey')
    sns.barplot(data =dm, x='Heures', y="Comptage horaire", hue='Annee')
    plt.legend(frameon=False);
    plt.style.use("dark_background")
    st.pyplot(fig)


# 〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️
    days = ['Lun','Mar','Mer','Jeu','Ven','Sam','Dim']
    
    dm = df.groupby(["Jours",'Annee']).agg({'Comptage horaire':'mean'})
    dm = dm.reset_index()
    
    fig, ax =plt.subplots(figsize=(15, 3))
    fig.patch.set_facecolor('black')
    ax.spines[:].set_color(COLOR)
    ax.patch.set_facecolor('black')
    plt.grid(axis = 'y', color='dimgrey')
    sns.barplot(data =dm, x='Jours', y="Comptage horaire", hue='Annee')
    ax.set_xticklabels(days)
    plt.legend(frameon=False);
    plt.style.use("dark_background")
    st.pyplot(fig)
    
    with st.expander("See explanation"):
        st.markdown(''' 
                    Les valeurs repérées comme extrême sont exclues des représentations graphiques.
                    Pour les faires réapparaître, il suffit de cocher la case "Valeurs extrêmes" sous les statistiques de comptage.
                    ''')

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%     
#       Correlation
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%   
    
def correla():    

      txErr = st.slider("Taux d'erreurs", 0.0, 100.0, 75.0)
   
      ds=df[['Identifiant du compteur', 'Nom du compteur',]]
      ds = ds.drop_duplicates(subset=['Identifiant du compteur'])
      ds = ds.reset_index()
      ds["Nb comptage"] = ds['Identifiant du compteur'].apply(lambda x: df[df['Identifiant du compteur']==x]['Comptage horaire'].count())
      ds["Nb zero"] = ds['Identifiant du compteur'].apply(lambda x: df[(df['Identifiant du compteur']==x) & (df['Comptage horaire']==0)]['Comptage horaire'].count())
      valCountMax = max(ds["Nb comptage"])
      ds["Taux d'erreurs"] = round(( (ds["Nb zero"] + valCountMax - ds["Nb comptage"] )/ valCountMax)*100,2)

      st.dataframe(ds.iloc[:,1:])

    # Df en colonnes -----------------------------------------------------------

      lstCmptNom = ds[ds["Taux d'erreurs"]< txErr ]['Nom du compteur'].unique()
      dfCol2 = pd.DataFrame({'Date et heure de comptage': df['Date et heure de comptage'].unique()})
      for nm in lstCmptNom:
        dg = df[df['Nom du compteur']==nm]
        dg = dg[['Date et heure de comptage','Comptage horaire']]
        dfCol2 = dfCol2.merge(dg[['Date et heure de comptage','Comptage horaire']], on ='Date et heure de comptage', how="outer")
        dfCol2 = dfCol2.rename(columns={'Comptage horaire' : nm} )
   
      nbcol = len(dfCol2.columns)-1
      dfCol2 = dfCol2.iloc[:,1:nbcol]
    
      plt.style.use('classic')
      fig, ax = plt.subplots(figsize = (10,10))
      sns.heatmap(dfCol2.corr(), annot = True, ax =ax, cmap = "coolwarm") # annot = 
      st.pyplot(fig)
      sns.reset_orig()
      plt.rcdefaults()

      with st.expander("See explanation"):
          st.markdown(''' 
                      En diminuant le taux d'erreur pris en compte, le nombre de compteurs diminue ce qui augmante la lisibilité du graphique.
                      ''')

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%     
#         Visuelles
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%     

def visuEnsemble():
      df['2022']=df[df['annee_cmpt']=="2022"]["Comptage horaire"]
      df['2023']=df[df['annee_cmpt']=="2023"]["Comptage horaire"]
      st.write("Ensemble des comptages")
      st.line_chart(data =df, y=("2022", "2023"),x='Date du comptage',width=.1)

# 〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️

def visuRepartAnnee():
      fig1, ax1 = plt.subplots(figsize=(10, 3))
      sns.countplot(x = df.annee_cmpt)
      st.pyplot(fig1)

# 〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️

def map1():

    dm = df.groupby(['Nom du compteur','Coordonnées géographiques']).agg({'Comptage horaire':'mean'})
    dm = dm.reset_index()

    dm[['lat','lon']]=dm['Coordonnées géographiques'].str.split(",", expand = True).astype(float)
    dm = dm.drop(['Coordonnées géographiques'], axis=1)
    st.write("Position des compteurs")
    st.map(dm,zoom=11, use_container_width=True)


#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%     
#         spécifiques
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%   

def visuSpe():
      ds=df[['Identifiant du compteur', 'Nom du compteur']]
      ds = ds.drop_duplicates(subset=['Identifiant du compteur'])
      ds = ds.reset_index()
      ds["Nb comptage"] = ds['Identifiant du compteur'].apply(lambda x: df[df['Identifiant du compteur']==x]['Comptage horaire'].count())
      ds["Nb zero"] = ds['Identifiant du compteur'].apply(lambda x: df[(df['Identifiant du compteur']==x) & (df['Comptage horaire']==0)]['Comptage horaire'].count())
      valCountMax = max(ds["Nb comptage"])
      ds["Taux d'erreurs"] = round(( (ds["Nb zero"] + valCountMax - ds["Nb comptage"] )/ valCountMax)*100,2)
     
      ds = ds.drop(['Identifiant du compteur'], axis=1)
      ds['Voie'] = ds['Nom du compteur'].apply(lambda x: " ".join(x.split()[1:-1]))
      col = ds.pop('Voie')
      ds.insert(loc= 1 , column= 'Voie', value= col)

      colA, colB = st.columns([5, 1])
      with colA:
        st.dataframe(ds.iloc[:,1:], height = 250)
      
      with colB: 
        periode = st.radio(
              "Periode",
              ('A date', 'Au mois', 'Au jour',"A l'heure"))

      select = st.multiselect('Sélectionnez les compteurs à afficher', ds['Nom du compteur'].unique())
      dfCol['date'] = dfCol["Date et heure de comptage"].apply(lambda x: x.date)

      for i in select:
          urlImg = df[df["Nom du compteur"] == i]["test_lien_vers_photos_du_site_de_comptage_"].unique()
          x = urlImg[0]
          response = requests.get(x)
          img = Image.open(BytesIO(response.content))
          
          col1, col2 = st.columns([1, 3])
          with col1:
            st.image(img)
          with col2:

            dg = df[df['Nom du compteur'] == i]
            dg = dg[['Date et heure de comptage','Comptage horaire']]
            dx = dft.merge(dg[['Date et heure de comptage','Comptage horaire']], on ='Date et heure de comptage', how="outer")
            dx = dx.fillna(0)

            COLOR = 'white'
            COLORplus= "purple"

            if (periode == 'Au mois'):
                dx['Mois'] = dx['Date et heure de comptage'].apply(lambda x: x.month)
                dx['Annee'] = dx['Date et heure de comptage'].apply(lambda x: x.year)

                dm = dx.groupby(["Mois",'Annee']).agg({'Comptage horaire':'mean'})
                dm = dm.reset_index()
                
                fig, ax =plt.subplots(figsize=(15, 4))
                fig.patch.set_facecolor('black')
                ax.spines[:].set_color(COLOR)
                ax.patch.set_facecolor('black')
                plt.grid(axis = 'y', color='dimgrey')
                sns.barplot(data =dm, x='Mois', y="Comptage horaire", hue='Annee')
                plt.title(i)
                plt.legend(frameon=False);
                st.pyplot(fig)

            if (periode == 'Au jour'):

                dlast = max(dx['Date et heure de comptage'])
                dlast=dlast +pd.DateOffset(days = -7)

                days = ['Lun','Mar','Mer','Jeu','Ven','Sam','Dim']
                dx['Jours'] = dx['Date et heure de comptage'].apply(lambda x: x.weekday())
                dx['Annee'] = dx['Date et heure de comptage'].apply(lambda x: x.year)

                dfnow = dx[dx['Date et heure de comptage']>dlast]
                dfnow = dfnow.groupby(["Jours",'Annee']).agg({'Comptage horaire':'mean'})

                dm = dx.groupby(["Jours",'Annee']).agg({'Comptage horaire':'mean'})
                dm = dm.reset_index()
                
                fig, ax =plt.subplots(figsize=(15, 4))
                fig.patch.set_facecolor('black')
                ax.spines[:].set_color(COLOR)
                ax.patch.set_facecolor('black')
                plt.grid(axis = 'y', color='dimgrey')
                sns.barplot(data =dm, x='Jours', y="Comptage horaire", hue='Annee')
                
                sns.lineplot(data =dfnow, x='Jours', y="Comptage horaire", color= COLORplus, label='7 derniers jours', linewidth = 3)  

                ax.set_xticklabels(days)
                plt.title(i)
                plt.legend(frameon=False);
                st.pyplot(fig)


            if (periode == "A l'heure"):
                dlast = max(dx['Date et heure de comptage'])
                dlast=dlast +pd.DateOffset(days = -1)
                dx['Heures'] = dx['Date et heure de comptage'].apply(lambda x: x.hour)
                dx['Annee'] = dx['Date et heure de comptage'].apply(lambda x: x.year)

                dfnow = dx[dx['Date et heure de comptage']>dlast]

                dm = df.groupby(["Heures",'Annee']).agg({'Comptage horaire':'mean'})
                dm = dm.reset_index()
    
                fig, ax =plt.subplots(figsize=(15, 4))
                fig.patch.set_facecolor('black')
                ax.spines[:].set_color(COLOR)
                ax.patch.set_facecolor('black')
                plt.grid(axis = 'y', color='dimgrey')
                sns.barplot(data =dm, x='Heures', y="Comptage horaire", hue='Annee')
                sns.lineplot(data =dfnow, x='Heures', y="Comptage horaire", color= COLORplus, label= dlast.date(), linewidth = 3)  
                plt.title(i)
                plt.legend(frameon=False);
                st.pyplot(fig)
            
            if (periode == 'A date'):
 
                plt.rcParams['text.color'] = COLOR
                plt.rcParams['axes.labelcolor'] = COLOR
                plt.rcParams['xtick.color'] = COLOR
                plt.rcParams['ytick.color'] = COLOR

                fig, ax =plt.subplots(figsize=(15, 4))
                fig.patch.set_facecolor('black')

                rule = rrulewrapper(YEARLY, bymonthday=1, interval=1) #rrule(DAILY, bymonthday=1, count=5))
                loc = RRuleLocator(rule)
                formatter = DateFormatter('%m/%Y')

                plt.plot_date(dx['Date et heure de comptage'],dx['Comptage horaire'], markersize=1, color='#25A4BD',label = i)
                ax.spines[:].set_color(COLOR)
                ax.xaxis.set_major_locator(loc)
                ax.xaxis.set_major_formatter(formatter)

                ax.patch.set_facecolor('black')
                ax.patch.set_alpha(0.5)

                plt.axhline(y=dx['Comptage horaire'].mean(), color= COLORplus, label='Moyenne', linewidth = 3)    

                plt.grid(axis = 'y', color='dimgrey')

                plt.legend(markerscale=12, framealpha=0, frameon=False);

                st.pyplot(fig)


if __name__=="__main__":
    st.set_page_config(
        page_title = "App. Paris Py Bike",
        page_icon = Image.open("analysis.png"),
        layout = "wide",
        initial_sidebar_state = "expanded",
        menu_items={
          'Get Help': 'https://www.linkedin.com/in/fran%C3%A7ois-gibault/',
          #'Report a bug': "",
          'About': '''
                  # Paris Py Bike  
                  > Application réalisée à partir du projet fil rouge développé en 2022 dans le cadre de la formation Datascientest de Data Analyst par:
                  >> - Yanik Gavet
                  >> - François Gibault
                  >> - Nicolas Vernet
                  '''
          }
        )
    
    init_sidebar()
    ouverture_session() # Compte le nombre d'ouverture de session
    
    st.session_state['counter'] += 1
    if st.session_state['counter']==1:
      st.header("Chargement des données...")
    
    #("data21_extrait.csv")
    url_data = "https://parisdata.opendatasoft.com/api/explore/v2.1/catalog/datasets/comptage-velo-donnees-compteurs/exports/csv?lang=fr&timezone=Europe%2FParis&use_labels=true&delimiter=%3B"          
    #url_data = "Extrait_comptage.csv"
    
    df,dfCol,dft,nbColInit,dxtrait = load_data(url_data)
    # 〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️

    # 〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️    
    if st.session_state['counter']==1:
     st.experimental_rerun()            # on redémarre pour effacer "changement des données"    

    st.sidebar.write("")
    page = st.sidebar.selectbox(
        "Selectionnez une page",
        [            
            
            "Généralités",
            "Positionnement géographique",
            "Statistisques",
            "Correlation",
            "Visual. individuelle"
            
        ]
    )
    
#    data_frame = sns.load_dataset('planets')
    
    COLOR = 'white'

    if page == "Positionnement géographique":
        #visuEnsemble()
        map1()
    elif page == "Statistisques":
        stats()
    elif page == "Correlation":
        correla()
    elif page == "Visual. individuelle":
        visuSpe()
    elif page == "Généralités":
        stats_gene(df)

