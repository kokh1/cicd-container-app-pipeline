#this is a front end for the local gitlab registry
###############################################
# THE DELETE BUTTON FUNCTIONALITY DOESN"T WORK YET
#  NEED TO  WIRE TABLE AND DELETE FUNCTIONALITY TOGETHER
# CURRENTLY ONLY WORKS AS A VIEWER
################################################

#BEFORE RUNNIG THE FIRST TIME
#create a venv in the directory where this file exists by running:
#cd /path/to/directory/where/this/files/exists
#python3 -m venv local-registry_fe_venv
#source local-registry_fe_venv/bin/activate
#pip install streamlit requests

#load crendentials (use the gitlab project specific token, not the general access token)
#export GITLAB_TOKEN_1="<your-GITLAB_TOKEN_1-goes-here>"
#OPTIONAL: echo $GITLAB_TOKEN_1

#RUN THE APP  
#cd /path/to/directory/where/this/files/exists
##source local-registry_fe_venv/bin/activate 
#streamlit run local-registry_fe.py

#AFTER RUNNING 
#it will output an url to access it at

#DEACTIVATE VENV
#deactivate

#local-registry_fe.py

import streamlit as st
import requests
import os
import json


#configuration
REGISTRY_BASE = "http://localhost:8930/v2/" #local registry
REGISTRY_CATALOG = REGISTRY_BASE + "_catalog"

GITLAB_API_URL = "http://localhost:8929/api/v4" #only for DELETE
GITLAB_TOKEN_1 = os.getenv("GITLAB_TOKEN_1") #this is the project-speicifc token saved in the .env of the ~/gitlab directory
PROJECT_ID = 2 #project id as shown in gitlab instance

#fetch repositories from registry
#note: this fetches from the registry directly, not the gitlab api
def fetch_repositories():
    try:
        resp = requests.get(REGISTRY_CATALOG)
        resp.raise_for_status()
        data = resp.json()
        return data.get("repositories", [])
    except Exception as e:
        st.error(f"Failed to fetch registry catalog: {e}")
        return []

#repository ID mapping function
def get_registry_repo_map():
    headers = {"PRIVATE-TOKEN": GITLAB_TOKEN_1}
    url = f"{GITLAB_API_URL}/projects/{PROJECT_ID}/registry/repositories"
    try:
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        #map from repo name to numeric ID
        return {repo['path']: repo['id'] for repo in data} #repo['path'] assume registry paths match gitlab's api output
    except Exception as e:
        st.error(f"Failed to fetch registry repository IDs: {e}")
        return {}
    
#fetch tags for a repository
def fetch_tags(repo_name):
    """
    Fetch tags directly from the Docker/OCI registry.
    Returns list of tag names. No size/reated_at is available here.
    """
    url = f"http://localhost:8930/v2/{repo_name}/tags/list"
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()
        return data.get("tags", [])
    except Exception as e:
        st.error(f"Failed to fetch tags for {repo}: {e}")
        return []

#fetch manifest for each tag
def fetch_manifest(repo, tag):
    url = f"{REGISTRY_BASE}{repo}/manifests/{tag}"
    headers = {
        "Accept": (   
            "application/vnd.oci.image.index.v1+json, "
            "application/vnd.docker.distribution.manifest.v2+json, "
            "application/vnd.oci.image.manifest.v1+json"
        )
    }
    try:
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None
    
#helpers
def get_total_size(manifest, repo, tag):
    """Return total size of the real image manifest, not the OCI index"""
    if not manifest:
        return 0
    
    #if this is an OCI index, fetch the actual image manifest
    if manifest.get("mediaType") == "application/vnd.oci.image.index.v1+json":
        manifests = manifest.get("manifests", [])
        if not manifests:
            return 0
        
        real_digest = manifests[0]["digest"]
        real_manifest_url = f"http://localhost:8930/v2/{repo}/manifests/{real_digest}"
        
        try:
            resp = requests.get(
                real_manifest_url,
                headers={"Accept": "application/vnd.oci.image.manifest.v1+json"}
            )
            resp.raise_for_status()
            manifest = resp.json()
        except:
            return 0
    
    #sum the layer sizes
    layers = manifest.get("layers", [])
    return sum(layer.get("size", 0) for layer in layers)

