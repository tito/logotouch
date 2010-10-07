Logotouch
=========

Logotouch est une application permettant de manipuler le sens des mots avec la gestuelle du multitouch, et de créer des phrases.

Description des interactions
----------------------------

Plusieurs interactions sont possibles en fonction du nombre de doigts sur le mot.

1 doigt
~~~~~~~

* On peut déplacer le mot avec un doigt.
* Si le mot est secoué, il est remplacé par un synonyme. (Regarder -> Explorer -> S'attarder)

2 doigts
~~~~~~~~

* La rotation du mot permet d'obtenir son contraire. (Noir -> Blanc)
* L'agrandissement ou le rétrécicement du mot permet de renforcer ou diminuer la valeur ou le sens du mot. (Petit -> Moyen -> Grand).

3 doigts
~~~~~~~~

Dans les interactions à 3 doigts, les 2 premiers doigts ne sont pas pris en compte, seul le mouvement du troisième permet l'interaction.

* Bouger le troisième doigt de gauche à droite permet de changer le temps du mot, (passé, présent puis futur).
* Bouger le troisième doigt de haut en bas permet de changer la personne (Je, tu, il, nous, vous, ils)


Installation
------------

Il faut installer les composants suivants:

* pymt: http://pymt.eu/wiki/DevGuide/Installation
* pymunk: easy_install pymunk

Puis, pour démarrer le programme, exécuter:

  python start.py
