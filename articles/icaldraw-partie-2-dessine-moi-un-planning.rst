=============================================
IcalDraw (Partie 2) : Dessine moi un planning
=============================================
--------------------------------------------------------
C'est l'heure de faire des traits :: svg,python,ical,fac
--------------------------------------------------------

    Pensez à lire la `première partie`_

Résumé de l'épisode précédent
=============================

Au cours de la première partie, nous avons écrit deux outils nous permettant respectivement de :

- récupérer une liste d'évènements Ical à partir d'une URL ou d'un fichier
- dessiner des choses dans un fichier SVG

Nous allons repartir de cette base et remplir les deux derniers objectifs fixés :

- écrire le programme lui même permettant la génération des images
- écrire un script l'utilisant

Pour ceux qui n'auraient pas suivi, on cherche à obtenir ça :

.. image:: /static/images/icaldraw/exemple.png
    :width: 800px
    :align: center

Pour commencer, essayez d'avoir une arborescence comme celle-ci ::

    .
    ├── __init__.py
    ├── fetcher.py
    ├── icaldraw.py
    └── svgutils.py

``__init__.py`` contient une ligne blanche, ``fetcher.py`` la classe ``IcalFetcher`` et ce qui s'y rapporte,
``svgutils.py`` la classe ``SVGwriter`` et enfin, nous alons travailler dans ``icaldraw.py``.

Découpage des méthodes
======================

Voilà comment seront réparties les fonctionnalités de la classe ``IcalDraw`` :

- méthodes spéciales :

  - constructeur ``__init__()`` : initialisation des variables objet, instanciation de ``IcalFetcher`` et récupération
    d'un itérateur sur la liste d'évènements, instanciation de ``SVGwriter``.

- méthodes publiques :

  - ``draw()`` : lance la création de l'image
  - ``save()`` : raccourci pour sauver l'image

- méthodes privées :

  - ``_header()`` : ajout de l'entête du planning (*"Semaine du DD/MM"*)
  - ``_grid()`` : dessin de la grille horaire grise en fond, ajout des numéros des jours
  - ``_place_events()`` : utilisation de la liste d'évènements pour les dessiner sur la grille, le gros du boulot se fera
    ici

On va les écrire dans l'ordre où elles sont notées ici.

IcalDraw
========

Imports and boilerplate
-----------------------

Voilà la base de la base :

.. sourcecode:: python

    from fetcher import IcalFetcher
    from svgutils import SVGwriter

    class IcalDraw:
        # code....

Constructeur
------------

Le code du constructeur se comprend tout seul (comme celui des méthodes publiques, vous verrez) :

.. sourcecode:: python

    def __init__(self, url=None, file=None, utc_offset=1, stroke_color="rgb(5%, 32%, 65%)"):
        self.url = url # url dans laquelle lire les données ICAL...
        self.file = file # ... ou fichier dans lequel lire les données ICAL
        self.utc_offset = utc_offset # pour des heures correctes
        self.stroke_color = stroke_color # couleur générale

        # space to be left as a header
        self.blank_header = 45

        # récupération des évènements
        self.cal = IcalFetcher()
        # si une url ET un fichier sont fournis, l'URL prime.
        if self.url: self.cal.from_url(self.url)
        elif self.file: self.cal.from_file(self.file)
        else: raise ValueError("Give me a source !")

        self.cal.get_events()

        # initialisation de l'image
        self.img = SVGwriter(1360, 430)

Pour ce qui est de la dernière ligne et ses valeurs précalculées (`An Human did this...`_), voilà l'explication.

On va afficher 7 jours, et un intervale horaire allant de 8h à 19h (soit 11h).

Pour la largeur (1360 ici) : je compte 120 par heure à quoi j'ajoute 20 de marge de chaque côté
soit :

.. math::

    w = 120*11 + 2*20 = 1320 + 40 = 1360

Pour la hauteur maintenant, je commence avec le ``blank_header`` puis 30 de marge et enfin 50 par jour :

.. math::

    h = 45 + 30 + 50*7 = 430

Une meilleure solution serait de parcourir une première fois la liste pour savoir sur combien de jours se répartissent
les évènements et d'utiliser ce nombre. On pourrait aussi rechercher à quelle heure commence l'évènement ayant lieu le
plus tôt et à quelle heure se termine celui qui se finit le plus tard pour savoir combien d'heures afficher.

