# Repo structure fix (why the deployed app failed)
The GitHub repo must have these files at its ROOT: app.py, requirements.txt, packages.txt, scrapers/, data/.
If you see a `data-collection-project/` folder at the top of the repo, run (replace the URL):

    cd ~/Desktop/data-collection-project
    rm -rf ~/Desktop/.git
    echo ".venv/" >> .gitignore
    git init && git add . && git commit -m "Data collection project"
    git branch -M main
    git remote add origin https://github.com/Richdoll/YOUR-REPO-NAME.git
    git push -u origin main --force

Then in Streamlit Cloud: delete the app, redeploy with Main file path = app.py, add the secrets.
