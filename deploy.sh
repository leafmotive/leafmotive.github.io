python3 main.py deploy
cd dist
git init
git checkout --orphan gh-pages
git remote add origin git@github.com:leafmotive/leafmotive.github.io.git
git add .
git commit -m "deploy"
git push -f origin gh-pages