Pour une autre version peut être....

Methode publique : draw()
-------------------------

Celle-ci se contente d'appeler les méthodes privées :

.. sourcecode:: python

    def draw(self):
        self._grid()
        self._header()
        self._place_events()

L'ordre d'appel a une importance : les derniers éléments ajoutés apparaissent au dessus des premiers sur l'image.

Méthode publique : save()
-------------------------

Je n'explique pas là.

.. sourcecode:: python

    def save(self,filename):
        self.img.save(filename)

Méthode privée : _header()
--------------------------

On ajoute un texte dans le ``blank_header`` (centré au mileu du ``blank_header`` horizontalement et aux deux tiers
verticalement). Comme texte on met "Semaine du DD/MM" avec DD le jour du premier évènement et MM son mois.

.. sourcecode:: python

    def _header(self):

        self.img.add_text(
            "Semaine du {0}/{1}".format(self.cal.events[0].dtstart.day,self.cal.events[0].dtstart.month),
            self.img.width/2,
            self.blank_header*2/3,
            style="text-anchor: middle; font-size: 30; alignment-baseline: middle; letter-spacing: 2pt; stroke: {};".format(self.stroke_color)
        )

Méthode privée : _grid()
------------------------

.. sourcecode:: python

    def _grid(self):
        """ Draw a hours&days grid """

        style = "stroke: black; stroke-opacity: 0.4;"

        # vertical
        for n in xrange(12): # [0 .. 11]
            if (n+8) in [8,12,14,18]:
                self.img.add_line(
                    20+n*120,
                    self.blank_header+10,
                    20+n*120,
                    self.img.height-10,
                    style=style+"stroke-width: 3;"
                )
            else:
                self.img.add_line(
                    20+n*120,
                    self.blank_header+10,
                    20+n*120,
                    self.img.height-10,
                    style=style
                )

        # horizontal
        for n in xrange(7): # [0 .. 6]
            self.img.add_line(
                10,
                self.blank_header+30+n*50,
                self.img.width-10,
                self.blank_header+30+n*50,
                style=style
            )

            if n == 0: str = "n"
            else: str = "n+{}"

            self.img.add_text(
                str.format(n),
                self.img.width-50,
                self.blank_header+20+n*50,
                style="text-anchor: middle; letter-spacing: 2pt;"+style
            )

Notez l'utilisation de ``stroke-opacity`` pour atténuer le noir des lignes et le fait que les marges soient plus faibles
que celle décrites au dessus. Ce second point permet de faire en sorte que les lignes guides dépassent un peu.

Enfin, plutot que m'embèter à remettre les dates pour chaque ligne, j'ai choisi d'ajouter un indice de *n* à *n+6* [#]_ à
droite au bout des lignes pour chaque jour (deuxième partie de la deuxième boucle).

Méthode privée : _place_events()
--------------------------------

Là, ça se corse, d'abord la méthode est plus longue et de deux, c'est elle qui fait tout le boulot.
Le début est fortement inspiré de l'article proposant un passage de l'Ical au PDF, la suite n'est que dessin :

