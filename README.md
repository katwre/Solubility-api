# Introduction

### Aim: predict solubility of a molecule

The goal of this project is simple: Given a set of molecular descriptors, predict whether a compound will dissolve in water. We provide the model with numeric features that describe the molecule (size, polarity, solvation energy, charge distribution, etc.) and ask: "Will this molecule dissolve, or will it stay stubbornly solid?"

In this version, the focus is on water. Other solvents (ethanol, benzene, acetone) are available in the dataset and can be used later to test whether the model generalizes across solvent environments.

### Concept: what drives solubility?

Solubility is a tug-of-war between how strongly the molecule likes itself (solid–solid) and how strongly it likes the solvent (solid–solvent).

<figure>
<p align="center">
  <img src="images/solubility_intro.png" width="600" />
</p>
<figcaption>
    <strong>Figure.</strong> Conceptual view of solubility prediction. Adapted from <a href="https://www.nature.com/articles/s41467-020-19594-z">Boobier et al., Nature Communications, 2020</a>.
  </figcaption>
</figure>
</br>

In the literature, dissolution - whether a solid will dissolve in a liquid — is described as the balance of three types of interactions:

- Solvent - solvent interactions (top of triangle). How the liquid interacts with itself. For a given solvent (water, ethanol, benzene, acetone), this is constant — the molecules of the solvent don’t change between samples - so there’s nothing for the model to learn here..
- Solute - solute interactions (left). How strongly the solid holds itself together (crystal packing / lattice strength). Compounds with strong intermolecular forces or high melting points tend to be stubborn solids that don't dissolve easily. This part is not modeled in this project
- Solute - solvent interactions (right). How well the solid and liquid can interact — this is where the variation happens and what we model. These interactions are quantified using descriptors such as:
    - ΔG_solv / ΔE_solv (solvation energies): how the molecule interacts with the solvent
    - SASA (solvent-accessible surface area): how much of the molecule is exposed to the solvent
    - Molar volume, molecular weight (MW): size/weight of the molecule
    - Charge/dipole features (partial charges, dipole): whether it has charge or polarity
    - HOMO - LUMO gap terms (simple frontier-orbital interaction proxies): simple electronic properties


# Project Overview

