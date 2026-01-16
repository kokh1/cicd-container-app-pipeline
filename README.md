README (WIP)

LICENSE/LEGAL
1. Please review the LICENSE.txt file before proceeding. 

CONTEXT
1. This project was self-directed and iteratively designed and built end-to-end using CI/CD and live cloud infrastrucuture. Components were deployed, debugged and interated against both local envirnoements and live remote cloud resources, performance constraints and costs. 
2. Git history has been cleaned for public release to remove sensitive data and large files. Original iterative commits are retained privately
3. In the CI YAML in particular, some VESTIGIAL LOGIC has been INTENTIONALLY LEFT INTACT so you can trace the project's evolution from: fully local Docker-based workflow using a .env as source of truth, to a local Kubernetes workflow and ultimately to a remote Kubernetes deployment. As part of this progression, configuration was gradually migrated from local .env files into CI/CD variables and the ci.variables file.   
4. Predefined variables and naming assume GitLab as the CI runtime. The project only relies on variables that most CI tools have direct analogs for. Docker is assumed as the container runtime, and named volumes are used for portability and recovery. While not fully runtime-agnostic, this project was designed with agnosticism in mind. 

PROJECT OVERVIEW
1. Purpose/What It Does
+ Template for the building, containerizing, testing and deploying applications using a CI/CD pipeline. 
+ While the template can be adapted to deploy nearly any application, this repository includes an example that deploys a Flask app written in Python, containerized with Docker, and deployed using Kubernetes (via Minikube and via EKS remotely). 
+ Although the pipeline automates most processes, applications can also be tested manually if desired. 
2. Key Features
+ Preconfigured GitLab CE + Runner + local registry setup
+ Custom CI/CD pipeline with build, test, and deploy_local/deploy_remote jobs
+ SBOM generated for built image (per arch)
+ Built image scanned for vulnerabilities (per arch)
+ Vulnerability scan output filtered using epss-check.sh helper script to filer out Criticals below a set EPSS threshold
+ Dynamic image tagginng (SHA + latest)
+ Helper scripts and .env.example files for portability
+ Custom Minikube profile for local deployment with SANs and insecure registries
+ Includes optional helper apps, such as
    + local-registry_fe.py to inspect the local registry
    + changelog.py to automate changelog updates
    + flatten_kubeconfig.sh to flatten the kubeconfig for use in CI
3.  Optional/Helpful Extras
+ Sensitive or system-specific config files (e.g., gitlab-runner.toml) have correspnoding .example files in the repository 
    + .env.example files for project and gitlab directories
+ local-registry_fe.py is uses its own venv (directions to create available inline in file) in the project directory which can be used to help inspect the local registry (as it otherwise has to front end)
+ Architecture diagram illustrating how GitLab, Docker, Minikube, and project directroy interact
**[PLACEHOLDER FOR ARCHITECTURE DIAGRAM]**

TESTING/SECURITY
1. While there is a tests job that does basic integration testing on the app, the majority of testing is integrated into the CI logic. 
    + Vulnerability scanning on the built image is run in CI before push and filtered using epss-check.sh helper script.  
    + Deployment jobs validate registry access, secrets retrieval, cluster connectivity and manifest rendering. 
2. In the CI YAML, there is a commented line in each deploy job suggesting where additional functional testing could be added. 

