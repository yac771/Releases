# 🚀 OmniScreen - Patch Note Global (Versions 4.0.0 à 6.0.1)
*Le passage vers l'Édition Entreprise (Enterprise Edition)*

## 🌟 Nouvelles Fonctionnalités Majeures

*   **L'Intelligence Artificielle "Omni AI ✨" :** OmniScreen intègre désormais un assistant IA conversationnel connecté au Cloud. Demandez-lui : "Crée-moi un Widget pour le cours du Bitcoin" ou "Crée une horloge avec la météo", et l'IA codera, générera et insérera le widget dynamiquement dans votre bibliothèque !
*   **Le Studio de Design "Canva-like" (Layouts) :** C'est la plus grande avancée d'OmniScreen. Un véritable éditeur graphique drag-and-drop a été intégré. Créez des dispositions personnalisées (1080p, 4K, Portrait), superposez des images, ajoutez du texte riche, intégrez des flux RSS et redimensionnez vos éléments à la souris. En 1 clic, votre composition est envoyée sur vos écrans !
*   **Menu d'Administration Complet (Xibo) :** Le panneau latéral a été intégralement restructuré pour répondre aux normes des grandes entreprises. Des dizaines de nouvelles pages ont été créées : Profils de Paramètres, Groupes d'Écrans, Importation de Polices (.ttf/.otf), Agendas de Planification.
*   **Gestion des Utilisateurs :** Le Super-Admin peut désormais créer, modifier et supprimer des sous-comptes sécurisés avec différents niveaux de permissions.
*   **Paramètres Globaux Massifs (Settings) :** Le menu Configuration propose désormais 6 onglets et plus de 30 options techniques avancées pour piloter votre flotte (Limite d'upload en Mo, Timeout hors-ligne, Paramètres SMTP, Forçage du mode HTTPS, Langue et Fuseau horaire...).
*   **Terminal de Logs en Temps Réel :** Un nouveau panneau de diagnostic permet de visualiser l'utilisation CPU/RAM du serveur et de lire les événements système et réseau en direct pour débugger vos players à distance.

## ⚙️ Améliorations de l'Architecture (Moteur de l'App)

*   **Méga-Base de Données V4 :** Déploiement de 6 nouvelles tables SQL sécurisées pour gérer les Layouts, les Groupes d'écrans, les Campagnes et les configurations globales. Migration silencieuse sans perte de données.
*   **Scraper d'Auto-Update Double-Fallback :** L'Updater graphique a été blindé. S'il est bloqué par les API ou un Antivirus, le logiciel lance un "Chrome fantôme" pour scraper le code HTML brut de la page de téléchargement. Plus aucun crash d'updater.
*   **Processus Détachés d'Installation :** L'UAC de Windows ne fait plus planter les mises à jour. Le système d'installation s'isole de l'application pour garantir que le nouveau `.exe` écrase l'ancien avec 100% de réussite.
*   **Player Ultra-Optimisé :** Injection des attributs C++ `--disable-gpu-compositing` et `--no-sandbox`. Le moteur d'affichage (WebEngine et QMedia) s'ouvre de manière fluide, même sur des ordinateurs ou des Raspberry Pi équipés de très vieilles cartes graphiques.

## 🛠 Corrections de Bugs Majeurs

*   **Sécurisation Absolue des Données :** Le bug critique qui effaçait les mots de passe et les images téléchargées lors d'une mise à jour a été éradiqué. Le coffre-fort de données est désormais verrouillé dans `C:\Users\Public\OmniScreenData`, un répertoire Windows indestructible.
*   **Fix du Réseau Local "Écran Noir" :** Les images envoyées depuis un smartphone via le réseau WiFi s'affichent maintenant correctement sur le Player (correction du bug de concaténation des URL API avec un `/` manquant).
*   **Compatibilité Mobile (Responsive UI) :** Le Tableau de Bord s'affiche désormais parfaitement sur iPhone et Android grâce au développement d'un "Menu Hamburger" coulissant, masquant intelligemment la barre latérale.