In this project, I make a use of a publicly available [dataset](https://doi.org/10.5281/zenodo.3686212) published by [Boobier et al Nature Communications 2020](https://www.nature.com/articles/s41467-020-19594-z) of organic molecules in different solvents (water, ethanol, benzene, acetone), along with the physicochemical descriptors described in the introduction. 

I experimented with several regression models — Partial Least Squares (baseline linear model), Elastic Net (linear model with feature selection), Random Forest, and XGBoost (gradient-boosted trees) - to predict whether a molecule will dissolve in water based on its descriptors. XGBoost achieved the best performance, which is consistent with the findings in the original publication.

# 🛠️ Tech Stack

**ML | Data Science**

🧠  numpy • pandas • scikit-learn • xgboost  
📊  seaborn • matplotlib  

**Backend**

🌐  Flask (lightweight WSGI web application framework)  
🐴  gunicorn (python WSGI HTTP server for unix)

**MLOps | Deployment**

🐳  Docker  
☁️  AWS Elastic Beanstalk (AWS web app deployment platform)


# Quick start

If the installation steps make your eyes glaze over, but you actually know how solubility works, test a few molecules via API.

The model uses physicochemical descriptors that describe how a molecule interacts with water:

- **Size & Exposure**
  - `MW`: Molecular weight
  - `Volume`: Molecular volume
  - `Area3`: Surface accessible to solvent (SASA)

- **Charge / Polarity**
  - `C_charges`, `O_charges`, `Het_charges`: Partial atomic charges
  - `Asp1`, `Asp2`: How unevenly charge is distributed (polarity)
  - `LsoluHsolv`: Hydrogen bond donor/acceptor balance

- **Electronic / Quantum properties**
  - `LUMO`: Lowest unoccupied molecular orbital energy

- **Energetics (gas vs solvent)**
  - `E0_gas`, `E0_solv`: Ground state energy of the molecule
  - `G_solv`, `HF_G_solv`: Gibbs free energy in solvent
  - `DeltaE0_sol`, `HF_DeltaG_sol`: Energy change when moving into water
  - Lower free energy in water = more soluble


Example prediction request:
```{bash}
curl -s -X POST http://solubility-env.eba-utpwak55.eu-west-1.elasticbeanstalk.com/predict \
  -H "Content-Type: application/json" \
  -d '{
   "HF_E0_solv": -6200.40,
    "Area3": 21000.0,
    "MW": 150.0,
    "HF_E0_gas": -6000.50,
    "E0_gas": -5200.00,
    "Het_charges": -5.20,
    "HF_G_solv": -6100.90,
    "LUMO": -0.20,
    "LsoluHsolv": 1.10,
    "Asp2": 1.80,
    "HF_G_gas": -5900.30,
    "Asp1": 1.60,
    "HF_DeltaE0_sol": 0.025,
    "G_solv": -3800.00,
    "C_charges": -1.5,
    "Volume": 120.0,
    "E0_solv": -5100.80,
    "HF_DeltaG_sol": 0.022,
    "DeltaE0_sol": 0.020,
    "O_charges": -4.30
  }'
```
And the result:
<figure>
<p align="center">
  <img src="images/example_responce_true.gif" width="900" />
</p>
</figure>


# Installation

### Organization of the files 

The repository contains:
```{bash}
Solubility/
├── notebooks/
    └── solubility_water.ipynb # Data preparation, cleaning, EDA, feature importance, model selection process, parameter tuning
├── src/
    ├── train.py # script that trains the model and saves it to a model with pickle
    └── predict.py # script that loads the model and serves it via a web service with flask
├── models/ # saved regression models using pickle
├── images/ # images used for the readme
├── data/ # input datasets
    └── water_set_narrow_descriptors.csv # our input file
├── Dockerfile # instructions to build the docker image
├── Pipfile # library dependencies
├── Pipfile.lock # library dependencies
└── README.md
```

#### Locally

For **local** development and dependency management use pipenv and follow instructions below.

1. Install Pipenv (if not installed)
```{bash}
pip install pipenv
```
2. Create virtual environment & install dependencies. Run this command from the project directory, where the Pipfile and Pipfile.lock are located.
```{bash}
pipenv install
```
3. Activate the environment
```{bash}
pipenv shell
```

4. Run the service using gunicorn:

Install gunicorn (if not installed)
```{bash}
pip install gunicorn
```

5. Run the service:
```{bash}
gunicorn --bind 0.0.0.0:9696 predict:app
```

6. Test your container:
```{bash}
curl -s -X POST http://127.0.0.1:9696/predict \
  -H "Content-Type: application/json" \
  -d '{
    "HF_E0_solv": -6200.40,
    "Area3": 21000.0,
    "MW": 150.0,
    "HF_E0_gas": -6000.50,
    "E0_gas": -5200.00,
    "Het_charges": -5.20,
    "HF_G_solv": -6100.90,
    "LUMO": -0.20,
    "LsoluHsolv": 1.10,
    "Asp2": 1.80,
    "HF_G_gas": -5900.30,
    "Asp1": 1.60,
    "HF_DeltaE0_sol": 0.025,
    "G_solv": -3800.00,
    "C_charges": -1.5,
    "Volume": 120.0,
    "E0_solv": -5100.80,
    "HF_DeltaG_sol": 0.022,
    "DeltaE0_sol": 0.020,
    "O_charges": -4.30
  }'
```
You should get a result such as:
```{bash}
[....]
{"predicted_solubility":-1.4,"soluble":true}
[....]
```

7. To exit the virtual environment:
```{bash}
exit # or deactivate
```

#### Deployment

For the production environment, Docker is used to containerize the application and make **deployment** to e.g. AWS Elastic Beanstalk simple and reproducible. Follow the instructions below to build and run the Docker image.

🐳 Build and run the Docker image (locally).

1. Build the image
```{bash}
docker build -t solubility-api .
```
2. Run the container:
```{bash}
docker run -p 9696:9696 solubility-api
```

🌐 Deploy to AWS Elastic Beanstalk

Requirements: AWS CLI + EB CLI (awsebcli). Install EB CLI (inside Pipenv environment):
```{bash}
pipenv install awsebcli --dev
```

1. Initialize the Elastic Beanstalk application (run once)
```{bash}
eb init -p docker -r eu-west-1 solubility-serving
```

2. Create an environment (run once)
```{bash}
AWS_PROFILE=learn-aws eb create solubility-env --single
```

After deployment, Elastic Beanstalk assigns a public URL, e.g. solubility-env.eba-utpwak55.eu-west-1.elasticbeanstalk.com.


### How to test the API?

Health check:
```{bash}
curl -s http://solubility-env.eba-utpwak55.eu-west-1.elasticbeanstalk.com/health
```

Example prediction request:
```{bash}
curl -s -X POST http://solubility-env.eba-utpwak55.eu-west-1.elasticbeanstalk.com/predict \
  -H "Content-Type: application/json" \
  -d '{
    "HF_E0_solv": -5200.35,
    "Area3": 42500.0,
    "MW": 320.4,
    "HF_E0_gas": -5400.92,
    "E0_gas": -4600.12,
    "Het_charges": -2.15,
    "HF_G_solv": -5100.75,
    "LUMO": -0.08,
    "LsoluHsolv": 0.26,
    "Asp2": 0.67,
    "HF_G_gas": -5200.50,
    "Asp1": 0.52,
    "HF_DeltaE0_sol": 0.015,
    "G_solv": -3100.12,
    "C_charges": -3.6,
    "Volume": 260.8,
    "E0_solv": -4500.55,
    "HF_DeltaG_sol": 0.012,
    "DeltaE0_sol": 0.009,
    "O_charges": -1.75
  }'
```
<figure>
<p align="center">
  <img src="images/example_health_responce_false.gif" width="900" />
</p>
</figure>