RELATED REPOSITORIES
+ [Container Configuration Files] (https://github.com/kokh1/project1)
+ [Minikube Setup Guides and Script] (https://github.com/kokh1/minikube-setup)

DEPENDENCIES/REQUIREMENTS
1. Operating System
    + macOS (primary supported environment)
        + Docker runs inside a VM, so networking is more complex
    + Linux (readily adaptable) 
        + simpler networking; Docker runs natively/no VM layer with Docker
    + Windows 
        + possible but more complex (not tested)
2. Required Tools:
    **Host machine**
    + Docker Desktop for macOS
    + Minikube (installed on host)
    + Gitlab CE instance with custom configuration (URLs, registry, runner, secrets)
    + Git
    + Python 3.9+
    + pip (Python package installer; needed for some helper scripts)
    + AWS Secrets Manager (adaptable to use your preferred secrets mananger)
    + AWS CLI v2 (awscli2)
    + kubectl
    + curl
    + AWS Elastic Kubernetes Services (aws eks; for remote deployment workflow)
    + jq (JSON parsing)
    + yq (YAML parsing; used in helper scripts)
    + gettext (for envsubst)
    + grype (vulnerability scanning)
    + syft (SBOM generation)
3. Optional Tools:
    + Homebrew (macOS package manager for installing/managing many helper tools)
    + streamlit (required for local-registry_de.py but runs using its own venv)
    + openssl (not required - see section of HTTPS/TLS below)
    + ***OTHERS?***
+ Note: If you are not going to consistently use brew (e.g. install packages manually by downloading from a web UI), to avoid conflicts, you may want edit your shell PATH ***EXPLAIN THIS MORE??***
+ Note: To avoid version conflicts between globally installed Python and versions of it used for other things/in venvs, you may want to edit your shell PATH ***EXPLAIN THIS MORE??***

GITLAB SETUP
This section explains how to set up the GitLab CE instance, runner and local container registry used in the project. 
Follow these steps carefully. Certain config edits are required for the project to run. 
It is important that you do the following in the order presented. 
1. Directory and Docker Compose Files
+ Create a directory for your Gitlab-related components:
mkdir -p /Users/<user>/docker/gitlab/project1  
cd /Users/<user>/docker/gitlab/project1
+ Once made, create the following Docker Compose files in this directory:
    + docker-compose.yml -> GitLab CE
        + 🐳⚠️ The first time you create this Docker Compose file, Docker auto-creates volumes for config, logs and data. It automatically prepends the name of the directory the Compose file exists in. In the service definition, the volumes block shows the volumes prepended with: gitlab_ but for initial creation you should NOT prepend gitlab_. Likewise, the bottom volumes section has external: true for each volume which you should NOT have for initial creation. The prepending and external: true are necessary only after initial creation if you want to force Docker to use the existing config, data and logs and the path to the project has changed. 
    + docker-compose.runner.yml -> Runner
    + docker.compose.registry.yml -> Local container registry
        + These Compose files will define the configuration for the containers that house each of these components. 
+ Create a dedicated Docker network for these containers to run on:
docker network create gitlab-network
    + Note: All Gitlab components should be on this network to allow communication between Gitlab CE instance, Runner and registry. 
2. Editing gitlab.rb
Only one setting must be updated in GitLab CE's config file:
external_url 'http://gitlab/'
+ This ensures that the GitLab Runner and other internal services can reach the GitLab CE instance over the Docker bridge network (gitlab-network). 
+ Note: Ensure the line is not commented out with a leading # symbol. 
+ From the directory where Gitlab is installed, enter the gitlab container:
docker exec -it gitlab /bin/bash
+ Make the edit (this example uses vi as the text editor):
vi /etc/gitlab/gitlab.rb
/external_url
  + the / lets you search and you follow it with the search term
  + if the search returns multiple entries, use the lowercase n key to move through them (N goes backward)
  + once you find it, enter edit mode:
i
  + this will give you a cursor you can edit with and control with arrow keys
  + edit the line tso it looks like: external_url 'http://gitlab/' with no leading # symbol
  + when done editing in vi, save and exit:
:wq
  + press enter
  + if you make a mistake and don't want to save, exit by typing :q!
+ Important: After editing gitlab.rb, apply changes:
gitlab-ctl reconfigure
  + Note: Do not edit the gitlab.rb while any Gitlab components are running. Stop them to edit, reconfigure and then restart them. 
+ 🚨⚠️ Runnig gitlab-ctl reconfigure after editing external_url in the gitlab.rb can cause NGINX to fail.
    + Running gitlab-ctl reconfigure regenerates the NGINX reconfiguration based on the updated external_url value.
    + Changes to gitlab.rb can cause NGINX to fail if they do not match the port mappings in Docker (or the SSL settings). The highest risk edits are to hostname, protocol or ports. 
    + Prevent NGINX from failing by:
        + ✅ Set external_url correctly BEFORE the first (an ideally only) reconfigure. 
        + ✅ Ensure exposed ports match what Docker exposes. 
        + ✅ Explicitly configure SSL behavior when using HTTPS (not fully tested).    
3. Editing gitlab-runner.toml
The Runner configuration requires:
  + Mounting the host Docker socket
  + Adjusting the URL to match Gitlab CE container (http://gitlab/)
+ After registering the runner, you will find a config.toml file is auto-generated and can be found in the gitlab directory.    
    + It may be in a sub-directory called runner-config of the gitlab directory. 
+ See the .toml.example file for an example of how to modify config.toml safely. 
+ ***MAYBE ADD: screenshot/snippet of edited portions of config.toml***
4. GitLab-specific Secrets
Some configuration for Gitlab CE and the runner relies on secrets. These are only required to start and register GitLab and the runner correctly. Other secrets needed for the project or CI/CD pipeline are covered in the **SECRETS & ENV FILES** section of this document. 
Project secrets and runner registration credentials are split beteen .env files in the /gitlab/project1 directory and as project CI/CD variables in Gitlab.
+ Sensitive files should never be committed - see .env.example for reference/a template
+ Ensure *.env is added to your .gitignore file in any directory that has a .env file
+ Note: variables set as project CI/CD variables in Gitlab will always supercede what is in the .env file (not sure if they override hardcoding)

**Required GitLab secrets:**
  + 4.1 **Runner registration token**
    + Generated in the Gitlab CE UI under the project's **Settings -> CI/CD -> Runners**
    + Needed to register the runner so it can pick up CI/CD jobs
  + 4.2 **GitLab CE instance secrets** (optional / only if using a preconfigured GitLab CE image)
+ The GitLab instance secrets are:  
***FILL THIS IN***
  + Admin password or other credentials required to log in as root
  + Any registry credentials if using the local container registry (default local registry requires none)
  + ⚠️ Note: The .toml file for the runner is auto-generated during registration. The .toml.example is for reference only. 
5. Create the local Docker Network
Before starting any Gitlab-related containers, you must create the shared Docker network they will all use.
+ Make sure you are in the gitlab directory where the Docker Compose file for the gitlab container exists:
cd /path/to/gitlab/project1/directory
+ Create the local Docker network:
docker network create gitlab-network
+ This network allows your Gitlab CE container, GitLab Runner container, and local registry to talk to each other.
+ Your docker-compose files must specify networks: [gitlab-network]
+ You only need to do this once (ever)
6. Access the GitLab CE instance in a web browser
You will need to run some commands from your host terminal to get your GitLab CE instance up and running:
+ From your host terminal, navigate to the gitlab directory:  
cd /path/to/gitlab/project1/directory
+ Start GitLab CE (in the gitlab container):  
docker-compose -f docker-composer.yml up -d
+ Verify it started correctly:  
docker ps
  + the container should show something like running or healthy
  + you can also check the Docker Desktop GUI (but this is not always an accurate indicator)
+ Open the GitLab CE UI in a web browser:  
http://localhost:8929
+ First time login:
    + GitLab will prompt you to create a root user password
    + After setting your password:
        + Username: root
        + Password: YourPassword
    + 😅 if you ever get locked out of your GitLab CE instance, you can reset your root password without editing gitlab.rb:
    cd /path/to/where/gitlab/container/exists
    docker exec -it gitlab gitlab-rake "gitlab:password:reset[root]"
    + you will be prompted to reset the root password
+ You must complete this Gitlab configuration before:
    + creating tokens
    + creating/editing CI/CD variables
    + registering the runner
7. Create the skeleton Project Repository in GitLab CE
CI/CD must have a project to attach to inside GitLab CE, so you must create the project before pushing any code or setting CI/CD variables. 
+ In the GitLab CE UI:
    + Create a new group (optional but recommended)
        + Recommended group name: local-testing
    + Create a new blank project inside that group
        + Recommended project name: local-project-test
+ This project repository in the Gitlab CE is what the CI/CD pipeline attaches to and acts on
+ Once the project is created you'll have access to:
    + Project-level CI/CD variables 
    + Project-level tokens 
    + The registration token for registering the runner

SECRETS & ENV FILES
This section covers all environment variables and secrets required for the project, CI/CD pipeline, Minikube deployment and other helper scripts. 
Variables that are only needed for Gitlab CE are documented in the **GITLAB SETUP -> Gitlab-specific Secrets** subsection. 
1. Env files
There are two main .env files used in this project (these are predominantly VESTIGIAL ARTIFACTS for a local workflow but illustrate project evolution):  
  + 1.1 **Project directory .env**

      + Contains project (application) and deploy-related secrets.
      + Example: .env.example shows required keys and expected format.
      + Typical variables include:
          + REGISTRY_IMAGE_NAME 
          + DOCKER_IMAGE_NAME
          + DOCKER_IMAGE_TAG
      + Credentials needed to push/pull from a public registry 
      + Deploy-related variables for local testing or other resources

  + 1.2 **gitlab/project1 directory .env**
      + Presumed path to this directory: Users/<user>/docker/gitlab/project1 as this set up assumes each of the Gitlab-related containers (gitlab, runner, local registry) are Dockerized 
      + Contains secrets for GitLab Runner, local registry, and GitLab-specific secrets
      + Use the .env.example for the gitlab directory for reference; do not commit real secrets
      + Note:
          + CI_SERVER_URL should match hostname of the Gitlab CE instance (http://gitlab/) inside the local Docker network (gitlab-network). 
          + Suggested: Generate and copy any required tokens from the Gitlab CE GUI into the .env
          + the gitlab-runner container's base image is specified in the Dockerfile.gitlab-runner Compose file located in the gitlab/project1 directory (.example version is provided). It uses the official gitlab/gitlab-runner:alpine image as its base image. 
          + See the ***gitlab*** repo for the example gitab/project1 directory setup at /Users/<user>/docker/gitlab/project1
2. Variables in GitLab CE
+ Purpose: 
    + Variables set in the GitLab project GUI that the CI/CD pipeline can access at runtime
    + They can store secrets, configuration values, or any environment-specific data the pipeline needs.
+ Key Points:
    + Variables can/should be masked or protected in Gitlab if they contain sensitive values (e.g., tokens)
    + Some variables are predefined by GitLab CI/CD (e.g., CI_PROJECT_NAME, CI_COMMIT_REF_NAME)
    + Overlaps with .env files (they will be in the Gitlab GUI and in your .env file). (This is mostly due to iterative migration of variables as the project matured.)
        + If a variable is in both places, the variable as assigned in the GitLab GUI will take precendence
+ Create you Personal Access Token in the Gitlab CE GUI:
    + click on on profile avatar
    + select "Edit Profile" from the drop down menu
    + select "Personal access tokens" from the left side bar
    + follow the prompts
        + your Personal Access Token is for general authentication into Gitlab CE and is not tied to a specific project 
        + you can use it to login in lieu of of your password when possible
        + after creating it, copy it somewhere safe immediately as you will not be able to access it again
+ Get your runner registration token from Gitlab CE:
    + in the Gitlab CE GUI, go to the Admin Area (very bottom of the lefthand dropdown menu)
    + select Runners from the dropdown menu
    + click the three dots in the upper righthand corner to copy your runner registration token        

## Variables **THIS IS NOT PRETTY; FIX THIS**
 + Note: Where Value is n/a, it means that the Value of the variable is auto-assigned by the tool or doesn't exist. 

+ Project-scoped Tokens
   
| Key | Value | Kind | Path | Description | Scopes |
| --- | ----- | ---- | ---- | ----------- | ------ | 
| GITLAB_TOKEN_1 | Your-Gitlab-Token | Access token | Project->Settings->Project access tokens | project-specific access token aka GITLAB_TOKEN_1 | api, read_api, create_runner, manage_runner, k8s_proxy, read_repository, write_repository |

+ CI/CD Variables
   + List of Project-Scoped Variables to be assigned in the GitLab GUI:

| Key | Value | Kind | Path | Type | Environment | Flags | Description | Scopes |
| --- | ----- | ---- | ---- | ---- | ----------- | ----- | ----------- | ------ | 
| AWS_ACCESS_KEY_ID | Your-AWS-AccessKeyID | CI/CD Varaibles | Project->Settings->CI/CD->Variables (scroll down to CI/CD variables table) | Variable(default) | All(defualt) | Masked and hidden | AWS_ACCESS_KEY_ID for Access Key for AWS SecretsManger | n/a |
| AWS_DEFAULT_REGION | Your-AWS-Default-Region | CI/CD Varaibles | Project->Settings->CI/CD->Variables (scroll down to CI/CD variables table) | Variable(default) | All(default) | Visible | AWS_DEFAULT_REGION for AWS SecretsManager | n/a |
| AWS_SECRET_ACCESS_KEY | Your-AWS-SecretAccessKey | CI/CD Varaibles | Project->Settings->CI/CD->Variables (scroll down to CI/CD variables table) | Variable(default) | All(default) | Masked and hidden | n/a | AWS_SECRET_ACCESS_KEY for AWS SecretsManager | n/a |
| BUILD_JOB_IMAGE | image used by teh build job | Project->Settings->CI/CD->Variables (scroll down to CI/CD variables table) | Variable(default) | All(default) | Visible | Expand variable reference | image to use to build the project image (default) | n/a |
| DOCKER_HUB_PAT | Your-DockerHub-PersonalAccessToken | CI/CD Variables | Project->Settings->CI/CD->Variables (scroll down to CI/CD variables table) | Variable(default) | All(default) | Masked | n/a | gitlab ci token aka DOCKER_HUB_PAT (note: this comes from your Docker Hub account settings) | n/a |
| DOCKER_HUB_USERNAME | Your-DockerHub-Username | CI/CD Variables | Project->Settings->CI/CD->Variables (scroll down to CI/CD variables table) | Variable(default) | All(default) | Visible | n/a | this is your docker hub username | n/a |
| KUBECONFIG_SECRET_NAME | minikube-in-docker-local/kubeconfig_flat | CI/CD Variables | Project->Settings->CI/CD->Variables (scroll down to CI/CD variables table) | Variable(default) | All(default) | Visible | n/a | flattened kubeconfig for minikube-in-docker-local cluster | n/a |
| REMOTE_DEPLOY | false(default); true(for deploy_remote) | CI/CD Variables | Project->Settings->CI/CD->Variables (scroll down to CI/CD variables table) | Variable(default) | All(default) | Visible | Expand variable reference | allows deploy_remote job to run if set to true | n/a |
| EPSS_THRESHOLD | .2 | CI/CD Variables | Project->Settings->CI/CD->Variables (scroll down to CI/CD variables table) | Variable(default) | All(default) | Visible | n/a | sets EPSS threshold for epss-check.sh script | n/a |
| GITHUB_USERNAME | Your-Github-Username | CI/CD Variables | Project->Settings->CI/CD->Variables (scroll down to CI/CD variables table) | Variable(default) | All(default) | Visible | n/a | github username | n/a |
| GITHUB_PAT | Your-Github-PersonalAccessToken | CI/CD Variables | Project->Settings->CI/CD->Variables (scroll down to CI/CD variables table) | Variable(default) | All(default) | Masked and hidden | n/a | PAT for github repo DOCKER_PUSH_TARGET pushes to | n/a |

+ Pipeline Trigger Tokens

| Key | Value | Kind | Path | Description |
| --- | ----- | ---- | ---- | ----------- |
| GITLAB_CI_TRIGGER_TOKEN | auto-generated | Pipeline trigger tokens | Project->Settings->CI/CD->Pipeline trigger tokens | token to trigger the pipeline |

+ You may also need to add credentials for whatever repositories you need to access as CI/CD variables. 
+ Strongly Recommended: Configure SSH keys for any remote repos you configure DOCKER_PUSH_TARGET and REMOTE_PULL_TARGET to use. 
  + Some repos have naming conventions for the pushed image. The CI YAML aligns with using Github as the remote when pushing/pulling the built image from a public remote.
    + Note: Just because a remote is public doesn't mean your repo there is publicly accessible. 
    + Note: On Github, pushed container images can be found under the Packages tab.  

3. Non-secret Variables
+ Since the pipeline pulls and pushes from registries dynamically, it uses a several non-secret variables. 
+ Non-secret variables are defined in the ci.variables files and must be manually edited
+ It defines the following variables:
    + LOCAL_DEPLOY=true
    + REMOTE_DEPLOY=false
        + REMOTE_DEPLOY is also set as CI/CD variable and can be overriden by setting it to true there. The CI logic is gated on the how REMOTE_DEPLOY is set. 
    + DOCKER_PUSH_TARGET tells the build what registry to push the built image to
        + options: gitlab-local (the default), gitlab-public, github, docker
            + any public registries must be configured prior to use (SSH deploy key recommended)
    + REMOTE_PULL_TARGET which tells the deploy_remote job which registry to pull the built image from for deployment
        + Options: gitlab-public, github, docker 

RUNNER REGISTRATION
The GitLab Runner is required to execute the pipeline jobs (build, test, deploy_local/deploy_remote). This runner runs in a Docker container on the local Docker network (gitlab-network) and communicates with the local GitLab CE instance. 
1. Navigate to the gitlab directory:
cd /Users/<user>/docker/gitlab/project1
and ensure the docker-compose.runner.yml exists. 
+ This yml file defines a custom GitLab runner container image (gitlab-runner-custom:latest) using Dockerfile.gitlab-runner (which is found in the same directory) extends the official gitlab/gitlab-runner:alpine base image to include:
    + Docker CLI (required to build and push images from pipeline jobs)
    + Bash (to run shell commands inside the contianer)
+ The name of the runner is: gitlab-runner as seen in the docker-compose.runner.yml file.
2. Stop the Runner (if running)
+ Before registration, ensure the runner container is stopped:
docker-compose -f docker-compose.runner.yml down
This prevents conflicts and ensures registration writes the config cleanly. 
3. Register the runner:
    gitlab-runner register --non-interactive --url http://gitlab/ --registration-token <YourRunnerRegistrationToken> --executor docker --docker-image docker:latest --description "gitlab-runner"
    + Most secretes and takens are already defined in the .env files (see SECRETS & ENV FILES section of this document)
    + The URL http://gitlab/ must match the internal Docker network, not localhost because localhost is self-referential from inside a container. 
    + docker:latest is used the default image for jobs that don't specify one. 
+ See the config.toml.example and the docker-compose.runner.yml.example files for referece. Do not use these - they are only examples. **MAYBE SAY THESE ARE IN THE LINKED AND IN gitlab/project1 DIRECTORY REPO**
4. Edit config.toml and persist the runner's configuration
GitLab Runner auto-generates a config.toml file. You must MANUALLY MODIFY the config.toml to be able to mount the host Docker socket as a volume to allow the runner to build and push Docker images. 
+ The runner's config.toml is written to the persistent directory:
./runner-config/config.toml (where . assumes you are in the gitlab/project1 directory)
+ This directory is mounted into the runner container so it can read the pre-registered configuration when the runner is started. The config.toml is the source of truth for the runner's config.  
+ Manually modify the config.toml:
    + Open the config.toml
    + Find the block labeled [[runners]]
        + Edit the url field so it looks like:
        url = "http://gitlab/"

    + Find the block labeled [[runners]] and then the block called [runners.docker]
    + The volumes field should look like: 
        volumes = ["/cache]
    + Edit the volumes field so it looks like:
        volumes = ["/var/run/docker.sock:/var/run/docker/sock", "/cache"]
    
    + In the same block [[runners]] -> [runners.docker] add a field for network_mode above the volumes field that looks like:
        network_mode = "gitlab-network"
    + Save and Exit
+ See the config.toml.example file for reference. Do not use it; it is only an example. 
5. Start the Runner Container
After registration, start the container:
docker-compose -f docker-compose.runner.yml up -d
  + The -d flag starts the container in detached mode so it continues to run until you stop it. 
  + The runner reads the pre-registered config.toml to execute jobs. 
6. Verify Runner
In Gitlab CE (accessible at http://localhost:8929) in a web browser:
  + 6.1 Naviagate to Admin Area->Runners->All Runners
  + 6.2 Confirm gitlab-runner is listed and online
Once online, the runner can execute build, test, and local deploy jobs.

DOCKER DAEMON: INSECURE REGISTRIES
Docker Desktop on macOS uses a VM (virtual machine) layer, so pushing/pulling to a local registry over HTTP (insecure) requires explicit permission. This ensure your GitLab Runner and Minikube can access the local registry without TLS errors. 
1. Before modifying Docker's configuration, stop all running containers:
    + cd /Users/<user>/docker/gitlab
    + docker-compose -f docker-compose.runner.registry.yml down
    + docker-compose -f docker-compose.runner.yml down
    + docker-compose -f docker-composer.yml down
This ensures Docker Desktop can apply the new daemon.json settings without conflicts.
2. Modify daemon.json via Docker Desktop GUI
+ Open Docker Desktop -> Settings -> Docker Engine
+ Update the configuration to include the inseucre registry so it looks like:  **PROBABLY NEED TO REPLACE WITH A GRAPHIC**
{
  "builder": {
    "gc": {
      "defaultKeepStorage": "20GB",
      "enabled": true
    }
  },
  "experimental": false,
  "insecure-registries": [
    "host.docker.internal:8930"
  ]
}
3. Click Apply and Restart. Docker Desktop will restart with the new configuration. 
    + Note: It may be necessary to quit and restart Docker Desktop for the change to take effect. Do this before restarting any containers. 
    + host.docker.internal:8930 points to the local GitLab container registry. You are telling the Docker daemon that it is safe to push/pull from.
    + Using localhost will not work from inside containers as localhost is self-referential inside a container.
4. Verify the Configuration
+ After Docker restarts, run:
docker info | grep -i insecure
+ You should see:
Insecure Registries:
    host.docker.internal:8930
+ This guarantees that:
    + The runner can push/pull to the local registry.
    + Minikube (running inside Docker) can deploy images from the registry. 
5. Restart stopped containers when ready. 
    
MINIKUBE SETUP
Minikube is required to deploy the app from the CI/CD pipeline. In this setup, Minikube runs inside a Docker container on macOS using a custom profile (minikube-in-docker-local) that connects to the host Docker daemon, supports SANs (Subject Alternative Names), insecure registries and port mappings to support local development.  
⚠️ This section is only needed the first time you create the minikube-in-docker-local profile and prepare the environmnet:
1. Install Prerequisites
+ Ensure Docker Desktop is installed and running on macOS. 
    + Note: When running on macOS, Docker uses a VM Layer which can introduce networking complexities.
+ Install Minikube from the official site.
    + Optional: modify .zshrc to avoid conflicts with Homebrew updates (if needed).
2. The Minikube Setup Directory
All detailed instructions and helper scripts live in a separate directory. 
⚠️ You need to be cautious with this directory as it will come to contain files containing secrets. Ensure you do not commit files containing secrets. 
+ From your host terminal, if it doesn't already exist, create and enter the minikube-setup directory:
mkdir -p /Users/<user>/minikube-setup
cd /Users/<user>/minikube-setup
+ Copy or clone files (no files with secrets) from the minikube-setup repository into the minikube-setup directory.
+ Key files: 
    + configure_minikube-in-docker-local.MD
      + step-by-step guide to create the minikube-in-docker-local profile and validate network/registry connectvity
    + before-flattening.MD
      + step-by-step guide to prepare the kubeconfig and PEMs for flattening prior to upload to the Secrets Manager
    + flatten_kubeconfig.sh
      + script that flattens the kubeconfig for upload to the Secrets Manager
    +  ⚠️ DO NOT SKIP THESE GUIDES - they contain critical steps for SANs, insecure registries and pipeline conntectvity. 
3. Quick Verification
+ Once the minikube-setup directory has been created and the steps in configure_minikube-in-docker-local.MD and before-flattening.MD have been completed, you can verify basic functionality:
+ Switch to the newly created minikube-in-docker-local profile:
kubectl config use-context minikube-in-docker-local
kubectl config current-context
+ Verify cluster nodes are reachable:
kubectl get nodes
+ The nodes should appear as Ready, confirming the Minikube profile is correctly configured. 
4. Starting and Using Minikube (Day-to-Day)
Once the minikube-in-docker-local profile has been created, you will typically only need to start, stop or restart it from your host terminal.
Starting:
minikube -p minikube-in-docker-local start
  + the -p flag is for profile and allows to to specify which minikube profile you want to start
  + if you omit the -p flag, Minikube will typically default to the default minikube profile which is not needed
    for this setup, but you should not delete it
kubectl config use-context minikube-in-docker-local
kubectl config current-context
+ Ensure both profile and context are set correctly. The pipeline relies on teh flattened kubeconfig matching this profile. 
+ Minikube may appear to continue running in Docker Desktop after a lid closure or sleep; always run the above commands to very the profile is active. You can also double-check with:
minikube -p minikube-in-docker-local status
Stopping:
minikube -p minikube-in-docker-local stop
+ minikube-in-docker-local uses the host Docker daemon, so images built on the host are immediately available to the cluster. 
+ Only one profile shouldbe active at a time; make sure to set the correct profile before running deploy jobs. 
+ No user pods exist by default; do not attempt to verify registry access via test pods, as pipeline networking is more complex than direct host-to-cluster connectivity. 

FLATTEN KUBECONFIG
The pipeline's deploy jobs rely on a flattened kubeconfig, which consolidates certificates and replaces dynamic values woith single-line base-64 encoded entries. This allows the deploy job to communicate with the Minikube cluster. 
1. Prerequisities
+ Ensure the Minikube profile minikube-in-docker-local is correctly configured and running.
+ The minikube-setup directory at Users/<user>/minikube-setup must exist with the following files (see the ***MINIKUBE SETUP*** section of this README):
    + before-flattening.MD -> step-by-step guide to prepare to flatten the kubeconfig
    + flatten_kubeconfig.sh -> script that flattens kubeconfig for use in CI/CD
2. Verify Required Files
+ PEMs extracted from Minikube:
    + kube-ca.pem -> Certificate Authority
    + kube-client.crt.pem -> Client certificate
    + kube-client.key.pem -> Client key
+ Kubeconfig template:
    + kubeconfig_template.yml -> generated from Minikube profile
        + ⚠️ If if have multiple minikube profiles (you should at least also have the default Minikube profile), this will contain information for all profiles. 
+ Verify existence and permissions:
ls -l kube-*.pem kubeconfig_template.yml
chmod 600 kube-clinet.key.pem
chmod 644 kube-ca.pem kube-client.crt.pem
3. Run flatten-kubeconfig.sh script
From your host terminal:
cd Users/<user>/minikube-setup
bash ./flatten_kubeconfig.sh
+ This script validates PEMs, converts them to single-line base64, patches the kubeconfig template and produces:
/Users/<user>/minikube-setup/kubeconfig_flat.yml
+ ⚠️ The flattened kubeconfig must be uploaded to your Secrets Manafer for use in CI/CD deploy jobs.
+ If the script runs successfully, you should see:
✅ kubeconfig flattened successfully
4. Quick Verification
+ Verify that the minikube-in-docker-local cluster is accessible and the node is ready:
KUBECONFIG=~/minikube-setup/kubeconfig_flat.yml kubectl get nodes
+ Nodes should appear as: Ready. This confirms that kubectl can communicate with the Minikube API server using the flattened kubeconfig. 
+ If errors occur, verify PEMs, base64 encoding and that you are using the minikube-in-docker-local profile. 
5. Notes
+ DO NOT MANUALLY MODIFY the flattened kubeconfig. You will need to regenerate it if changes occur. 
+ Keep the kubeconfig_flat.yml OUT OF VERSION CONTROL. Ensure this file and all *.pem and any other files containing secrets are gtignored (if applicable). 
+ This only needs to be done once unless certificates or kubeconfig change. However, as best practice, it is recommended the rotate your certs. 
6. Upload kubeconfig_flat.yml to Secrets Manager
+ See before-flattening.MD for detailed instructions

PIPELINE WALKTHROUGH
The CI/CD pipeline automates building, testing and deploying the application (in this project, a Flask app is used for demonstration purposes). The pipeline is executred by the GitLab Runner registered on the local Docker network (gitlab-network). 
The main stages are: build, test, deploy_local, deploy_remote, cleanup_deploy_remote. 
1. Build Job
+ Purpose: Containerize the application and tag and push the image to the target registry. 
+ Base Image of the app (not the build job): Custom image based on python:3.9.-slim with:
    + Flask
    + requests
    + python-dotenv
    + pytest
+ Generates SBOM for built image (per arch) and saves as json artifact
+ Scans built image (per arch) for vulnerabilities and runs epss-check.sh helper script to filter out Criticals below set EPSS threshold
+ Registry:
    + Default: local registry at host.docker.internal:8930
    + Optional: punlic registries (Gitlab public, Github, Docker Hub) using CI/CD variables for credentials
+ Image Tagging and Pushing
    + relies on DOCKER_IMAGE_NAME and DOCKER_IMAGE_TAG
    + derives REGISTRY_IMAGE_NAME from DOCKER_PUSH_TARGET
+ Each successful Build job pushes both a versioned SHA and a latest tag
+ Tags and registry information are saved to deploy.env artifact for use in deploy jobs
+ Note: Some registries have specific naming conventions for pushed images. 
2. Test Job
+ Purpose: Run automated integration test on the app 
+ Base Image: Publicly availbe Docker image from Docker Hub
+ Notes: 
    + No build required in this stage
    + Test is in the /tests subdirectory within the project directory
3. deploy_local Job
+ Purpose: Deploy the app to the minikube-in-docker-local cluster
+ Base Image: Publicly available Docker image from Docker Hub
+ Prerequisites:
    + Flattened kubeconfig (kubeconfig_flat.yml) uploaded to Secrets Manager
    + Minikube profile minikube-in-docker-local running and accessible
+ 👀🖥️✋ To view in a web browser on local host, from host terminal run:
minikube -p minikube-in-docker-local service flask-app-template-service --url
  + go to the output IP address in a web browser to access
  + necessary due to Docker VM layer on macOS preventing direct access to localhost from inside a container
+ Steps: 
    + Pull the container image built in the Build job (local or public registry)
    + Use kubectl with the flatttened jubeconfig to deploy manifests from the project directory
    + Apply environment varaible using envsubst from deploy.env artifact to ensure correct image references
4. deploy_remote Job
+ Deploys the same app to a remote Kubernetes cluster
+ Can run as an alternate to the local_deploy job (not at the same time)
+ Requires manually setting the DEPLOY_REMOTE in CI/CD variables explicitly to true
+ Requires manually setting the REMOTE_PULL_TARGET in ci.variables (cannot be gitlab-local)
+ Requires a remote Kubernetes cluster to deploy to. This setup uses AWS 
EKS. 
+ ✋ Must be triggered manually in CI
+ 🚨⚠️ The line in the ci yaml: 
    - kubectl get secrets -n default --kubeconfig="$KUBECONFIG"
    is commented out by default but prints the ImagePullSecret. It is for debug only. NEVER run this line in real deployments to avoid exposing secrets. 
5. cleanup_remote_deploy Job
+ Ends the remote deployment by destroying the remote cluster
    + It is possible to persist the cluster and only delete the deployment/service, but persisting the cluster can incur siginificant costs. 
+ ✋ Must be triggered manually in CI. 
6. Triggering the Pipeline
+ Enter the runner container with the project directory mounted:
docker exec -it gitlab-runner /bin/bash
cd /builds/<my-project>
  + In this case, replace <my-project> with flask-app-template but this would be whatever the project directory is called locally
gitlab push gitlab main
  + gitlab is the dedicated local remote used for this project for local development (but Git should be managed as desired). The setup assumes git is used to push. 
7. Notes
+ Ensure Minikube is running before triggering the pipeline:
minikube -p minikube-in-docker-local status
  + If not, start it:
    minikube -p minikube-in-docker-local start
+ Only one deploy job can run at time (local vs. remote)
+ Ensure deploy.env contains all necessary variables before running the deploy job
+ Ensure DOCKER_PUSH_TARGET and REMOTE_PULL_TARGET are set correctly in ci.variables before running the pipeline
+ The local registry has no credentials; public registries require CI/CD varaible setup
+ Build and deploy rely on dynamic image tagging
    + Do not manually override tags in deploy.env
8. Stop a local deployment
+ Deployments are persisted by default. To stop a persisted deployment from your host terminal, run:  
  + minikube -p minikube-in-docker-local kubectl delete deployment flask-app-template  
  + minikube -p minikube-in-docker-local kubectl delete service flask-app-template-service  
+ Verify:
minikube -p minikube-in-docker-local kubectl get pods
  + Expected: empty
minikube -p minikube-in-docker-local kubectl get services
  + Expected: only the built-in, default Kubernetes API service remains
9. Manually Stop a remote deployment: 
+ eksctl delete cluster \
  --region <AWS_DEFAULT_REGION> \
  --name local-project-test-remote-deploy-poc-$CI__PIPELINE_ID \
  --wait
+ Verify:  
  + aws eks list-clusters --region <AWS_DEFAULT_REGION>
  + aws cloudformation list-stacks \
    --region <AWS_DEFAULT_REGION> \
    --stack-status-filter CREATE_IN_PROGRESS UPDATE_IN_PROGRESS UPDATE_COMPLETE_CLEANUP_IN_PROGRESS DELETE_IN_PROGRESS

HELPER SCRIPTS
This project includes helper scripts to assist with CI/CD preparation, registry management and Minikube interactions. Scripts are intended to be run locally and all include specific instructions for running them as comments within the file. They may rely on their own Python virtual environment and .env variables for configuration. Refer to .env.example files as needed for required keys. 
1. flatten-kubeconfig.sh (REQUIRED)
    + Flattens Minikube kubeconfig for use in CI/CD deploy jobs. 
    + Detailed steps for preparing to run this script are in before-flattening.MD
    + Execute from the minikube-setup directory
2. epss-check.sh
    + Filters the output from vulnerability scan built image (per arch) in build job
    + Filters out CRITICALS below a set threshold
    + EPSS_THRESHOLD set as a CI/CD variable
    + Runs in CI build job container
3. local-registry_fe.py (OPTIONAL)
    + Provides a simple frontend for the local container registry.
    + Used as needed. 
    + Follow instructions in inline comments for creating and activating venv before running. 
    + Run using Streamlit
4. changelog.py (OPTIONAL)
    + Updates a CHANGELOG.md file with latest commit message, commit SHA and timestamp
    + Follow inline instructions to run.
    + Recommended to run in a Python virtual environment. 
    + Intended to be run locally after a successful pipeline run, not in CI.  
    + Inlucded to simulate a production release workflow. 
5. ***MAYBE ADD AUTOMATED PIPELINE TRIGGER SCRIPT run_pipeline.sh HERE AS WELL***

TROUBELSHOOTING/TIPS
***MAYBE ADD TO THIS LATER BUT ALREADY ADDRESSED THROUGHOUT***
+ 🍰 On macOS Docker uses a VM Layer which introduces networking complexity.
    + On macOS, Docker runs inside a lightweight virtual machine. This means containers are not on the host netowrk directly. 
    + You can interact with the containers using docker exec commands or attach to its processes, but there is no direct pathway for tools running inside containers to access services running directly on the host and vice versa. 
    + For example, any communication between containerzed services and the host typically requires port-forwarding or commands to retireve endpoints. (For example, the host cannot automatically discover URLs of containerized services. See the deploy_local workflow for workaround.)
    + Also, some port ranges may be restricted because Docker limits the VM's available IP/port mapping mapping range. 
+ 🚨 Inside a Docker container, localhost refers only to the container itself. To access services running on your host machine or in other Docker containers from within a container, use: host.docker.internal:<port> instead of localhost:<port>
+ 🐳 No DIND (Docker-in-Docker) used in this project, only DOD (Docker-Outside-Docker).
+ 🏃🏻‍♀️ If you change the Runner config, you have to reregister the runner with Gitlab (or whatever CI/CD tool you use)
+ #️⃣ DO NOT put comment lines in the config.toml (for the Runner)
+ 🆗 Your project does NOT need to have the same name in Gitlab as it does on host (as long as your pathing is correct)
+ 😴 Minikube may stop when the host sleeps (including lid closures). 
+ ⚠️ The Docker Desktop UI may not accurately reflect whether all services (including apiserver and kubelet) for the minikube-in-docker-local container are fully up and running. Check all services are running:
minikube -p minikube-in-docker-local status
+ Docker (built) image variables overview:
    + DOCKER_PUSH_TARGET: the canonical registry where images are pushed
        + set in ci.variables
    + REGISTRY_IMAGE_NAME: the full image name including repo (derived from name & tag of the built image).
    + REGISTRY_PULL_TARGET: derived from DOCKER_PUSH_TARGET
        + used as default registry for pulling in remote deployment
    + REMOTE_PULL_TARGET: which registry to pull from for remote deployment
        + set in ci.variables
        + defaults to REGISTRY_PULL_TARGET
        + can be overridden
    + DEPLOY_IMAGE: the final image reference used for deployment, combining REMOTE_PULL_TARGET and REGISTRY_IMAGE_NAME
    + Flow: DOCKER_PUSH_TARGET → REGISTRY_PULL_TARGET → REMOTE_PULL_TARGET → DEPLOY_IMAGE
+ 🧼 Running gitlab-ctl reconfigure (as required after editing the external_url in the gitlab.rb) can overwrite service configurations that rely on it even if you haven't touched them. 
    + This is because Gitlab regenerates service configs from templates. 
    + This means that editing from an otherwise clean template and recofiguring should be smooth, but reconfiguring after editing an already altered template can reset customizations or cause conflicts with any modified settings. 
    + In this project, the risk is highest for NGINX as it relies on the external_url setting, but this can apply to all service configurations in the gitlab.rb
    + Exercise caution by backing up configs, never running reconfigure while a service is active and avoid running gitlab-ctl reconfigure on a modified template. 
+ 🏛️ When deploying remotely, multiarch builds are needed because you cannot assume the architecture of the remote EKS node. The deploy object's architecture is not auto-detected and matched by EKS. 
+ 👷🏼 The Docker BUILDKIT command buildx runs a lot of containers in parallel if you don't explicitly set concurrency limits. 
    + This is why the build job sets PARALLELISM=1 by default. 
    + If you have the resources do increase it, do so cautiously. 
+ 🐚🔁 It is better to write loops and conditionals in CI logic as single line commands due to YAML parsing quirks. 
    + In CI, each command gets interpreted in its own shell, so single line commands ensure the entire loop is executed in the same shell. 
    + Line breaks can break the loop, and multiline blocks can collapse log output making debugging difficult. 
+ 🐳🖥️📝On macOS, you can only edit the daemon.json in the Docker Desktop GUI. 
+ 👻 In CI, variable persistence is very touchy. Each command is executed in its own shell. 
    + Variables exported in a job's before script will persist throughout the job unless overwritten. 
    + Within the job script, exported variables will only persist across lines if everything following the export is in the same multiline block as the export. Multiline blocks suppress log output. 
    + Sourcing variables allows them to persist without use of multiline blocks. Multiline blocks cannot contain comment lines and must have uniform identation. You cannot nest within a multiline block. 
+ ⛔️📂 In CI, avoid redirecting standard error using 2>/dev/null if using minimal container images to run jobs in as /dev/null is not guaranteed to exist. 
+ ☁️ AWS CLI flags are not consistent across services. For example: some commands take --filter and others take --filters. Recommended: if you plan to add AWS CLI commands, especially in CI jobs, verify the commands locally first. 
+ ***ANYTHING ELSE***

TLS/HTTPS
The pipeline uses HTTP only; however, it is designed to support TLS for the remote deployment using certificates stored in Secrets Manager and referenced in the Kubernetes manifests. TLS was omitted to avoid incurring costs associated with secrets storage. 
To implement TLS, the intended workflow involves: adding an ingress definition to the remote deploy Kubernetes manifest, generating certificates locally with Openssl (or obtained through a trusted CA), flattening (and decrypting locally if needed), uploading them to Secrets Manager and extracting them in CI. Decrypting in CI is not recommended as it requires introducing additional dependencies into the job container. 

AWS USAGE
This implementation relies on the AWS CLI (awscli2), AWS Secrets Manager and AWS Elastic Kubernetes Services (EKS). This assumes:
+ You have an AWS account. 
+ Configuration of at least one IAM user with sufficient permissions to run these services. 
+ Local installation EKS (used as a backup workflow for remote resource teardown). 
+ Required AWS credentials are stored as CI/CD variables. 
+ The flattened kubeconfig must be uploaded to Secrets Manager before deploying using Kubernetes (local or remote deploy jobs); it is not required for fully local testing. 
+ to implement TLS, the TLS certificate and key would need to be flattened locally and uploaded to secrets manager for the remote workflow. 
+ The CI logic could be modified to use runtimes of your choosing. 

CONTRIBUTING

See LICENSE.txt for usage restrictions. This repository is for personal or educational purposes only; no external contributions are permitted.

REFERENCES/FURTHER READING
+ https://docs.gitlab.com
+ https://docs.docker.com
+ https://kubernetes.io/docs/home/
+ https://minikube.sigs.k8s.io/docs/
+ https://docs.streamlit.io/
+ https://www.python.org/doc/
+ https://docs.aws.amazon.com/secretsmanager/
+ https://docs.aws.amazon.com/eks/
+ https://curl.se/docs/
+ https://docs.streamlit.io/
+ ***OTHERS?***

OTHER WEIRDNESSES TO BE AWARE OF

#The project is desgined so that the local directory/directories are the source of truth, differing from most production CI/CD pipelines. This introduces siginficant complexity and the project can be simplified by making the CI/CD repo authoritative instead. 
#I have done my best to write all aspects of this project in an inclusive manner that provides a level of transpency and guidance that makes it accessible and understandable to all interested audiences.  
#In a worst case scenario and something crashes with a remote deployment live, delete the cluster manually in the AWS Console (or whatever hosts your cluster). However, be aware that deleting the cluster, does not guarantee that all provisioned resources have been deleted. Recomended: manually run the commands in the cleanup_remote_deploy job from host. (This assumes your local awscli user has permissions for this EKS cluster and anything it provisions.) 