def get_created_at(manifest, repo, tag):
    """Extract created timestamp from config blob if present."""
    if not manifest:
            return "N/A"
    
    #if this is an OCI index, fetch the actual image manifest
    if manifest.get("mediaType") == "application/vnd.oci.image.index.v1+json":
        manifests = manifest.get("manifests", [])
        if not manifests:
            return "N/A"
        
        real_digest = manifests[0]["digest"]
        real_manifest_url = f"http://localhost:8930/v2/{repo}/manifests/{real_digest}"
        
        try:
            resp = requests.get(
                real_manifest_url,
                headers={"Accept": "application/vnd.oci.image.manifest.v1+json"}
            )
            resp.raise_for_status()
            manifest = resp.json()
        except:
            return "N/A"
    
    #Extract creation timestamp from config blob
    config_digest = manifest.get("config", {}).get("digest")
    if config_digest:
        cfg_url = f"http://localhost:8930/v2/{repo}/blobs/{config_digest}"
        try:
            cfg_resp = requests.get(cfg_url)
            cfg_resp.raise_for_status()
            config_json = cfg_resp.json()
            return config_json.get("created", "N/A")
        except:
            return "N/A"
    
    return "N/A"

#streamlit ui
st.title("Local Gitlab Registry Explorer")
st.write(f"Conntected to registry: **{REGISTRY_BASE}**")

#session state for deletion
if "images_to_delete" not in st.session_state:
    st.session_state.images_to_delete = []

repositories = fetch_repositories()
st.write("DEBUG - repositories:", repositories)

#table header
col1, col2, col3, col4 = st.columns([3, 1, 2, 1])
col1.write("**IMAGE**")
col2.write("**SIZE**")
col3.write("**CREATED_AT**")
col4.write("**DELETE**")

#table rows
for repo in repositories:
    tags = fetch_tags(repo)
    for tag in tags:
        manifest = fetch_manifest(repo, tag)

        size_bytes = get_total_size(manifest, repo, tag)
        size_mb = size_bytes / (1024 * 1024) 
        
        created_at = get_created_at(manifest, repo, tag)

        image_key = f"{repo}:{tag}"

        col1, col2, col3, col4 = st.columns([3, 1, 2, 1])

        col1.write(f"{repo}:{tag}")
        col2.write(f"{size_mb:.2f} MB")
        col3.write(created_at)

        selected = col4.checkbox("", key=image_key)

        if selected:
            if image_key not in st.session_state.images_to_delete:
                st.session_state.images_to_delete.append(image_key)
        else:
            if image_key in st.session_state.images_to_delete:
                st.session_state.images_to_delete.remove(image_key)
  
#add delete button
#Requires: GITLAB_TOKEN_1 exported to vennv and PROJECT_ID is correct

# Button to delete selected images
st.write("---")
if st.button("Delete Selected Images"):
        if not st.session_state.images_to_delete:
            st.info("No images selected for deletion.")
        else:
            headers = {"PRIVATE-TOKEN": GITLAB_TOKEN_1}
            for image_key in st.session_state.images_to_delete:
                repo, tag = image_key.split(":")
            
            #Gitlab DELETE endpoint
            delete_url = (
                f"{GITLAB_API_URL}/projects/{PROJECT_ID}/registry/"
                f"repositories/{repo}/tags/{tag}"
            )

            resp = requests.delete(delete_url, headers=headers)

            if resp.status_code in (200, 202, 204):
                st.success(f"Deleted {image_key}")
            else:
                st.error(f"Failed to delete {image_key} ({resp.status_code})")
            
        # Clear selection list and refresh UI
        st.session_state.images_to_delete = []
        st.experimental_rerun()