.. sourcecode:: python

    def _place_events(self):
        """ Places events on timelines """

        # on retient le jour précédent pour savoir s'il
        # faut changer de ligne
        previous_d = self.cal.events[0].dtstart.day
        # nb_days nous dit sur quelle ligne se placer
        nb_days = 0

        # on itère sur les évènements
        for e in self.cal:

            # test pour changement de ligne
            if previous_d != e.dtstart.day:

                # on calcule combien de jours séparent l'évènement
                # précédent de celui en cours (pour les problèmes de
                # ligne à laisser vide, toussa....)
                nb_days += e.dtstart.day - previous_d
                previous_d = e.dtstart.day

            # on a dit qu'on affichait que pour 7 jours (de toute façon, on a que 7 lignes)
            if nb_days < 7:

                # on calcule les abscisses de début et de fin
                # start_px = padding +
                #   (heure début + correction utc - début de l'échelle de temps)* longueur choisie +
                #   (nombre de "5minutes" après l'heure de début) * longueur choisie pour 5minutes
                # idem pour la fin
                # le milieu (middle_px) correspond au début + la moitié de la durée de l'évènement
                #   on l'utilise pour centrer le texte
                # la hauteur correspond au blank_header + la marge + nb_days*50 et elle permet
                #   de se positionner sur une ligne
                start_px = 20+(e.dtstart.hour+self.utc_offset-8)*120+(e.dtstart.minute/5)*10
                end_px = 20+(e.dtend.hour+self.utc_offset-8)*120+(e.dtend.minute/5)*10
                middle_px = start_px + (end_px-start_px)/2
                height = self.blank_header+30+50*nb_days

                # on ajoute la ligne entre start_px et end_px
                self.img.add_line(
                    start_px,
                    height,
                    end_px,
                    height,
                    style = "stroke: {}; stroke-width: 10;".format(self.stroke_color)
                )

                # on ajoute par-dessus les cercles de début et de fin
                self.img.add_circle(
                    start_px,
                    height,
                    10,
                    style = "fill: {};".format(self.stroke_color)
                )
                self.img.add_circle(
                    end_px,
                    height,
                    10,
                    style = "fill: {};".format(self.stroke_color)
                )

                # au dessus de la ligne, on met l'intitulé du cours
                self.img.add_text(
                    e.summary,
                    middle_px,
                    height-15,
                    style="text-anchor: middle; font-size: 0.8em; letter-spacing: 2pt; stroke: {};".format(self.stroke_color)
                )
                # et en dessous la salle
                self.img.add_text(
                    e.location,
                    middle_px,
                    height+25,
                    style="text-anchor: middle; font-size: 0.8em; letter-spacing: 2pt; stroke: {};".format(self.stroke_color)
                )

Et voilà !

En dehors du bidouillage de coordonnées, ça va :) D'ailleurs, en voyant le découpage par 5 minutes, vous comprennez
pourquoi j'ai pris 120 et non 100 pour 1 heure : 120 ça se divise facilement par 12 :).

Voilà donc pour ce module qui était fatiguant par ses problèmes de coordonnées (j'ai horreur de ça).

Reste maintenant à écrire le script qui l'utilise :

Script final
============

Là, rien de plus simple, on va refaire le planning de l'exemple (donc à partir d'un fichier Ical).

Le fichier est `téléchargeable ici`_

Et pour le code, rien de plus simple :

.. sourcecode:: python

    from icaldraw import IcalDraw

    def main():

        FILE = "exemple.ics"


        id = IcalDraw(file=FILE)
        id.draw()
        id.save("exemple.svg")

    if __name__=='__main__':
        main()

Et voilà !

Le tout avec style !
====================

Vous aurez noté que je n'ai pas parlé une seule fois des arguments ``style`` qui sont pourtant partout.

Je n'ai pas envie de détailler l'ensemble des propriétés de style du SVG mais sachez qu'elles sont nombreuse.
Pour tout ce qui touche aux spécification de ce format assez puissant (oui, oui, on peut même faire des jeux en JS+SVG,
c'est dire.), je vous renvoie à *SVG Essentials* d'O'Reilly  [#]_.

Conclusion
==========

Bon, soyons francs, je suis plutot satisfait du résultat. Toutefois, comme je l'ai déjà dit dans d'autres articles,
cette API d'export n'est pas faite pour être utilisée en dehors d'un agenda, et ça se sent (dans les lieux associés par
exemple, il y a plein de données inutiles). On arrive toujours au même point : une API plus générale ne serait pas un
mal (ou une meilleure conformité avec l'Ical, qui ne recommande pas d'écrire un roman dans le champ LOCATION)

Finalement, je suis surtout content d'une chose : le module pour le SVG est assez efficace et suffisant pour une majorité des
utilisation que j'en ferais.

D'ailleurs, il n'est pas impossible qu'il deviennent un module à part entière...

.. [#] Quoi ? Moi, faire des maths ? Non. C'est faux.
.. [#] ISBN-13 : 978-0596002237 ou `en ligne`_

.. _première partie: /writing/icaldraw-partie-1-quelques-outils/
.. _An Human did this...: http://www.youtube.com/watch?v=Gsz4EkGQSHw
.. _téléchargeable ici: /static/images/icaldraw/exemple.ics
.. _en ligne: http://commons.oreilly.com/wiki/index.php/SVG_Essentials
