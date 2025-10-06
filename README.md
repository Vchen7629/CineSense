# CineSense
![React](https://img.shields.io/badge/React-19.1.1-orange)
![Python](https://img.shields.io/badge/Python-3.13-purple)
![Database](https://img.shields.io/badge/Database-PostgreSQL-cyan)
![NPM](https://img.shields.io/badge/NPM-23.6.1-blue)
![API](https://img.shields.io/badge/API-TMDB-fcba03)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com)
![Infrastructure](https://img.shields.io/badge/Infrastructure-AWS-yellow)

A Python-based movie recommendation system designed for groups of friends who can never agree on what to watch. 

## How it Works
By analyzing each person’s viewing history, ratings, and preferences, The app can suggests movies that maximize enjoyment for the entire group. The system combines collaborative filtering, content-based recommendations, and personalized weighting to ensure that everyone’s tastes are considered, making movie nights stress-free and fun. It will turns indecision into a shared cinematic experience, blending data analysis, machine learning, and user interactivity into one smart recommendation tool.

## Features
* Ability to input the movies you've watched via Searchbar
* Ability to rate movies to like or dislike movies
* User curated movie recommendations based on the ratings
* Save your user profile via user accounts


## Project Structure

```
CineSense/
├── .github/                         # Github Automation files
│   ├── workflows/                   # Github Actions files for running the CI/CD Pipeline
├── backend/                         # Api backend files
│   ├── user-api                     # FastAPI user application
│        └── app/db/                 # configuration files for connecting to the PostgresSQL Database
|        └── app/middleware/         # files for api middleware logic such as logging, etc
|        └── app/models/             # files for defining how db tables should be structured
|        └── app/routes/             # files for handling api route logic
|        └── app/schemas/            # files for defining how api requests and responses should be structured
|   └── main.py                      # entry point
|        └── tests/integration/      # integration tests for user api
|        └── tests/unit/             # unit tests for user api
├── frontend/                        # React application
│   ├── src/features/Homepage        # Folder containing all the files for the homepage feature
|       └── pages/                   # various pages used by this feature
|       └── components/              # UI components used for this feature
|       └── utils/                   # functions and logic used by this feature
│   ├── src/features/movie-input     # Folder containing all the files for the movie-input feature
|       └── pages/                   # various pages used by this feature
|       └── components/              # UI components used for this feature
|       └── utils/                   # functions and logic used by this feature
│   ├── src/features/navbar          # Folder containing all the files for the navbar feature
|       └── components/              # UI components used for this feature
|       └── utils/                   # functions and logic used by this feature
|   ├── src/features/recommendations # Folder containing all the files for the movie recommendation feature
|       └── pages/                   # various pages used by this feature
|       └── components/              # UI components used for this feature
|       └── utils/                   # functions and logic used by this feature
│   ├── src/features/user            # Folder containing all the files for the user feature
|       └── pages/                   # various pages used by this feature
|       └── components/              # UI components used for this feature
|       └── utils/                   # functions and logic used by this feature
│   ├── shared/assets/               # assets (svg, png, etc) used by more than one feature
|   ├── shared/components/           # Reusable components used by more than one feature
|   ├── shared/styles/               # CSS styling used by more than one feature
|   ├── shared/utils/                # Reusable functions used by more than one feature
│   └── main.tsx                     # entry point
├── Infrastructure/backend           # Terraform files for provisioning backend infra on AWS (Api Gateway, Lambda, VPC, RDS, Sagemaker)
├── Infrastructure/frontend          # Terraform files for provisioning frontend infra on AWS (S3, Cloudfront, Cloudflare)
├── .gitignore                       # Ignoring sensitive and unneeded files
└── 📚 README.md                     # This file
```

## Quick Start

### Local Development

#### Frontend Setup

Note: if you don't have node installed on your pc, you need to install it to use the package manager via: https://nodejs.org/en/download

```bash
cd frontend
npm install
npm run dev
```

#### Backend Setup

This project uses the [UV package manager](https://docs.astral.sh/uv/getting-started/installation/#standalone-installer) to manage dependencies.

Installing UV (Windows)

```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Skip the previous step if you have UV installed

```bash
cd backend
uv sync
uv run fastapi dev
```
    
