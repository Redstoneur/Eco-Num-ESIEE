# Utilisez une image de Node.js pour l'environnement de développement
FROM node:22-alpine

# installe un simple serveur http pour servir un contenu statique
RUN npm install -g http-server

# Définissez le répertoire de travail dans le conteneur
WORKDIR /app

# Copiez le package.json et package-lock.json dans le conteneur
COPY package*.json ./

# Installez les dépendances
RUN npm install

# Copiez le reste de l'application dans le conteneur
COPY . .

# Exposez le port 3000 que Vue utilise par défaut
EXPOSE 3000

# construit l'app pour la production en la minifiant
RUN npm run build

# Démarrez l'application
CMD ["http-server", "dist", "-p", "3000"]
