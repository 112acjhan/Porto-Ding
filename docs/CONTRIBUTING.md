# Contributors Guidelines

## **Github workflow**
1. **Isolate Work**: Creates a new branch for the specific feature or bug you are working on. For example:
    - 'feature/login-system'
    - 'feature/document_extraction'
    - 'bugfix/header-typo'
    - 'bugfix/function-mismatch'
    - 'docs/add-contributor-guidelines'

2. **Collaborative Review**: Once the work is done, push your branch:
    - command: 'git add file'
    - command: 'git commit -m "Brief description of what you did"'
    - command: 'git push -u origin feature/feature_description'

3. **Pull Request (PR)**: Go to GitHub, select your branch, and open a PR to merge into 'main'.
4. **Delete After Merge**: After the PR is merged, delete the feature branch on GitHub and locally to keep the repo clean.


## **Branch workflow**
1. **Check Current Branch**
Before you start working, always check where you are.
    - command: git branch
The branch with the * next to it is your current location.

2. **Pull Latest Update**
Pull the latest updates before starting any new task.
    - command: git pull origin main

2. **Create and Switch to a New Branch**
Creates the branch and moves you into it immediately. For example:
    - command: git checkout -b feature/document_extraction

3. **Switch Back to Main**
When you need to pull the latest updates or start a new task.
    - command: 
        - git checkout main
        - git pull origin main

4. **Delete a Branch (After Merging)**
Once your PR is merged on GitHub and you've switched back to main, clean up your local machine:
    - command: git branch -d feature/document_extraction
